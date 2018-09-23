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
import wx.html2
import os
from .localization import _
from . import gui
from . import data
from .app.custom_app import debug
import webbrowser
from .. import util


class HTMLDialog(gui.HtmlDialog):
    """HTMLDialog."""

    def __init__(self, parent, content, title=None, string=False):
        """Init SettingsDialog object."""

        super(HTMLDialog, self).__init__(parent)
        self.localize()
        self.busy = False
        self.m_content_html.Bind(wx.html2.EVT_WEBVIEW_NAVIGATING, self.on_navigate)
        # self.m_content_html.Bind(wx.html2.EVT_WEBVIEW_NAVIGATED, self.on_navigated)
        self.m_content_html.Bind(wx.html2.EVT_WEBVIEW_LOADED, self.on_loaded)
        self.m_content_html.Bind(wx.html2.EVT_WEBVIEW_TITLE_CHANGED, self.on_title_changed)
        self.load(content, title, string)
        self.Fit()

    def load(self, content, title=None, string=False):
        """Reshow the dialog."""

        self.refresh_localization()
        self.load_html(content, string)

    def localize(self):
        """Translage strings."""

        self.TITLE = _("Untitled")

    def refresh_localization(self):
        """Localize dialog."""

        self.SetTitle(self.TITLE)
        self.Fit()

    def load_html(self, content, string):
        """Load HTML."""

        if not string:
            url = 'file://%s' % os.path.join(data.RESOURCE_PATH, 'docs', content).replace('\\', '/')
            if self.busy:
                self.m_content_html.Stop()
            self.busy = True
            self.m_content_html.LoadURL(url)
        else:
            # We may not even use this
            pass

    def on_title_changed(self, event):
        """Get title."""

        title = self.m_content_html.CurrentTitle
        self.SetTitle(title)

    def on_loaded(self, event):
        """Handle laoded event."""

        self.busy = False

    def on_cancel(self, event):
        """Close dialog."""

        self.Close()

    def on_navigate(self, event):
        """Handle links."""

        target = event.GetTarget()
        url = event.GetURL()
        debug("HTML Nav URL: " + url)
        debug("HTML Nav Target: " + target)

        # Things we can allow the backend to handle (local HTML files)
        ltype = util.link_type(url)
        if ltype == util.HTML_LINK:
            self.busy = True
            pass
        # Send URL links to browser
        elif ltype == util.URL_LINK:
            webbrowser.open_new_tab(url)
            self.busy = False
            event.Veto()
        # Handle webkit id jumps for IE (usually when handling HTML strings, not files)
        elif url.startswith('about:blank#'):
            script = "document.getElementById('%s').scrollIntoView();" % url.replace('about:blank#', '')
            debug("HTML Nav ID: " + script)
            self.m_content_html.RunScript(script)
            self.busy = False
            event.Veto()
        # Show unhandled links
        else:
            debug("HTML unhandled link: " + url)
            self.busy = False
            event.Veto()
