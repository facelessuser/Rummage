"""
Encoding list.

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
from .dynamic_lists import DynamicList
from ..localization import _
from .. import data


class EncodingList(DynamicList):
    """Encoding list."""

    def __init__(self, parent):
        """Initialization."""

        self.localize()

        super(EncodingList, self).__init__(
            parent,
            [
                self.FILE_TYPE,
                self.EXTENSIONS
            ]
        )

    def localize(self):
        """Translate strings."""

        self.FILE_TYPE = _("File type")
        self.EXTENSIONS = _("Extensions")

    def create_image_list(self):
        """Create image list."""

        self.images = wx.ImageList(16, 16)
        self.doc = self.images.Add(data.get_bitmap('doc.png'))
        self.bin = self.images.Add(data.get_bitmap('binary.png'))
        self.sort_up = self.images.Add(data.get_bitmap('arrow_up.png', tint=data.RGBA(0x33, 0x33, 0x33, 0xFF)))
        self.sort_down = self.images.Add(data.get_bitmap('arrow_down.png', tint=data.RGBA(0x33, 0x33, 0x33, 0xFF)))
        self.AssignImageList(self.images, wx.IMAGE_LIST_SMALL)

    def get_item_text(self, item, col, absolute=False):
        """Return the text for the given item and col."""

        if not absolute:
            item = self.itemIndexMap[item]
        return self.itemDataMap[item][self.get_real_col(col)]

    def OnGetItemImage(self, item):
        """Override method to get the image for the given item."""

        return self.bin if self.itemIndexMap[item] == 'bin' else self.doc
