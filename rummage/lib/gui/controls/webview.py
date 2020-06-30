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
import os
import re
import html
from urllib.request import url2pathname
from urllib.parse import urlparse
from .. import data
from ..app.custom_app import debug
import webbrowser
from .. import util
import functools

HTML_FILE = 0
HTML_STRING = 1
MARKDOWN_STRING = 2

URL_LINK = 0
HTML_LINK = 1
BLANK_LINK = 2
OTHER_LINK = 3

RE_WIN_DRIVE_LETTER = re.compile(r"^[A-Za-z]$")
RE_WIN_DRIVE_PATH = re.compile(r"^[A-Za-z]:(?:\\.*)?$")
RE_SLASH_WIN_DRIVE = re.compile(r"^/[A-Za-z]{1}:/.*")
RE_URL = re.compile('(http|ftp)s?|data|mailto|tel|news')

EXTENSIONS = [
    "markdown.extensions.toc",
    "markdown.extensions.attr_list",
    "markdown.extensions.def_list",
    "markdown.extensions.smarty",
    "markdown.extensions.footnotes",
    "markdown.extensions.tables",
    "markdown.extensions.sane_lists",
    "markdown.extensions.admonition",
    "markdown.extensions.md_in_html",
    "pymdownx.highlight",
    "pymdownx.inlinehilite",
    "pymdownx.magiclink",
    "pymdownx.superfences",
    "pymdownx.betterem",
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
    """Basic HTML escaping."""

    txt = txt.replace('&', '&amp;')
    txt = txt.replace('<', '&lt;')
    txt = txt.replace('>', '&gt;')
    txt = txt.replace('"', '&quot;')
    return txt


def convert_markdown(title, content):
    """Convert Markdown to HTML."""

    css = data.get_file(os.path.join('docs', 'css', 'theme.css'))
    content = markdown.Markdown(extensions=EXTENSIONS, extension_configs=EXTENSION_CONFIGS).convert(content)
    content = TEMPLATE % (escape(title), css, content)
    return content


def parse_url(url):
    """
    Parse the URL.

    Try to determine if the following is a file path or
    (as we will call anything else) a URL.
    We return it slightly modified and combine the path parts.
    We also assume if we see something like c:/ it is a Windows path.
    We don't bother checking if this **is** a Windows system, but
    'nix users really shouldn't be creating weird names like c: for their folder.
    """

    is_url = False
    is_absolute = False
    is_blank = False
    scheme, netloc, path, params, query, fragment = urlparse(html.unescape(url))

    if scheme == 'about' and netloc == '' and path == "blank":
        is_blank = True
    elif RE_URL.match(scheme):
        # Clearly a URL
        is_url = True
    elif scheme == '' and netloc == '' and path == '':
        # Maybe just a URL fragment
        is_url = True
    elif scheme == 'file' and (RE_WIN_DRIVE_PATH.match(netloc)):
        # file://c:/path or file://c:\path
        path = '/' + (netloc + path).replace('\\', '/')
        netloc = ''
        is_absolute = True
    elif scheme == 'file' and netloc.startswith('\\'):
        # file://\c:\path or file://\\path
        path = (netloc + path).replace('\\', '/')
        netloc = ''
        is_absolute = True
    elif scheme == 'file':
        # file:///path
        is_absolute = True
    elif RE_WIN_DRIVE_LETTER.match(scheme):
        # c:/path
        path = '/%s:%s' % (scheme, path.replace('\\', '/'))
        scheme = 'file'
        netloc = ''
        is_absolute = True
    elif scheme == '' and netloc != '' and url.startswith('//'):
        # //file/path
        path = '//' + netloc + path
        scheme = 'file'
        netloc = ''
        is_absolute = True
    elif scheme != '' and netloc != '':
        # A non file path or strange URL
        is_url = True
    elif path.startswith(('/', '\\')):
        # /root path
        is_absolute = True

    return (scheme, netloc, path, params, query, fragment, is_url, is_absolute, is_blank)


def link_type(link):
    """Test if local file."""

    link_type = OTHER_LINK
    try:
        scheme, netloc, path, params, query, fragment, is_url, is_absolute, is_blank = parse_url(link)
        if is_url:
            link_type = URL_LINK
        elif is_blank:
            link_type = BLANK_LINK
        else:
            path = url2pathname(path).replace('\\', '/')
            # Adjust /c:/ to c:/.
            if scheme == 'file' and RE_SLASH_WIN_DRIVE.match(path):
                path = path[1:]

            file_name = os.path.normpath(path)
            if os.path.exists(file_name) and (file_name.lower().endswith('.html') or os.path.isdir(file_name)):
                link_type = HTML_LINK

    except Exception:
        # Parsing crashed and burned; no need to continue.
        pass
    return link_type


class WebViewMixin:
    """HTML `WebView`."""

    def setup_html(self, obj, control_title=None):
        """Setup HTML events."""

        # Setup busy tracker
        obj.busy = False
        obj.control_title = control_title

        # Setup events
        obj.Bind(wx.html2.EVT_WEBVIEW_NAVIGATING, functools.partial(self.on_navigate, obj=obj))
        obj.Bind(wx.html2.EVT_WEBVIEW_LOADED, functools.partial(self.on_html_loaded, obj=obj))
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
                content = convert_markdown(title, content)
            else:
                content = content
            obj.busy = True
            obj.SetPage(content, 'file://')
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
        ltype = link_type(url)
        if ltype == BLANK_LINK:
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
        elif ltype == HTML_LINK:
            obj.busy = True
        # Send URL links to browser
        elif ltype == URL_LINK:
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

    def on_html_loaded(self, event, obj=None):
        """Handle loaded event."""

        obj.busy = False
