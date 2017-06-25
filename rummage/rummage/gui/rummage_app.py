"""
Rummage App.

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
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.
"""
from __future__ import unicode_literals
import wx
import os
from .platform_window_focus import platform_window_focus
from .custom_app import PipeApp, set_debug_mode
from .rummage_dialog import RummageFrame
from .regex_test_dialog import RegexTestDialog
from .. import util

__all__ = (
    'set_debug_mode', 'RummageApp', 'RummageFrame', 'RegexTestDialog'
)

wx.Log.EnableLogging(False)


class RummageApp(PipeApp):
    """RummageApp."""

    def __init__(self, *args, **kwargs):
        """Init RummageApp object."""

        PipeApp.__init__(self, *args, **kwargs)

    def on_pipe_args(self, event):
        """
        Handle piped arguments.

        When receiving arguments via named pipes,
        look for the search path argument, and populate
        the search path in the RummageFrame
        """

        frame = self.GetTopWindow()
        if frame is not None and isinstance(frame, RummageFrame):
            args = iter(event.data)
            filename = None
            for a in args:
                if a == "--path":
                    try:
                        a = util.iternext(args)
                        filename = a
                        break
                    except StopIteration:
                        break
            if filename is None:
                cwd = os.getcwdu()
                filename = cwd
            if filename:
                frame.m_searchin_text.safe_set_value(filename)
                frame.m_grep_notebook.SetSelection(0)
                frame.m_searchfor_textbox.GetTextCtrl().SetFocus()
            platform_window_focus(frame)

    def process_args(self, arguments):
        """Event for processing the arguments."""

        argv = iter(arguments)
        args = []
        path_arg_found = False
        for a in argv:
            args.append(a)
            if a == "--path":
                try:
                    args.append(os.path.abspath(os.path.normpath(util.iternext(argv))))
                    path_arg_found = True
                except StopIteration:
                    break
        if not path_arg_found:
            args.extend(['--path', util.getcwd()])

        return args

    def MacReopenApp(self):  # noqa
        """Ensure that app will be unminimized in OSX on dock icon click."""

        frame = self.GetTopWindow()
        platform_window_focus(frame)
