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
import os
from .platform_window_focus import platform_window_focus
from .custom_app import PipeApp
from ..dialogs import rummage_dialog
from ..settings import Settings
import wx
from .. import util

__all__ = ('RummageApp',)


class RummageApp(PipeApp):
    """Rummage app."""

    def __init__(self, argv, **kwargs):
        """Initialize Rummage app object."""

        if util.platform() == "windows":
            import ctypes

            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('facelessuser.rummage.app.version')

        self.debug_mode = argv.debug
        self.path = argv.path if argv.path is not None else None
        self.no_redirect = argv.no_redirect

        PipeApp.__init__(self, **kwargs)

    def OnInit(self):
        """Call on initialization."""

        self.locale = wx.Locale(wx.LANGUAGE_DEFAULT)

        # Setup log, setting, and cache file, and start logging
        Settings.setup_setting_files()
        log = Settings.get_log_file()
        self.setup_logging(log, self.debug_mode, self.no_redirect)

        # Load up the settings and setup single instance
        Settings.load_settings()
        single_instance = Settings.get_single_instance()
        if single_instance and not self.ensure_single_instance("Rummage"):
            self.setup_pipe(Settings.get_fifo())
            self.send_arg_pipe()
            return False

        if not self.setup_pipe(Settings.get_fifo() if single_instance else None):
            return False

        # Setup app.
        if self.single_instance is None or self.is_instance_okay():
            window = rummage_dialog.RummageFrame(
                None,
                self.path,
                self.debug_mode
            )
            window.Show()
            self.SetTopWindow(window)
        return True

    def OnExit(self):
        """Handle exit."""

        Settings.unload()
        return PipeApp.OnExit(self)

    def on_pipe_args(self, event):
        """
        Handle piped arguments.

        When receiving arguments via named pipes,
        look for the search path argument, and populate
        the search path in the Rummage frame
        """

        frame = self.GetTopWindow()
        if frame is not None:
            args = iter(event.data)
            filename = None
            for a in args:
                if a == "--path":
                    try:
                        a = next(args)
                        filename = a
                        break
                    except StopIteration:
                        break
            if filename is None:
                cwd = os.getcwd()
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
                    args.append(os.path.abspath(os.path.normpath(next(argv))))
                    path_arg_found = True
                except StopIteration:
                    break
        if not path_arg_found:
            args.extend(['--path', os.getcwd()])

        return args

    def MacReopenApp(self):  # noqa
        """Ensure that app will be un-minimized in macOS on dock icon click."""

        frame = self.GetTopWindow()
        platform_window_focus(frame)
