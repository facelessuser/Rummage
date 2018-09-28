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
import markdown
import pymdownx.slugs as slugs

HTML_FILE = 0
HTML_STRING = 1
MARKDOWN_STRING = 2

EXTENSIONS = [
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
    "pymdownx.caret",
    "pymdownx.mark",
    "pymdownx.b64",
    "pymdownx.pathconverter"
]

EXTENSION_CONFIGS = {
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
    },
    "pymdownx.pathconverter": {
        "base_path": os.path.join(data.RESOURCE_PATH, 'docs'),
        "absolute": True
    },
    "pymdownx.b64": {
        "base_path": os.path.join(data.RESOURCE_PATH, 'docs')
    }
}

TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta http-equiv="x-ua-compatible" content="ie=edge">
<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
<title>%s</title>
<style>
%s
</style>
</head>
<body>
<div class="markdown">
%s
</div>
</body>
</html>
"""


def escape(txt):
    """Basic html escaping."""

    txt = txt.replace('&', '&amp;')
    txt = txt.replace('<', '&lt;')
    txt = txt.replace('>', '&gt;')
    txt = txt.replace('"', '&quot;')
    return txt


def convert_markdown(title, content):
    """Convert Markdown to HTML."""

    css = data.get_file(os.path.join('docs', 'css', 'theme.css'))
    html = markdown.Markdown(extensions=EXTENSIONS, extension_configs=EXTENSION_CONFIGS).convert(content)
    html = TEMPLATE % (escape(title), css, html)
    return html


class HTMLDialog(gui.HtmlDialog):
    """HTMLDialog."""

    def __init__(
        self, parent, content, title=None, content_type=HTML_FILE,
        min_width=500, min_height=500, max_width=-1, max_height=-1
    ):
        """Init SettingsDialog object."""

        super(HTMLDialog, self).__init__(parent)
        self.SetSizeHints(wx.Size(min_width, min_height), wx.Size(max_width, max_height))
        self.localize()
        self.busy = False
        self.m_content_html.Bind(wx.html2.EVT_WEBVIEW_NAVIGATING, self.on_navigate)
        # self.m_content_html.Bind(wx.html2.EVT_WEBVIEW_NAVIGATED, self.on_navigated)
        self.m_content_html.Bind(wx.html2.EVT_WEBVIEW_LOADED, self.on_loaded)
        self.m_content_html.Bind(wx.html2.EVT_WEBVIEW_TITLE_CHANGED, self.on_title_changed)
        self.load(content, title, content_type)
        self.Fit()
        self.Center()

    def load(self, content, title=None, content_type=HTML_FILE):
        """Reshow the dialog."""

        self.content_type = content_type
        self.refresh_localization()
        self.load_html(content, title)

    def localize(self):
        """Translage strings."""

        self.TITLE = _("Untitled")

    def refresh_localization(self):
        """Localize dialog."""

        self.SetTitle(self.TITLE)
        self.Fit()

    def load_html(self, content, title):
        """Load HTML."""

        if self.content_type == HTML_FILE:
            url = 'file://%s' % os.path.join(data.RESOURCE_PATH, 'docs', content).replace('\\', '/')
            if self.busy:
                self.m_content_html.Stop()
            self.busy = True
            self.m_content_html.LoadURL(url)
        else:
            if self.content_type == MARKDOWN_STRING:
                html = convert_markdown(title, content)
            else:
                html = content
            self.busy = True
            self.m_content_html.SetPage(html, 'file://')
            if util._PLATFORM == "windows":
                # Ugh.  Why can't things just work
                # Here we must reload the page so that things render properly.
                # This was done to fix poorly rendered pages observed in Windows.
                self.m_content_html.Reload()

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
        if ltype == util.BLANK_LINK:
            self.busy = True
        # We don't handle links outside of a "blank" (HTML string) page.
        # This mainly occurs on Windows.
        elif self.content_type == HTML_STRING and url.startswith('about:'):
            self.busy = False
            event.Veto()
        # 'Nix systems treat "blank" (HTML string) pages as root paths most of the time.
        # So if we get `file:///` that is not empty and not linking to a target, we are
        # Linking outside or page, but not to an external site.
        elif self.content_type == HTML_STRING and not (url == 'file:///' or url.startswith('file:///#')):
            self.busy = False
            event.Veto()
        elif ltype == util.HTML_LINK:
            self.busy = True
        # Send URL links to browser
        elif ltype == util.URL_LINK:
            webbrowser.open_new_tab(url)
            self.busy = False
            event.Veto()
        # Show unhandled links
        else:
            debug("HTML unhandled link: " + url)
            self.busy = False
            event.Veto()
