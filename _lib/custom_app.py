'''
Custom App
https://gist.github.com/facelessuser/5750404

Licensed under MIT
Copyright (c) 2013 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import wx
import simplelog
import sys
import json

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
            wx.MessageBox("Only one instance allowed!", "ERROR", wx.OK | wx.ICON_ERROR)
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
