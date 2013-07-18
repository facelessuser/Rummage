"""
Rummage App

Licensed under MIT
Copyright (c) 2013 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import wx

from _gui.custom_app import PipeApp
from _gui.platform_window_focus import platform_window_focus
from _gui.custom_app import *
from _gui.rummage_dialog import RummageFrame
from _gui.regex_test_dialog import RegexTestDialog
import _gui.notify as notify

from _icons.rum_ico import rum_64

notify.set_growl_icon(rum_64.GetData())
wx.Log.EnableLogging(False)


class RummageApp(PipeApp):
    def __init__(self, *args, **kwargs):
        """
        Init RummageApp object
        """

        super(RummageApp, self).__init__(*args, **kwargs)

    def on_pipe_args(self, event):
        """
        When receiving arguments via named pipes,
        look for the search path argument, and populate
        the search path in the RummageFrame
        """

        frame = self.GetTopWindow()
        if frame is not None and isinstance(frame, RummageFrame):
            args = iter(event.data.split("|"))
            filename = None
            for a in args:
                if a == "-s":
                    try:
                        a = args.next()
                        filename = a
                        break
                    except StopIteration:
                        break
            if filename is not None:
                frame.m_searchin_text.safe_set_value(filename)
                frame.m_grep_notebook.SetSelection(0)
                frame.m_searchfor_textbox.GetTextCtrl().SetFocus()
            platform_window_focus(frame)

    def process_args(self, arguments):
        """
        Event for processing the arguments
        """

        argv = iter(arguments)
        args = []
        for a in argv:
            args.append(a)
            if a == "-s":
                try:
                    args.append(abspath(normpath(argv.next())))
                except StopIteration:
                    break
        return args

    def MacReopenApp(self):
        """
        Ensure that app will be unminimized
        in OSX on dock icon click
        """

        frame = self.GetTopWindow()
        platform_window_focus(frame)
