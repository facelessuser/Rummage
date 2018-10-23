"""
A `WebView` mixin.

Mixin for a window that adds functions to setup `html2` objects.
Adds events that control external and internal links.
Loads HTML files from our specified data location.
Loads HTML from strings and even converts it from Markdown if requested.

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
import wx.html2
import markdown
import pymdownx.slugs as slugs
import pymdownx
import os
from .. import data
from ..app.custom_app import debug
import webbrowser
from ... import util
import functools

PMDX6 = pymdownx.version_info >= (6, 0, 0)

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
    }
}

# No need to use `base64` as `pathconverter` issues have been fixed in version 6.0.0
if not PMDX6:
    EXTENSION_CONFIGS["pymdownx.b64"] = {
        "base_path": os.path.join(data.RESOURCE_PATH, 'docs')
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
    """Basic HTML escaping."""

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


class WebViewMixin(object):
    """HTML `WebView`."""

    def setup_html(self, obj, control_title=None):
        """Setup HTML events."""

        # Setup busy tracker
        obj.busy = False
        obj.control_title = control_title

        # Setup events
        obj.Bind(wx.html2.EVT_WEBVIEW_NAVIGATING, functools.partial(self.on_navigate, obj=obj))
        obj.Bind(wx.html2.EVT_WEBVIEW_LOADED, functools.partial(self.on_loaded, obj=obj))
        obj.Bind(wx.html2.EVT_WEBVIEW_TITLE_CHANGED, functools.partial(self.on_title_changed, obj=obj))

    def load_html(self, obj, content, title, content_type):
        """Load HTML."""

        obj.content_type = content_type

        if obj.content_type == HTML_FILE:
            url = 'file://%s' % os.path.join(data.RESOURCE_PATH, 'docs', content).replace('\\', '/')
            if obj.busy:
                self.Stop()
            obj.busy = True
            obj.LoadURL(url)
        else:
            if obj.content_type == MARKDOWN_STRING:
                html = convert_markdown(title, content)
            else:
                html = content
            obj.busy = True
            obj.SetPage(html, 'file://')
            if util._PLATFORM == "windows":
                # Ugh.  Why can't things just work
                # Here we must reload the page so that things render properly.
                # This was done to fix poorly rendered pages observed in Windows.
                obj.Reload()

    def on_navigate(self, event, obj=None):
        """Handle links."""

        target = event.GetTarget()
        url = event.GetURL()
        debug("HTML Nav URL: " + url)
        debug("HTML Nav Target: " + target)

        # Things we can allow the backend to handle (local HTML files)
        ltype = util.link_type(url)
        if ltype == util.BLANK_LINK:
            obj.busy = True
        # We don't handle links outside of a "blank" (HTML string) page.
        # This mainly occurs on Windows.
        elif obj.content_type == HTML_STRING and url.startswith('about:'):
            obj.busy = False
            event.Veto()
        # 'Nix systems treat "blank" (HTML string) pages as root paths most of the time.
        # So if we get `file:///` that is not empty and not linking to a target, we are
        # Linking outside or page, but not to an external site.
        elif obj.content_type == HTML_STRING and not (url == 'file:///' or url.startswith('file:///#')):
            obj.busy = False
            event.Veto()
        elif ltype == util.HTML_LINK:
            obj.busy = True
        # Send URL links to browser
        elif ltype == util.URL_LINK:
            webbrowser.open_new_tab(url)
            obj.busy = False
            event.Veto()
        # Show unhandled links
        else:
            debug("HTML unhandled link: " + url)
            obj.busy = False
            event.Veto()

    def on_title_changed(self, event, obj=None):
        """Get title."""

        if obj.control_title is not None:
            title = obj.CurrentTitle
            obj.control_title.SetTitle(title)

    def on_loaded(self, event, obj=None):
        """Handle loaded event."""

        obj.busy = False
