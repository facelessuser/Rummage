"""
Custom App.

https://gist.github.com/facelessuser/5750404

Licensed under MIT
Copyright (c) 2013 - 2015 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
from __future__ import unicode_literals
import codecs
import json
import os
import sys
from . import simplelog
import time
import wx
import wx.lib.newevent
from .. import util
try:
    import thread
except ImportError:
    import _thread as thread


if util.platform() == "windows":
    import ctypes
    GENERIC_READ = 0x80000000
    GENERIC_WRITE = 0x40000000
    OPEN_EXISTING = 0x3
    PIPE_ACCESS_DUPLEX = 0x3
    PIPE_TYPE_MESSAGE = 0x4
    PIPE_WAIT = 0x0

PipeEvent, EVT_PIPE_ARGS = wx.lib.newevent.NewEvent()

log = None
last_level = simplelog.ERROR
DEBUG_MODE = False
DEBUG_CONSOLE = False


class GuiLog(wx.PyOnDemandOutputWindow):
    """GUI logging."""

    def __init__(self, title="Debug Console"):
        """Init the PyOnDemandOutputWindow object."""

        # wx.PyOnDemandOutputWindow is old class style
        # Cannot use super with old class styles
        wx.PyOnDemandOutputWindow.__init__(self, title)

    def CreateOutputWindow(self, st):  # noqa
        """Create the logging console."""

        self.frame = wx.Frame(self.parent, -1, self.title, self.pos, self.size, style=wx.DEFAULT_FRAME_STYLE)
        self.text = wx.TextCtrl(self.frame, -1, "", style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH)
        self.text.AppendText(st)
        self.frame.Show(True)
        self.frame.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

        # Create debug keybinding to open debug console
        debugid = wx.NewId()
        self.frame.Bind(wx.EVT_MENU, self.debug_close, id=debugid)
        mod = wx.ACCEL_CMD if util.platform() == "osx" else wx.ACCEL_CTRL
        accel_tbl = wx.AcceleratorTable(
            [(mod, ord('`'), debugid)]
        )
        self.frame.SetAcceleratorTable(accel_tbl)

    def debug_close(self, event):
        """Close debug frame."""

        self.frame.Close()

    def write(self, text, echo=True):
        """Write to log, and if console is open, echo to it as well."""

        if self.frame is None:
            if not wx.IsMainThread():
                if echo:
                    wx.CallAfter(gui_log, text)
                if get_debug_console():
                    wx.CallAfter(self.CreateOutputWindow, text)
            else:
                if echo:
                    gui_log(text)
                if get_debug_console():
                    self.CreateOutputWindow(text)
        else:
            if not wx.IsMainThread():
                if echo:
                    wx.CallAfter(gui_log, text)
                if get_debug_console():
                    wx.CallAfter(self.text.AppendText, text)
            else:
                if echo:
                    gui_log(text)
                if get_debug_console():
                    self.text.AppendText(text)

    def OnCloseWindow(self, event):  # noqa
        """Close logging console."""

        if self.frame is not None:
            self.frame.Destroy()
        self.frame = None
        self.text = None
        self.parent = None
        if get_debug_console():
            set_debug_console(False)
            log.set_echo(False)
            debug("**Debug Console Closed**\n")


class CustomApp(wx.App):
    """Custom app that adds a number of features."""

    outputWindowClass = GuiLog

    def __init__(self, *args, **kwargs):
        """
        Init the custom app.

        Provide two new inputs:
            single_instance_name: this creates an instance id with the name given
                                  this will allow you to check if this is the only
                                  instance currently open with the same name.
            callback: A callback you can do if instance checks out
        """

        self.instance = None
        self.custom_init(*args, **kwargs)
        if "single_instance_name" in kwargs:
            del kwargs["single_instance_name"]
        if "callback" in kwargs:
            del kwargs["callback"]
        wx.App.__init__(self, *args, **kwargs)

    def custom_init(self, *args, **kwargs):
        """Parse for new inputs and store them because they must be removed."""

        self.single_instance = None
        self.init_callback = None
        instance_name = kwargs.get("single_instance_name", None)
        callback = kwargs.get("callback", None)
        if instance_name is not None and isinstance(instance_name, util.string_type):
            self.single_instance = instance_name
        if callback is not None and hasattr(callback, '__call__'):
            self.init_callback = callback

    def ensure_single_instance(self, name):
        """Check to see if this is the only instance."""

        self.name = "%s-%s" % (self.single_instance, wx.GetUserId())
        self.instance = wx.SingleInstanceChecker(self.name)
        if self.instance.IsAnotherRunning():
            # wx.MessageBox("Only one instance allowed!", "ERROR", wx.OK | wx.ICON_ERROR)
            return False
        return True

    def is_instance_okay(self):
        """Return whether this is the only instance."""

        return self.instance_okay

    def OnInit(self):  # noqa
        """
        Execute callback if instance is okay.

        Store instance check variable.
        """

        self.locale = wx.Locale(wx.LANGUAGE_DEFAULT)

        self.instance_okay = True
        if self.single_instance is not None:
            if not self.ensure_single_instance(self.single_instance):
                self.instance_okay = False
        if self.init_callback is not None and self.instance_okay:
            self.init_callback()
        return True

    def OnExit(self):  # noqa
        """Cleanup instance check."""

        if self.instance is not None:
            del self.instance
        return 0


class ArgPipeThread(object):
    """Argument pipe thread for receiving arguments from another instance."""

    def __init__(self, app, pipe_name):
        """Init pipe thread variables."""

        self.app = app
        self.pipe_name = pipe_name

    def Start(self):  # noqa
        """Start listening to the pipe."""

        self.check_pipe = True
        self.running = True
        thread.start_new_thread(self.Run, ())

    def Stop(self):  # noqa
        """
        Stop listening to the pipe.

        Send a new line to kick the listener out from waiting.
        """

        self.check_pipe = False
        if util.platform() == "windows":
            file_handle = ctypes.windll.kernel32.CreateFileW(
                self.pipe_name,
                GENERIC_READ | GENERIC_WRITE,
                0, None,
                OPEN_EXISTING,
                0, None
            )
            data = '\n'
            bytes_written = ctypes.c_ulong(0)
            ctypes.windll.kernel32.WriteFile(
                file_handle, ctypes.c_wchar_p(data), len(data), ctypes.byref(bytes_written), None
            )
            ctypes.windll.kernel32.CloseHandle(file_handle)
        else:
            # It's okay if the pipe is broken, our goal is just to break the
            # wait loop for recieving pipe data.
            try:
                with codecs.open(self.pipe_name, "w", encoding="utf-8") as pipeout:
                    try:
                        pipeout.write('\n')
                    except IOError:
                        pass
            except util.CommonBrokenPipeError:
                pass

    def IsRunning(self):  # noqa
        """Return if the thread is still busy."""

        return self.running

    def Run(self):  # noqa
        """The actual thread listening loop."""

        if util.platform() == "windows":
            data = ""
            p = ctypes.windll.kernel32.CreateNamedPipeW(
                self.pipe_name,
                PIPE_ACCESS_DUPLEX,
                PIPE_TYPE_MESSAGE | PIPE_WAIT,
                1, 65536, 65536, 300, None
            )
            while self.check_pipe:
                ctypes.windll.kernel32.ConnectNamedPipe(p, None)
                result = ctypes.create_unicode_buffer(4096)
                bytes_read = ctypes.c_ulong(0)
                success = ctypes.windll.kernel32.ReadFile(p, result, 4096, ctypes.byref(bytes_read), None)
                if success:
                    data += result.value.replace("\r", "")
                    if len(data) and data[-1] == "\n":
                        lines = data.rstrip("\n").split("\n")
                        try:
                            args = json.loads(lines[-1])
                        except Exception:
                            args = []
                        evt = PipeEvent(data=args)
                        wx.PostEvent(self.app, evt)
                        data = ""
                ctypes.windll.kernel32.DisconnectNamedPipe(p)
                time.sleep(0.2)
        else:
            if os.path.exists(self.pipe_name):
                os.unlink(self.pipe_name)
            if not os.path.exists(self.pipe_name):
                os.mkfifo(self.pipe_name)

            while self.check_pipe:
                with codecs.open(self.pipe_name, "r", 'utf-8') as pipein:
                    while self.check_pipe:
                        line = pipein.readline()[:-1]
                        if line != "":
                            try:
                                args = json.loads(line)
                            except Exception:
                                args = []
                            evt = PipeEvent(data=args)
                            wx.PostEvent(self.app, evt)
                            break
                        time.sleep(0.2)
        self.running = False


class PipeApp(CustomApp):
    """Pip app variant that allows the app to be sent data via a pipe."""

    def __init__(self, *args, **kwargs):
        """Parse pipe args."""

        self.active_pipe = False
        self.pipe_thread = None
        self.pipe_name = kwargs.get("pipe_name", None)
        if "pipe_name" in kwargs:
            del kwargs["pipe_name"]
        CustomApp.__init__(self, *args, **kwargs)

    def OnInit(self):  # noqa
        """
        Check if this is the first instance, and if so, start the pipe listener.

        If not, send the current args to the pipe to be read
        by the first instance.
        """

        CustomApp.OnInit(self)
        self.Bind(EVT_PIPE_ARGS, self.on_pipe_args)
        if self.pipe_name is not None:
            if self.is_instance_okay():
                self.receive_arg_pipe()
            else:
                self.send_arg_pipe()
                return False
        return True

    def get_sys_args(self):
        """Get system args as unicode."""

        args = []
        encoding = sys.getfilesystemencoding()
        for a in sys.argv[1:]:
            args.append(a.decode(encoding) if isinstance(a, util.bstr) else a)
        return args

    def send_arg_pipe(self):
        """Send the current arguments down the pipe."""
        argv = self.get_sys_args()
        if util.platform() == "windows":
            args = self.process_args(argv)
            file_handle = ctypes.windll.kernel32.CreateFileW(
                self.pipe_name,
                GENERIC_READ | GENERIC_WRITE,
                0, None,
                OPEN_EXISTING,
                0, None
            )
            data = json.dumps(args) + '\n'
            bytes_written = ctypes.c_ulong(0)
            ctypes.windll.kernel32.WriteFile(
                file_handle, ctypes.c_wchar_p(data), len(data) * 2, ctypes.byref(bytes_written), None
            )
            ctypes.windll.kernel32.CloseHandle(file_handle)
        else:
            with codecs.open(self.pipe_name, "w", encoding="utf-8") as pipeout:
                args = self.process_args(argv)
                pipeout.write(json.dumps(args) + '\n')

    def process_args(self, arguments):
        """Noop, but can be overriden to process the args."""

        return arguments

    def receive_arg_pipe(self):
        """Start the pipe listenr thread."""

        self.active_pipe = True
        self.pipe_thread = ArgPipeThread(self, self.pipe_name)
        self.pipe_thread.Start()

    def OnExit(self):  # noqa
        """Stop the thread if needed."""

        if self.active_pipe:
            wx.Yield()
            self.pipe_thread.Stop()
            running = True
            while running:
                running = self.pipe_thread.IsRunning()
                time.sleep(0.1)
        return CustomApp.OnExit(self)

    def on_pipe_args(self, event):
        """An overridable event for when pipe arguments are received."""

        event.Skip()


class DebugFrameExtender(object):
    """Extend frame with debugger."""

    def set_keybindings(self, keybindings=[], debug_event=None):
        """
        Method to easily set key bindings.

        Also sets up debug keybindings and events.
        """

        # Create keybinding to open debug console, bind debug console to ctrl/cmd + ` depending on platform
        # if an event is passed in.
        tbl = []
        bindings = keybindings
        if debug_event is not None:
            mod = wx.ACCEL_CMD if util.platform() == "osx" else wx.ACCEL_CTRL
            bindings.append((mod, ord('`'), debug_event))

        for binding in keybindings:
            keyid = wx.NewId()
            self.Bind(wx.EVT_MENU, binding[2], id=keyid)
            tbl.append((binding[0], binding[1], keyid))

        if len(bindings):
            self.SetAcceleratorTable(wx.AcceleratorTable(tbl))

    def open_debug_console(self):
        """Open the debug console."""

        set_debug_console(True)
        # echo out log to console
        log.set_echo(True)
        if wx.GetApp().stdioWin.frame is None:
            wx.GetApp().stdioWin.write(log.read(), False)
        else:
            wx.GetApp().stdioWin.write("", False)
        debug("**Debug Console Opened**")

    def toggle_debug_console(self):
        """Open up the debug console if closed or close if opened."""

        set_debug_console(not get_debug_console())
        if get_debug_console():
            # echo out log to console
            log.set_echo(True)
            wx.GetApp().stdioWin.write(log.read(), False)
            debug("**Debug Console Opened**")
        else:
            debug("**Debug Console Closed**")
            # disable echoing of log to console
            log.set_echo(False)
            if wx.GetApp().stdioWin is not None:
                wx.GetApp().stdioWin.close()

    def close_debug_console(self):
        """
        On close, ensure that console is closes.

        Also, make sure echo is off in case logging
        occurs after App closing.
        """

        if get_debug_console():
            debug("**Debug Console Closed**")
            set_debug_console(False)
            log.set_echo(False)
            if wx.GetApp().stdioWin is not None:
                wx.GetApp().stdioWin.close()


def _log_struct(obj, log_func, label="Object"):
    """Base logger to log a dict in pretty print format."""

    log_func(obj, log_fmt="%(loglevel)s: " + label + ": %(message)s\n", msg_fmt=json_fmt)


def json_fmt(obj):
    """Format the dict as JSON."""

    return json.dumps(obj, sort_keys=True, indent=4, separators=(',', ': '))


def gui_log(msg):
    """Logger used in the GUI frames."""

    log._log(msg, echo=False)


def debug(msg, echo=True, log_fmt="%(loglevel)s: %(message)s\n", msg_fmt=None):
    """Debug level log."""

    if get_debug_mode():
        log.debug(msg, echo=echo, log_fmt=log_fmt, msg_fmt=msg_fmt)


def info(msg, echo=True, log_fmt="%(loglevel)s: %(message)s\n", msg_fmt=None):
    """Info level log."""

    log.info(msg, echo=echo, log_fmt=log_fmt, msg_fmt=msg_fmt)


def critical(msg, echo=True, log_fmt="%(loglevel)s: %(message)s\n", msg_fmt=None):
    """Critical level log."""

    log.critical(msg, echo=echo, log_fmt=log_fmt, msg_fmt=msg_fmt)


def warning(msg, echo=True, log_fmt="%(loglevel)s: %(message)s\n", msg_fmt=None):
    """Warning level log."""

    log.warning(msg, echo=echo, log_fmt=log_fmt, msg_fmt=msg_fmt)


def error(msg, echo=True, log_fmt="%(loglevel)s: %(message)s\n", msg_fmt=None):
    """Error level log."""

    log.error(msg, echo=echo, log_fmt=log_fmt, msg_fmt=msg_fmt)


def debug_struct(obj, label="Object"):
    """Debug level dict log."""

    _log_struct(obj, debug, label)


def info_struct(obj, label="Object"):
    """Info level dict log."""

    _log_struct(obj, info, label)


def critical_struct(obj, label="Object"):
    """Critical level dict log."""

    _log_struct(obj, critical, label)


def warning_struct(obj, label="Object"):
    """Warning level dict log."""

    _log_struct(obj, warning, label)


def error_struct(obj, label="Object"):
    """Error level dict log."""

    _log_struct(obj, error, label)


def init_app_log(name, level=simplelog.ERROR):
    """Init the app log."""

    global log
    global last_level
    if level != simplelog.DEBUG:
        last_level = level
    simplelog.init_global_log(name, level=last_level)
    log = simplelog.get_global_log()


def set_debug_mode(value):
    """Set whether the app is in debug mode."""

    global DEBUG_MODE
    global last_level
    DEBUG_MODE = bool(value)
    current_level = log.get_level()
    if DEBUG_MODE:
        if current_level > simplelog.DEBUG:
            last_level = current_level
        log.set_level(simplelog.DEBUG)
    elif not DEBUG_MODE:
        if last_level == simplelog.DEBUG:
            last_level = simplelog.ERROR
        log.set_level(last_level)


def set_debug_console(value):
    """Set debug console enable."""

    global DEBUG_CONSOLE
    DEBUG_CONSOLE = bool(value)


def get_debug_mode():
    """Get the debug mode."""

    return DEBUG_MODE


def get_debug_console():
    """Get debug console mode."""

    return DEBUG_CONSOLE
