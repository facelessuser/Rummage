"""
Support Information Dialog.

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
from .. import util
import textwrap
import platform
import sys
from .. import __meta__


def list2string(obj):
    """Convert list to string."""

    return '.'.join([str(x) for x in obj])


def format_version(module, attr, call=False):
    """Format the version."""

    try:
        if call:
            version = getattr(module, attr)()
        else:
            version = getattr(module, attr)
    except Exception as e:
        print(e)
        version = 'Version could not be acquired!'

    if not isinstance(version, str):
        version = list2string(version)
    return version


class SupportInfoDialog(gui.SupportInfoDialog):
    """SettingsDialog."""

    def __init__(self, parent):
        """Init SettingsDialog object."""

        super(SupportInfoDialog, self).__init__(parent)
        if util.platform() == "windows":
            self.m_support_panel.SetDoubleBuffered(True)
        self.localize()
        self.refresh_localization()

        self.m_support_panel.Fit()
        self.Fit()
        if self.GetSize()[1] < 300:
            self.SetSize(wx.Size(300, self.GetSize()[1]))
        self.SetMinSize(wx.Size(300, self.GetSize()[1]))

        self.display_support_information()

    def localize(self):
        """Translage strings."""

        self.TITLE = _("Support Info")
        self.CLOSE = _("Close")

    def refresh_localization(self):
        """Localize dialog."""

        self.SetTitle(self.TITLE)
        self.m_cancel_button.SetLabel(self.CLOSE)
        self.Fit()

    def on_copy(self, event):
        """Handle copy event."""

        if wx.TheClipboard.Open():
            try:
                wx.TheClipboard.SetData(wx.TextDataObject(self.info))
            except Exception:
                pass
            wx.TheClipboard.Close()

    def on_cancel(self, event):
        """Close dialog."""

        self.Close()

    def display_support_information(self):
        """Display the support information."""

        info = {
            "arch": "64bit" if sys.maxsize > 2**32 else "32bit",
            "platform": util.platform(),
            "python": format_version(platform, "python_version_tuple", True),
            "wxpython": wx.version(),
            "rummage": format_version(__meta__, "__version__"),
            "status": __meta__.__status__,
            "py_type": platform.python_implementation()
        }

        try:
            import backrefs
            info["backrefs"] = format_version(backrefs, 'version')
        except Exception:
            info["backrefs"] = 'Version could not be acquired!'

        try:
            import regex
            info["regex"] = format_version(regex, '__version__')
        except Exception:
            info["regex"] = 'Version could not be acquired!'

        try:
            import chardet
            info["chardet"] = format_version(chardet, '__version__')
        except Exception:
            info["chardet"] = 'Version could not be acquired!'

        try:
            import cchardet
            info["cchardet"] = format_version(cchardet.version, '__version__')
        except Exception:
            info["cchardet"] = 'Version could not be acquired!'

        try:
            import filelock
            info["filelock"] = format_version(filelock, '__version__')
        except Exception:
            info["filelock"] = 'Version could not be acquired!'

        try:
            import gntp.version
            info["gntp"] = format_version(gntp.version, '__version__')
        except Exception:
            info["gntp"] = 'Version could not be acquired!'

        self.info = textwrap.dedent(
            """\
            - Arch: %(arch)s
            - Platform: %(platform)s
            - Python: %(python)s (%(py_type)s)
            - Rummage: %(rummage)s %(status)s
            - WxPython: %(wxpython)s
            - Backrefs: %(backrefs)s
            - Chardet: %(chardet)s
            - cChardet: %(cchardet)s
            - Regex: %(regex)s
            - Filelock: %(filelock)s
            - Gntp: %(gntp)s
            """ % info
        )

        self.m_info_textbox.SetValue(self.info)
