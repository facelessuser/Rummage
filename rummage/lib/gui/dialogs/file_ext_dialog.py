"""
File Ext Dialog.

Licensed under MIT
Copyright (c) 2013 - 2018 Isaac Muse <isaacmuse@gmail.com>

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
from ..localization import _
from .. import gui


class FileExtDialog(gui.FileExtDialog):
    """File extension dialog."""

    def __init__(self, parent, extensions):
        """Initialize dialog."""

        super().__init__(parent)

        self.extensions = extensions
        self.localize()
        self.refresh_localization()
        self.m_ext_textbox.SetValue(self.extensions)

        self.m_ext_panel.Layout()
        self.m_ext_panel.Fit()
        self.Fit()

        if self.GetSize()[0] < 500:
            self.SetSize(wx.Size(500, self.GetSize()[1]))
        self.SetMinSize(wx.Size(500, self.GetSize()[1]))
        self.SetMinSize(self.GetSize())
        self.Centre()

    def localize(self):
        """Translate strings."""

        self.TITLE = _("File Extension")
        self.EXTENSIONS = _("Extensions")
        self.OKAY = _("Save")
        self.CANCEL = _("Cancel")

    def refresh_localization(self):
        """Localize dialog."""

        self.SetTitle(self.TITLE)
        self.m_ext_label.SetLabel(self.EXTENSIONS)
        self.m_okay_button.SetLabel(self.OKAY)
        self.m_cancel_button.SetLabel(self.CANCEL)
        self.Fit()

    def on_okay_click(self, event):
        """Handle on overwrite."""

        value = self.m_ext_textbox.GetValue()
        new_items = []
        for item in value.split(','):
            item = item.strip()
            if item:
                if not item.startswith('.'):
                    item = '.' + item
                new_items.append(item)

        self.extensions = ', '.join(new_items)

        self.Close()

    def on_cancel_click(self, event):
        """Handle on skip."""

        self.Close()
