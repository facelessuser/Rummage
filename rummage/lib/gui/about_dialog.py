"""
About Dialog.

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
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
from __future__ import unicode_literals
import wx
from . import gui
from . import data
from .localization import _
from .. import __meta__


class AboutDialog(gui.AboutDialog):
    """About Dialog."""

    def __init__(self, parent):
        """Initialize the AboutDialog object."""

        super(AboutDialog, self).__init__(parent)
        self.localize()

        self.m_bitmap = wx.StaticBitmap(
            self.m_about_panel,
            wx.ID_ANY,
            data.get_bitmap('rummage_dialog.png'),
            wx.DefaultPosition,
            wx.Size(64, 64), 0
        )

        self.refresh_localization()
        self.Fit()

    def localize(self):
        """Translate strings."""

        self.TITLE = _("About")
        self.CONTACT = _("Contact")
        self.VERSION = _("Version: %s %s")
        self.DEVELOPER = _("Developer(s):\n%s")

    def refresh_localization(self):
        """Localize."""

        self.SetTitle(self.TITLE)
        self.m_app_label.SetLabel(__meta__.__app__)
        self.m_version_label.SetLabel(
            self.VERSION % (__meta__.__version__, __meta__.__status__)
        )
        self.m_developers_label.SetLabel(
            self.DEVELOPER % ("\n".join(["    %s - %s" % (m[0], m[1]) for m in __meta__.__maintainers__]))
        )
        self.m_dev_toggle.SetLabel(self.CONTACT + " >>")

    def on_toggle(self, event):
        """Show/hide contact info on when contact button is toggled."""

        if self.m_dev_toggle.GetValue():
            self.m_dev_toggle.SetLabel(self.CONTACT + " <<")
            self.m_developers_label.Show()
        else:
            self.m_dev_toggle.SetLabel(self.CONTACT + " >>")
            self.m_developers_label.Hide()
        self.Fit()
        self.Refresh()
