"""
Search error list.

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
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.
"""
import wx
from .dynamic_lists import DynamicList
from ..localization import _
from .. import data


class ErrorList(DynamicList):
    """Error list."""

    def __init__(self, parent):
        """Initialization."""

        self.localize()

        super().__init__(
            parent,
            [
                self.ERROR,
                self.FILE_NAME
            ]
        )

        self.Bind(wx.EVT_LEFT_DCLICK, self.on_dclick)

    def localize(self):
        """Translate strings."""

        self.ERROR = _("Error")
        self.FILE_NAME = _("File Name")

    def create_image_list(self):
        """Create image list."""

        self.images = wx.ImageList(16, 16)
        self.tint = data.RGBA(self.GetForegroundColour().Get()[:3])
        self.error_symbol = self.images.Add(data.get_bitmap('error.png'))
        self.sort_up = self.images.Add(data.get_bitmap('arrow_up.png', tint=self.tint, alpha=0.3))
        self.sort_down = self.images.Add(data.get_bitmap('arrow_down.png', tint=self.tint, alpha=0.3))
        self.AssignImageList(self.images, wx.IMAGE_LIST_SMALL)

    def get_item_text(self, item, col, absolute=False):
        """Return the text for the given item and col."""

        real = self.get_real_col(col)
        if not absolute:
            item = self.itemIndexMap[item]
        if real == 0:
            return self.itemDataMap[item][real][0]
        else:
            return self.itemDataMap[item][real]

    def on_dclick(self, event):
        """Open file at in editor with optional line and column argument."""

        pos = event.GetPosition()
        item = self.HitTestSubItem(pos)[0]
        if item != -1:
            file_name = self.get_map_item(item, col=self.get_virt_col(1))
            full_error = ''.join(reversed(self.get_map_item(item, col=self.get_virt_col(0))))
            self.GetParent().GetParent().show_error("%s\n%s" % (file_name, full_error))
        event.Skip()
