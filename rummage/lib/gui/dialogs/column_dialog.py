"""
Columns dialog.

Licensed under MIT
Copyright (c) 2017 Isaac Muse <isaacmuse@gmail.com>

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


class ColumnDialog(gui.ColumnDialog):
    """Columns dialog."""

    def __init__(self, parent, columns, headers):
        """Initialize search chain dialog object."""

        super().__init__(parent)
        self.localize()
        self.refresh_localization()

        self.columns = columns
        self.headers = headers
        self.load_columns(columns, headers)

        # Ensure good sizing of frame
        self.m_column_list.SetMinSize(wx.Size(-1, 200))
        self.m_column_panel.Fit()
        self.Fit()
        self.SetMinSize(self.GetSize())
        self.Centre()

        self.m_column_list.SetFocus()
        self.changed = False

    def localize(self):
        """Translate strings."""

        self.TITLE = _("Arrange Columns")
        self.UP = _("Up")
        self.DOWN = _("Down")
        self.OKAY = _("Apply")
        self.CLOSE = _("Cancel")

    def refresh_localization(self):
        """Localize."""

        self.SetTitle(self.TITLE)
        self.m_up_button.SetLabel(self.UP)
        self.m_down_button.SetLabel(self.DOWN)
        self.m_apply_button.SetLabel(self.OKAY)
        self.m_cancel_button.SetLabel(self.CLOSE)

    def get_virt_col(self, index):
        """Get virtual column from real column."""

        return self.virt2col[index]

    def get_real_col(self, index):
        """Get real column from virtual column."""

        return self.col2virt[index]

    def load_columns(self, columns, headers):
        """Populate list with column entries."""

        self.col2virt = {}
        self.virtual_columns = columns
        for virt, real in enumerate(columns):
            self.col2virt[real] = virt
        self.virt2col = {virt: real for real, virt in self.col2virt.items()}
        for virt, real in enumerate(self.virtual_columns):
            self.m_column_list.Insert(self.headers[real], virt)

    def on_up_click(self, event):
        """Move up."""

        index = self.m_column_list.GetSelection()
        if index > 0:
            search = self.m_column_list.GetString(index)
            self.m_column_list.Delete(index)
            self.m_column_list.Insert(search, index - 1)
            self.m_column_list.Select(index - 1)
            current = self.virt2col[index]
            previous = self.virt2col[index - 1]
            self.virt2col[index - 1] = current
            self.virt2col[index] = previous
            self.col2virt = {real: virt for virt, real in self.virt2col.items()}

    def on_down_click(self, event):
        """Move up."""

        count = self.m_column_list.GetCount()
        index = self.m_column_list.GetSelection()
        if wx.NOT_FOUND < index < count - 1:
            search = self.m_column_list.GetString(index)
            self.m_column_list.Delete(index)
            self.m_column_list.Insert(search, index + 1)
            self.m_column_list.Select(index + 1)
            current = self.virt2col[index]
            forward = self.virt2col[index + 1]
            self.virt2col[index + 1] = current
            self.virt2col[index] = forward
            self.col2virt = {real: virt for virt, real in self.virt2col.items()}

    def on_apply_click(self, event):
        """Add new chain."""

        length = len(self.virtual_columns)
        self.virtual_columns = []
        for virt in range(length):
            self.virtual_columns.append(self.virt2col[virt])
        self.changed = True
        self.Close()

    def on_cancel_click(self, event):
        """Close window."""

        self.Close()
