"""
Overwrite Dialog.

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
import wx
import sys
from ..localization import _
from .. import gui
from .msg_dialogs import prompt_icon, DEFAULT_ICON_SIZE


class OverwriteDialog(gui.OverwriteDialog):
    """Overwrite dialog."""

    def __init__(self, parent, msg=None):
        """Initialize overwrite dialog."""

        super().__init__(parent)

        self.action = False
        self.remember = False
        if sys.platform == "darwin":
            bm = prompt_icon.GetBitmap()
            bm.SetHeight(DEFAULT_ICON_SIZE)
            bm.SetWidth(DEFAULT_ICON_SIZE)
        else:
            scaled = prompt_icon.GetImage().Rescale(DEFAULT_ICON_SIZE, DEFAULT_ICON_SIZE)
            bm = scaled.ConvertToBitmap()

        self.m_bitmap = wx.StaticBitmap(
            self.m_overwrite_panel,
            wx.ID_ANY,
            bm,
            wx.DefaultPosition,
            wx.Size(DEFAULT_ICON_SIZE, DEFAULT_ICON_SIZE), 0
        )

        self.localize(msg)
        self.refresh_localization()

        self.m_overwrite_panel.Layout()
        self.m_overwrite_panel.Fit()
        self.Fit()
        self.SetMinSize(self.GetSize())
        self.Centre()

    def localize(self, msg):
        """Translate strings."""

        self.TITLE = _("Overwrite")
        self.MSG = _("Overwrite?") if msg is None else msg
        self.OVERWRITE = _("Overwrite")
        self.SKIP = _("Skip")
        self.APPLY = _("Apply to all")

    def refresh_localization(self):
        """Localize dialog."""

        self.SetTitle(self.TITLE)
        self.m_message_label.SetLabel(self.MSG)
        self.m_remember_checkbox.SetLabel(self.APPLY)
        self.m_overwrite_button.SetLabel(self.OVERWRITE)
        self.m_cancel_button.SetLabel(self.SKIP)
        self.Fit()

    def on_overwrite(self, event):
        """Handle on overwrite."""

        self.action = True
        self.remember = self.m_remember_checkbox.GetValue()
        self.Close()

    def on_skip(self, event):
        """Handle on skip."""

        self.action = False
        self.remember = self.m_remember_checkbox.GetValue()
        self.Close()
