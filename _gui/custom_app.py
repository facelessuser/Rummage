"""
Custom App
https://gist.github.com/facelessuser/5750404

Licensed under MIT
Copyright (c) 2013 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import wx
import simplelog
import sys
import json
import wx.lib.newevent
import os
import thread
import time

if sys.platform.startswith('win'):
    _PLATFORM = "windows"
elif sys.platform == "darwin":
    _PLATFORM = "osx"
else:
    _PLATFORM = "linux"

if _PLATFORM == "windows":
    import win32pipe, win32file

PipeEvent, EVT_PIPE_ARGS = wx.lib.newevent.NewEvent()

log = None
last_level = simplelog.ERROR
DEBUG_MODE = False
DEBUG_CONSOLE = False


class GuiLog(wx.PyOnDemandOutputWindow):
    def __init__(self, title="Debug Console"):
        # wx.PyOnDemandOutputWindow is old class style
        # Cannot use super with old class styles
        wx.PyOnDemandOutputWindow.__init__(self, title)

    def CreateOutputWindow(self, st):
        wx.PyOnDemandOutputWindow.CreateOutputWindow(self, st)
        # Create debug keybinding to open debug console
        debugid= wx.NewId()
        self.frame.Bind(wx.EVT_MENU, self.debug_close, id=debugid)
        mod = wx.ACCEL_CMD if sys.platform == "darwin" else wx.ACCEL_CTRL
        accel_tbl = wx.AcceleratorTable(
            [(mod, ord('`'), debugid)]
        )
        self.frame.SetAcceleratorTable(accel_tbl)

    def debug_close(self, event):
        self.frame.Close()

    def write(self, text, echo=True):
        if self.frame is None:
            if not wx.Thread_IsMain():
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
            if not wx.Thread_IsMain():
                if echo:
                    wx.CallAfter(gui_log, text)
                if get_debug_console():
                    wx.CallAfter(self.text.AppendText, text)
            else:
                if echo:
                    gui_log(text)
                if get_debug_console():
                    self.text.AppendText(text)

    def OnCloseWindow(self, event):
        if self.frame is not None:
            self.frame.Destroy()
        self.frame = None
        self.text  = None
        self.parent = None
        if get_debug_console():
            set_debug_console(False)
            log.set_echo(False)
            debug("**Debug Console Closed**\n")


class CustomApp(wx.App):
    def __init__(self, *args, **kwargs):
        self.outputWindowClass = GuiLog
        self.custom_init(*args, **kwargs)
        if "single_instance_name" in kwargs:
            del kwargs["single_instance_name"]
        if "callback" in kwargs:
            del kwargs["callback"]
        super(CustomApp, self).__init__(*args, **kwargs)

    def custom_init(self, *args, **kwargs):
        self.single_instance = None
        self.init_callback = None
        instance_name = kwargs.get("single_instance_name", None)
        callback = kwargs.get("callback", None)
        if instance_name is not None and isinstance(instance_name, basestring):
            self.single_instance = instance_name
        if callback is not None and hasattr(callback, '__call__'):
            self.init_callback = callback

    def ensure_single_instance(self, name):
        self.name = "%s-%s" % (self.single_instance, wx.GetUserId())
        self.instance = wx.SingleInstanceChecker(self.name)
        if self.instance.IsAnotherRunning():
            # wx.MessageBox("Only one instance allowed!", "ERROR", wx.OK | wx.ICON_ERROR)
            return False
        return True

    def is_instance_okay(self):
        return self.instance_okay

    def OnInit(self):
        self.instance_okay = True
        if self.single_instance is not None:
            if not self.ensure_single_instance(self.single_instance):
                self.instance_okay = False
        if self.init_callback is not None and self.instance_okay:
            self.init_callback()
        return True

    def OnExit(self):
        del self.instance


class ArgPipeThread(object):
    def __init__(self, app, pipe_name):
        self.app = app
        self.pipe_name = pipe_name

    def Start(self):
        self.check_pipe = True
        self.running = True
        thread.start_new_thread(self.Run, ())

    def Stop(self):
        self.check_pipe = False
        if _PLATFORM == "windows":
            fileHandle = win32file.CreateFile(
                self.pipe_name,
                win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                0, None,
                win32file.OPEN_EXISTING,
                0, None
            )
            data = '\n'
            win32file.WriteFile(fileHandle, data)
            win32file.CloseHandle(fileHandle)
        else:
            with open(self.pipe_name, "w") as pipeout:
                pipeout.write('\n')

    def IsRunning(self):
        return self.running

    def Run(self):
        if _PLATFORM == "windows":
            data = ""
            p = win32pipe.CreateNamedPipe(
                self.pipe_name,
                win32pipe.PIPE_ACCESS_DUPLEX,
                win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_WAIT,
                1, 65536, 65536, 300, None
            )
            while self.check_pipe:
                win32pipe.ConnectNamedPipe(p, None)
                result = win32file.ReadFile(p, 4096)
                if result[0] == 0:
                    data += result[1].replace("\r", "")
                    if len(data) and data[-1] == "\n":
                        lines = data.rstrip("\n").split("\n")
                        evt = PipeEvent(data=lines[-1])
                        wx.PostEvent(self.app, evt)
                        data = ""
                win32pipe.DisconnectNamedPipe(p)
                time.sleep(0.2)
        else:
            if os.path.exists(self.pipe_name):
                os.unlink(self.pipe_name)
            if not os.path.exists(self.pipe_name):
                os.mkfifo(self.pipe_name)

            with open(self.pipe_name, "r") as pipein:
                while self.check_pipe:
                    line = pipein.readline()[:-1]
                    if line != "":
                        evt = PipeEvent(data=line)
                        wx.PostEvent(self.app, evt)
                    time.sleep(0.2)
        self.running = False


class PipeApp(CustomApp):
    def __init__(self, *args, **kwargs):
        self.active_pipe = False
        self.pipe_thread = None
        self.pipe_name = kwargs.get("pipe_name", None)
        if "pipe_name" in kwargs:
            del kwargs["pipe_name"]
        super(PipeApp, self).__init__(*args, **kwargs)

    def OnInit(self):
        super(PipeApp, self).OnInit()
        self.Bind(EVT_PIPE_ARGS, self.OnPipeArgs)
        if self.pipe_name is not None:
            if self.is_instance_okay():
                self.receive_arg_pipe()
            else:
                self.send_arg_pipe()
                return False
        return True

    def send_arg_pipe(self):
        if len(sys.argv) > 1:
            if _PLATFORM == "windows":
                argv = iter(sys.argv[1:])
                args = []
                for a in argv:
                    args.append(a)
                    if a == "-s":
                        try:
                            args.append(os.path.abspath(os.path.normpath(argv.next())))
                        except StopIteration:
                            break
                fileHandle = win32file.CreateFile(
                    self.pipe_name,
                    win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                    0, None,
                    win32file.OPEN_EXISTING,
                    0, None
                )
                data = '|'.join(args) + '\n'
                win32file.WriteFile(fileHandle, data)
                win32file.CloseHandle(fileHandle)
            else:
                with open(self.pipe_name, "w") as pipeout:
                    argv = iter(sys.argv[1:])
                    args = []
                    for a in argv:
                        args.append(a)
                        if a == "-s":
                            try:
                                args.append(os.path.abspath(os.path.normpath(argv.next())))
                            except StopIteration:
                                break
                    pipeout.write('|'.join(args) + '\n')

    def receive_arg_pipe(self):
        self.active_pipe = True
        self.pipe_thread = ArgPipeThread(self, self.pipe_name)
        self.pipe_thread.Start()

    def OnExit(self):
        if self.active_pipe:
            wx.Yield()
            self.pipe_thread.Stop()
            running = True
            while running:
                running = self.pipe_thread.IsRunning()
                time.sleep(0.1)
        super(PipeApp, self).OnExit()

    def OnPipeArgs(self, event):
        event.Skip()


class DebugFrameExtender(object):
    def set_keybindings(self, keybindings=[], debug_event=None):
        # Create keybinding to open debug console, bind debug console to ctrl/cmd + ` depending on platform
        # if an event is passed in.
        tbl = []
        bindings = keybindings
        if debug_event is not None:
            mod = wx.ACCEL_CMD if sys.platform == "darwin" else wx.ACCEL_CTRL
            bindings.append((mod, ord('`'), debug_event))

        for binding in keybindings:
            keyid = wx.NewId()
            self.Bind(wx.EVT_MENU, binding[2], id=keyid)
            tbl.append((binding[0], binding[1], keyid))

        if len(bindings):
            self.SetAcceleratorTable(wx.AcceleratorTable(tbl))

    def open_debug_console(self):
        """
        Open up the debug console if closed
        or close if opened.
        """
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
    log_func(obj, format="%(loglevel)s: " + label + ": %(message)s\n", fmt=json_fmt)


def json_fmt(obj):
    return json.dumps(obj, sort_keys=True, indent=4, separators=(',', ': '))


def gui_log(msg):
    log._log(msg, echo=False)


def debug(msg, echo=True, format="%(loglevel)s: %(message)s\n", fmt=None):
    if get_debug_mode():
        log.debug(msg, echo=echo, format=format, fmt=fmt)


def info(msg, echo=True, format="%(loglevel)s: %(message)s\n", fmt=None):
    log.info(msg, echo=echo, format=format, fmt=fmt)


def critical(msg, echo=True, format="%(loglevel)s: %(message)s\n", fmt=None):
    log.critical(msg, echo=echo, format=format, fmt=fmt)


def warning(msg, echo=True, format="%(loglevel)s: %(message)s\n", fmt=None):
    log.warning(msg, echo=echo, format=format, fmt=fmt)


def error(msg, echo=True, format="%(loglevel)s: %(message)s\n", fmt=None):
    log.error(msg, echo=echo, format=format, fmt=fmt)


def debug_struct(obj, label="Object"):
    _log_struct(obj, debug, label)


def info_struct(obj, label="Object"):
    _log_struct(obj, info, label)


def critical_struct(obj, label="Object"):
    _log_struct(obj, critical, label)


def warning_struct(obj, label="Object"):
    _log_struct(obj, warning, label)


def error_struct(obj, label="Object"):
    _log_struct(obj, error, label)


def init_app_log(name, level=simplelog.ERROR):
    global log
    global last_level
    last_level = level
    simplelog.init_global_log(name, level=last_level)
    log = simplelog.get_global_log()


def set_debug_mode(value):
    global DEBUG_MODE
    global last_level
    DEBUG_MODE = bool(value)
    current_level = log.get_level()
    if DEBUG_MODE and current_level > simplelog.DEBUG:
        last_level = current_level
        log.set_level(simplelog.DEBUG)
    elif not DEBUG_MODE and last_level != simplelog.DEBUG:
        log.set_level(last_level)


def set_debug_console(value):
    global DEBUG_CONSOLE
    DEBUG_CONSOLE = bool(value)


def get_debug_mode():
    return DEBUG_MODE


def get_debug_console():
    return DEBUG_CONSOLE
