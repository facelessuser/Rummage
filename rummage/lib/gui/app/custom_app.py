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
import sys
import json
import os
import time
import wx
import wx.lib.newevent
from ... import util
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
last_level = wx.LOG_Error
DEBUG_MODE = False


class CustomApp(wx.App):
    """Custom app that adds a number of features."""

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
            ctypes.windll.kernel32.CloseHandle(p)
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

        return util.to_unicode_argv()[1:]

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


class CustomLog(wx.Log):
    """Logger."""

    def __init__(self, log_file, no_redirect):
        """Initialize."""

        self.format = "%(message)s"
        self.file_name = log_file

        try:
            self.log_file = codecs.open(log_file, 'w', encoding='utf-8')
        except Exception:
            self.log_file = None

        self.no_redirect = no_redirect

        super(CustomLog, self).__init__()

    def get_log_file(self):
        """Get log file path and name."""

        return self.file_name

    def DoLogText(self, msg):
        """Log the text."""

        try:
            if self.log_file:
                self.log_file.write(msg)
        except Exception:
            pass
        if self.no_redirect:
            try:
                sys.stdout.write(
                    (self.format % {"message": msg})
                )
            except UnicodeEncodeError:
                sys.stdout.write(
                    (self.format % {"message": msg}).encode(self.encoding, 'replace').decode(self.encoding)
                )

    def formatter(self, lvl, log_fmt, msg, msg_fmt=None):
        """Special formatters for log message."""

        return log_fmt % {
            "loglevel": lvl,
            "message": util.to_ustr(msg if msg_fmt is None else msg_fmt(msg))
        }

    def _log_struct(self, obj, log_func, label="Object"):
        """Base logger to log a dict in pretty print format."""

        log_func(obj, log_fmt="%(loglevel)s: " + label + ": %(message)s\n", msg_fmt=json_fmt)

    def _log(self, msg):
        """Base logger."""

        return self.format % {"message": msg}

    def _debug(self, msg, log_fmt="%(loglevel)s: %(message)s\n", msg_fmt=None):
        """Debug level log."""

        if self.GetLogLevel() <= wx.LOG_Debug:
            self.DoLogText(self._log(self.formatter("DEBUG", log_fmt, msg, msg_fmt)))

    def _info(self, msg, log_fmt="%(loglevel)s: %(message)s\n", msg_fmt=None):
        """Info level log."""

        if self.GetLogLevel() <= wx.LOG_Info:
            self.DoLogText(self._log(self.formatter("INFO", log_fmt, msg, msg_fmt)))

    def _critical(self, msg, log_fmt="%(loglevel)s: %(message)s\n", msg_fmt=None):
        """Critical level log."""

        if self.GetLogLevel() <= wx.LOG_FatalError:
            self.DoLogText(self._log(self.formatter("CRITICAL", log_fmt, msg, msg_fmt)))

    def _warning(self, msg, log_fmt="%(loglevel)s: %(message)s\n", msg_fmt=None):
        """Warning level log."""

        if self.GetLogLevel() <= wx.LOG_Warning:
            self.DoLogText(self._log(self.formatter("WARNING", log_fmt, msg, msg_fmt)))

    def _error(self, msg, log_fmt="%(loglevel)s: %(message)s\n", msg_fmt=None):
        """Error level log."""

        if self.GetLogLevel() <= wx.LOG_Error:
            self.DoLogText(self._log(self.formatter("ERROR", log_fmt, msg, msg_fmt)))

    def close_log(self):
        """Close log file."""

        if self.log_file:
            self.log_file.close()


def debug(*args, **kwargs):
    """Log wrapper for debug."""

    log._debug(*args, **kwargs)


def info(*args, **kwargs):
    """Log wrapper for info."""

    log._info(*args, **kwargs)


def critical(*args, **kwargs):
    """Log wrapper for critical."""

    log._critical(*args, **kwargs)


def warning(*args, **kwargs):
    """Log wrapper for warning."""

    log._warning(*args, **kwargs)


def error(*args, **kwargs):
    """Log wrapper for error."""

    log._error(*args, **kwargs)


def json_fmt(obj):
    """Format the dict as JSON."""

    return json.dumps(obj, sort_keys=True, indent=4, separators=(',', ': '))


def debug_struct(obj, label="Object"):
    """Debug level dict log."""

    log._log_struct(obj, log._debug, label)


def info_struct(obj, label="Object"):
    """Info level dict log."""

    log._log_struct(obj, log._info, label)


def critical_struct(obj, label="Object"):
    """Critical level dict log."""

    log._log_struct(obj, log._critical, label)


def warning_struct(obj, label="Object"):
    """Warning level dict log."""

    log._log_struct(obj, log._warning, label)


def error_struct(obj, label="Object"):
    """Error level dict log."""

    log._log_struct(obj, log._error, label)


def init_app_log(name, no_redirect=False, level=wx.LOG_Error):
    """Init the app log."""

    global log
    global last_level
    if level != wx.LOG_Debug:
        last_level = level
    log = CustomLog(name, no_redirect)
    wx.Log.SetActiveTarget(log)


def get_log_file():
    """Get log file path."""

    return log.get_log_file()


def close_log():
    """Close the log."""

    global log
    if log:
        log.close_log()


def set_debug_mode(value):
    """Set whether the app is in debug mode."""

    global DEBUG_MODE
    global last_level
    DEBUG_MODE = bool(value)
    current_level = log.GetLogLevel()
    if DEBUG_MODE:
        if current_level > wx.LOG_Debug:
            last_level = current_level
        log.SetLogLevel(wx.LOG_Debug)
    elif not DEBUG_MODE:
        if last_level == wx.LOG_Debug:
            last_level = wx.LOG_Error
        log.SetLogLevel(last_level)


def get_debug_mode():
    """Get the debug mode."""

    return DEBUG_MODE
