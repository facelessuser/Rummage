"""
About Dialog

Licensed under MIT
Copyright (c) 2013 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import wx
import version
import _gui.gui as gui
from _icons.rum_ico import rum_64


class AboutDialog(gui.AboutDialog):
    def __init__(self, parent):
        """
        Initialize the AboutDialog object
        """

        super(AboutDialog, self).__init__(parent)

        self.m_bitmap = wx.StaticBitmap(
            self.m_about_panel, wx.ID_ANY, rum_64.GetBitmap(), wx.DefaultPosition, wx.Size(64, 64), 0
        )
        self.m_app_label.SetLabel(version.app)
        self.m_version_label.SetLabel(
            "Version: %s %s" % (version.version, version.status)
        )
        self.m_developers_label.SetLabel(
            "Developers(s):\n%s" % ("\n".join(["    %s - %s" % (m[0], m[1]) for m in version.maintainers]))
        )
        self.Fit()

    def on_toggle(self, event):
        """
        Show\hide contact info on when contact button is toggled
        """

        if self.m_dev_toggle.GetValue():
            self.m_dev_toggle.SetLabel("Contact <<")
            self.m_developers_label.Show()
        else:
            self.m_dev_toggle.SetLabel("Contact >>")
            self.m_developers_label.Hide()
        self.Fit()
