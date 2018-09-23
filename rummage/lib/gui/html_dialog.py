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
import re
from urllib.request import url2pathname
from urllib.parse import urlparse
import html

RE_WIN_DRIVE_LETTER = re.compile(r"^[A-Za-z]$")
RE_WIN_DRIVE_PATH = re.compile(r"^[A-Za-z]:(?:\\.*)?$")
RE_SLASH_WIN_DRIVE = re.compile(r"^/[A-Za-z]{1}:/.*")
RE_URL = re.compile('(http|ftp)s?|data|mailto|tel|news')

URL_LINK = 0
HTML_LINK = 1
OTHER_LINK = 2


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
    scheme, netloc, path, params, query, fragment = urlparse(html.unescape(url))

    if RE_URL.match(scheme):
        # Clearly a url
        is_url = True
    elif scheme == '' and netloc == '' and path == '':
        # Maybe just a url fragment
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
        # A non-filepath or strange url
        is_url = True
    elif path.startswith(('/', '\\')):
        # /root path
        is_absolute = True

    return (scheme, netloc, path, params, query, fragment, is_url, is_absolute)


def link_type(link):
    """Test if local file."""

    link_type = OTHER_LINK
    try:
        scheme, netloc, path, params, query, fragment, is_url, is_absolute = parse_url(link)
        if is_url:
            link_type = URL_LINK
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


class HTMLDialog(gui.HtmlDialog):
    """HTMLDialog."""

    def __init__(self, parent, content, title=None, string=False):
        """Init SettingsDialog object."""

        super(HTMLDialog, self).__init__(parent)
        self.localize()
        self.m_content_html.Bind(wx.html2.EVT_WEBVIEW_NAVIGATING, self.on_navigate)
        self.load(content, title, string)
        self.Fit()

    def load(self, content, title=None, string=False):
        """Reshow the dialog."""

        if title is None:
            self.title = self.TITLE
        else:
            self.title = title
        self.refresh_localization()
        self.load_html(content, string)

    def localize(self):
        """Translage strings."""

        self.TITLE = _("Untitled")

    def refresh_localization(self):
        """Localize dialog."""

        self.SetTitle(self.title)
        self.Fit()

    def load_html(self, content, string):
        """Load HTML."""

        if not string:
            url = 'file://%s' % os.path.join(data.RESOURCE_PATH, 'docs', content).replace('\\', '/')
            while self.m_content_html.IsBusy():
                pass
            self.m_content_html.LoadURL(url)
        else:
            # We may not even use this
            pass

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
        ltype = link_type(url)
        if ltype == HTML_LINK:
            pass
        # Send URL links to browser
        elif ltype == URL_LINK:
            webbrowser.open_new_tab(url)
            event.Veto()
        # Handle webkit id jumps for IE (usually when handling HTML strings, not files)
        elif url.startswith('about:blank#'):
            script = "document.getElementById('%s').scrollIntoView();" % url.replace('about:blank#', '')
            debug("HTML Nav ID: " + script)
            self.m_content_html.RunScript(script)
            event.Veto()
        # Show unhandled links
        else:
            debug("HTML unhandled link: " + url)
            event.Veto()
