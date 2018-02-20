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
import functools
from ... import util
from collections import OrderedDict

MINIMUM_COL_SIZE = 100
COLUMN_SAMPLE_SIZE = 100
USE_SAMPLE_SIZE = True


class DummyLock(object):
    """A dummy lock that does nothing."""

    def __enter__(self):
        """Enter."""
        return self

    def __exit__(self, type, value, traceback):  # noqa: A002
        """Exit."""
        return True


class DynamicList(wx.ListCtrl, listmix.ColumnSorterMixin):
    """Dynamic list."""

    def __init__(self, parent, columns, single_sel=True):
        """Init the base class DynamicList object."""

        flags = wx.LC_REPORT | wx.LC_VIRTUAL

        if single_sel:
            flags |= wx.LC_SINGLE_SEL

        super(DynamicList, self).__init__(
            parent, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
            style=flags
        )
        if not single_sel:
            # Select all
            self.set_keybindings(
                [
                    (wx.ACCEL_CMD if util.platform() == "osx" else wx.ACCEL_CTRL, ord('A'), self.select_all)
                ]
            )

        self.main_window = self.GetParent().GetParent().GetParent().GetParent()
        self.sort_init = True
        self.complete = False
        self.resize_complete = False
        self.wait = DummyLock()
        self.column_count = len(columns)
        self.headers = columns
        self.itemDataMap = OrderedDict()
        self.first_resize = True
        self.size_sample = COLUMN_SAMPLE_SIZE
        self.widest_cell = [MINIMUM_COL_SIZE] * self.column_count
        self.attr1 = wx.ListItemAttr()
        self.attr1.SetBackgroundColour(wx.Colour(0xEE, 0xEE, 0xEE))
        self.dc = wx.ClientDC(self)
        self.dc.SetFont(self.GetFont())
        self.last_idx_sized = -1
        self.create_image_list()
        self.setup_columns()
        self.itemIndexMap = []

    def destroy(self):
        """Destroy."""

        self.dc.Destroy()

    def set_keybindings(self, keybindings=None):
        """
        Method to easily set key bindings.

        Also sets up debug keybindings and events.
        """

        if keybindings is None:
            keybindings = []

        # Add keybindings.
        tbl = []
        bindings = keybindings
        for binding in keybindings:
            keyid = wx.NewId()
            self.Bind(wx.EVT_MENU, binding[2], id=keyid)
            tbl.append((binding[0], binding[1], keyid))

        if len(bindings):
            self.SetAcceleratorTable(wx.AcceleratorTable(tbl))

    def select_all(self, event):
        """Select all items."""

        with self.wait:
            item = self.GetNextItem(-1)
            while item != -1:
                if not self.IsSelected(item):
                    self.Select(item)
                item = self.GetNextItem(item)
        event.Skip()

    def deselect_all(self, event):
        """Deselect all items."""

        with self.wait:
            item = self.GetNextItem(-1)
            while item != -1:
                if self.IsSelected(item):
                    self.Select(item, False)
                item = self.GetNextItem(item)
        if event:
            event.Skip()

    def set_wait_lock(self, wait_lock):
        """Set wait lock."""

        self.wait = wait_lock

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

    def setup_columns(self):
        """Setup columns."""

        for x in range(0, self.column_count):
            self.InsertColumn(x, self.headers[x])
        for i in range(0, self.column_count):
            self.SetColumnWidth(i, self.widest_cell[i])

    def get_column_count(self):
        """Get column count."""

        return self.column_count

    def set_item_map(self, idx, *args):
        """Set new entry in item map."""

        self.itemDataMap[idx] = tuple([a for a in args])
        self.itemIndexMap.append(idx)
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
        self.complete = False
        self.resize_complete = False
        self.itemDataMap = OrderedDict()
        self.itemIndexMap = []
        self.SetItemCount(0)
        self.size_sample = COLUMN_SAMPLE_SIZE
        self.widest_cell = [MINIMUM_COL_SIZE] * self.column_count
        self.setup_columns()
        self.Refresh()

    def load_list(self, last=False):
        """Load the list of items from the item map."""

        self.SetItemCount(len(self.itemDataMap))
        if not self.resize_complete:
            for i in range(0, self.column_count):
                self.SetColumnWidth(i, self.widest_cell[i])
            if not self.size_sample:
                self.resize_complete = True
        if last:
            if self.sort_init:
                listmix.ColumnSorterMixin.__init__(self, self.column_count)
                self.sort_init = False
            self.resize_last_column()
            self.size_sample = 0
            self.complete = True

    def get_item_text(self, idx, col, absolute=False):
        """Return the text for the given item and col."""

        return util.to_ustr(self.itemDataMap[self.itemIndexMap[idx] if not absolute else idx][col])

    def GetSecondarySortValues(self, col, key1, key2):
        """Get secondary sort values."""

        sscol = 1 if col == 0 else 0
        return (self.itemDataMap[key1][sscol], self.itemDataMap[key2][sscol])

    def SortItems(self, sorter=None):
        """Sort items."""

        with self.wait:
            if sorter is not None:
                self.itemIndexMap.sort(key=functools.cmp_to_key(sorter))
            else:
                self.itemIndexMap.sort()

            # redraw the list
            self.Refresh()

    def OnGetItemText(self, item, col):
        """Override method to return the text for the given item and col."""

        return self.get_item_text(item, col)

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
