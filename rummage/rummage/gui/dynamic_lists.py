"""
Dynamic lists.

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
from __future__ import unicode_literals
import wx
import wx.lib.mixins.listctrl as listmix
from .. import util

MINIMUM_COL_SIZE = 100
COLUMN_SAMPLE_SIZE = 100
USE_SAMPLE_SIZE = True


class DynamicList(wx.ListCtrl, listmix.ColumnSorterMixin):
    """Dynamic list."""

    def __init__(self, parent, columns):
        """Init the base class DynamicList object."""

        super(DynamicList, self).__init__(
            parent, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
            style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_VIRTUAL
        )
        self.sort_init = True
        self.column_count = len(columns)
        self.headers = columns
        self.itemDataMap = {}
        self.first_resize = True
        self.size_sample = COLUMN_SAMPLE_SIZE
        self.widest_cell = [MINIMUM_COL_SIZE] * self.column_count
        self.attr1 = wx.ListItemAttr()
        self.attr1.SetBackgroundColour(wx.Colour(0xEE, 0xEE, 0xEE))
        self.dc = wx.ClientDC(self)
        self.dc.SetFont(self.GetFont())
        self.last_idx_sized = -1
        self.create_image_list()

    def resize_last_column(self):
        """Resize the last column."""

        total_width = 0
        last_width = 0
        for i in range(0, self.column_count):
            total_width += self.GetColumnWidth(i)
            if i == self.column_count - 1:
                last_width = self.GetColumnWidth(i)
        if total_width < self.GetSize()[0] - 20:
            self.SetColumnWidth(self.column_count - 1, last_width + self.GetSize()[0] - total_width)

    def init_column_size(self):
        """Setup the initial column size."""

        for i in range(0, self.column_count):
            self.SetColumnWidth(i, self.widest_cell[i])
        self.resize_last_column()
        self.size_sample = 0

    def get_column_count(self):
        """Get column count."""

        return self.column_count

    def set_item_map(self, idx, *args):
        """Set new entry in item map."""

        self.itemDataMap[idx] = tuple([a for a in args])
        # Sample the first "size_sample" to determine
        # column width for when table first loads
        if self.size_sample or not USE_SAMPLE_SIZE:
            for x in range(0, self.column_count):
                text = self.get_item_text(idx, x, True)
                lw = self.dc.GetFullTextExtent(text)[0]
                width = lw + 30
                if width > self.widest_cell[x]:
                    self.widest_cell[x] = width
            self.last_idx_sized = idx
            self.size_sample -= 1

    def get_map_item(self, idx, col=0, absolute=False):
        """Get attribute in in item map entry and the given index."""

        return self.itemDataMap[self.itemIndexMap[idx] if not absolute else idx][col]

    def reset_list(self):
        """Reset the list."""

        self.ClearAll()
        self.itemDataMap = {}
        self.SetItemCount(0)
        self.size_sample = COLUMN_SAMPLE_SIZE
        self.widest_cell = [MINIMUM_COL_SIZE] * self.column_count
        self.Refresh()

    def load_list(self):
        """Load the list of items from the item map."""

        for x in range(0, self.column_count):
            self.InsertColumn(x, self.headers[x])
        self.SetItemCount(len(self.itemDataMap))
        if self.sort_init:
            listmix.ColumnSorterMixin.__init__(self, self.column_count)
            self.sort_init = False
        self.SortListItems(col=0, ascending=1)
        self.init_column_size()

    def GetSecondarySortValues(self, col, key1, key2):
        """Get secondary sort values."""

        sscol = 1 if col == 0 else 0
        return (self.itemDataMap[key1][sscol], self.itemDataMap[key2][sscol])

    def SortItems(self, sorter=None):
        """Sort items."""

        items = list(self.itemDataMap.keys())
        if sorter is not None:
            util.sorted_callback(items, sorter)
        else:
            items.sort()
        self.itemIndexMap = items

        # redraw the list
        self.Refresh()

    def OnGetItemText(self, item, col):
        """Override method to return the text for the given item and col."""

        return self.get_item_text(item, col)

    def get_item_text(self, idx, col, absolute=False):
        """Return the text for the given item and col."""

        return util.to_ustr(self.itemDataMap[self.itemIndexMap[idx] if not absolute else idx][col])

    def OnGetItemAttr(self, item):
        """Override method to get attributes for the cells in the given item."""

        if item % 2 == 0:
            return self.attr1
        return None

    def OnGetItemImage(self, item):
        """Override method to get the image for the given item."""

        return 0

    def GetSortImages(self):
        """Override method to provide sort images in column headers."""

        return self.sort_down, self.sort_up

    def GetListCtrl(self):
        """Get ListCtrl object (self)."""

        return self
