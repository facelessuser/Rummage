"""
HTML Dialog.

Licensed under MIT
Copyright (c) 2013 - 2017 Isaac Muse <isaacmuse@gmail.com>

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
from .localization import _
from . import gui
from .controls import webview


class HTMLDialog(gui.HtmlDialog, webview.WebViewMixin):
    """HTML dialog."""

    def __init__(
        self, parent, content, title=None, content_type=webview.HTML_FILE,
        min_width=500, min_height=500, max_width=-1, max_height=-1
    ):
        """Initialize dialog."""

        super(HTMLDialog, self).__init__(parent)
        self.setup_html(self.m_content_html, control_title=self)
        self.SetSizeHints(wx.Size(min_width, min_height), wx.Size(max_width, max_height))
        self.localize()
        self.load(content, title, content_type)
        self.Fit()
        self.Center()

    def load(self, content, title=None, content_type=webview.HTML_FILE):
        """Reshow the dialog."""

        self.refresh_localization()
        self.load_html(self.m_content_html, content, title, content_type)

    def localize(self):
        """Translate strings."""

        self.TITLE = _("Untitled")

    def refresh_localization(self):
        """Localize dialog."""

        self.SetTitle(self.TITLE)
        self.Fit()

    def on_cancel(self, event):
        """Close dialog."""

        self.Close()
