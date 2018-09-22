"""
Changelog Dialog.

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
from .localization import _
from . import gui
from . import data
from .. import util
import markdown
import pymdownx.slugs as slugs
from .app.custom_app import debug
import webbrowser
import re

extensions = [
    "markdown.extensions.toc",
    "markdown.extensions.attr_list",
    "markdown.extensions.def_list",
    "markdown.extensions.smarty",
    "markdown.extensions.footnotes",
    "markdown.extensions.tables",
    "markdown.extensions.sane_lists",
    "markdown.extensions.admonition",
    "pymdownx.highlight",
    "pymdownx.inlinehilite",
    "pymdownx.magiclink",
    "pymdownx.superfences",
    "pymdownx.betterem",
    "pymdownx.extrarawhtml",
    "pymdownx.keys",
    "pymdownx.escapeall",
    "pymdownx.smartsymbols",
    "pymdownx.tasklist",
    "pymdownx.tilde",
    "pymdownx.caret"
]

extension_configs = {
    "markdown.extensions.toc": {
        "slugify": slugs.uslugify,
        # "permalink": "\ue157"
    },
    "pymdownx.inlinehilite": {
        "style_plain_text": True
    },
    "pymdownx.superfences": {
        "custom_fences": []
    },
    "pymdownx.magiclink": {
        "repo_url_shortener": True,
        "repo_url_shorthand": True,
        "user": "facelessuser",
        "repo": "Rummage"
    },
    "markdown.extensions.smarty": {
        "smart_quotes": False
    },
    "pymdownx.escapeall": {
        "hardbreak": True,
        "nbsp": True
    }
}


class ChangelogDialog(gui.HtmlDialog):
    """SettingsDialog."""

    def __init__(self, parent):
        """Init SettingsDialog object."""

        super(ChangelogDialog, self).__init__(parent)
        # if util.platform() == "windows":
        #     self.m_html_panel.SetDoubleBuffered(True)
        self.localize()
        self.refresh_localization()
        self.m_content_html.Bind(wx.html2.EVT_WEBVIEW_NAVIGATING, self.on_navigate)
        self.load_changelog()
        self.Fit()

    def localize(self):
        """Translage strings."""

        self.TITLE = _("Changelog")

    def refresh_localization(self):
        """Localize dialog."""

        self.SetTitle(self.TITLE)
        self.Fit()

    def load_changelog(self):
        """Handle copy event."""

        cl = data.get_file('changelog.md')
        css = data.get_file('webview.css')
        if not cl:
            cl = "# Changelog\n\nChangelog was not generated!\n"
        html = markdown.Markdown(extensions=extensions, extension_configs=extension_configs).convert(cl)
        html = '<!DOCTYPE html><html><head><meta charset="utf-8"><style>%s</style><body><div class="markdown">%s</div></body></html>' % (css, html)
        debug(html)
        while self.m_content_html.IsBusy():
            pass
        self.m_content_html.SetPage(html, '.')

    def on_cancel(self, event):
        """Close dialog."""

        self.Close()

    def on_navigate(self, event):
        """Handle links."""

        target = event.GetTarget()
        url = event.GetURL()
        debug("HTML Nav URL: " + url)
        debug("HTML Nav Target: " + target)

        # Handle basic link schemes
        if url.lower().startswith(('http://', 'https://', 'ftp://', 'ftps://')):
            webbrowser.open_new_tab(url)
            event.Veto()
        # Webkit relative page handling
        elif url.lower().startswith('file://'):
            pass
        # Handle webkit id jumps for IE
        elif url.startswith('about:blank#'):
            script = "document.getElementById('%s').scrollIntoView();" % url.replace('about:blank#', '')
            debug("HTML Nav ID: " + script)
            self.m_content_html.RunScript(script)
            event.Veto()
        # Show unhandled links
        else:
            debug("HTML unhandled link: " + url)
            event.Veto()
