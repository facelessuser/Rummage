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
import wx
import wx.lib.mixins.listctrl as listmix
import functools
from .. import util
from collections import OrderedDict
import locale
from ..settings import Settings
from .. util import rgba

MINIMUM_COL_SIZE = 100
COLUMN_SAMPLE_SIZE = 100
USE_SAMPLE_SIZE = True


def cmp(a, b):
    """Compare."""

    return (a > b) - (a < b)


class DummyLock:
    """A dummy lock that does nothing."""

    def __enter__(self):
        """Enter."""
        return self

    def __exit__(self, type, value, traceback):  # noqa: A002
        """Exit."""
        return True


class DynamicList(wx.ListCtrl, listmix.ColumnSorterMixin):
    """Dynamic list."""

    def __init__(self, parent, columns, single_sel=True, virtual_list=None):
        """Initialize the base class `DynamicList` object."""

        if virtual_list is None:
            virtual_list = []

        flags = wx.LC_REPORT | wx.LC_VIRTUAL

        if single_sel:
            flags |= wx.LC_SINGLE_SEL

        super().__init__(
            parent, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
            style=flags
        )
        if not single_sel:
            # Select all
            self.set_keybindings(
                [
                    (wx.ACCEL_CMD if util.platform() == "macos" else wx.ACCEL_CTRL, ord('A'), self.select_all)
                ]
            )
        self.Bind(wx.EVT_SYS_COLOUR_CHANGED, self.on_color_change)

        self.hidden_columns = set()
        self.main_window = self.GetParent().GetParent().GetParent().GetParent()
        self.sort_init = True
        self.complete = False
        self.resize_complete = False
        self.wait = DummyLock()
        self.column_count = len(columns)
        self.col2virt = {x: x for x in range(self.column_count)}
        self.virt2col = {v: k for k, v in self.col2virt.items()}
        self.setup_virtual(virtual_list)
        self.headers = columns
        self.itemDataMap = OrderedDict()
        self.first_resize = True
        self.size_sample = COLUMN_SAMPLE_SIZE
        self.widest_cell = [MINIMUM_COL_SIZE] * self.column_count
        self.dc = wx.ClientDC(self)
        self.dc.SetFont(self.GetFont())
        self.last_idx_sized = -1
        self.update_colors()
        self.setup_columns()
        self.itemIndexMap = []

    def update_colors(self):
        """Update colors."""

        bg = rgba.RGBA(self.GetBackgroundColour().Get())
        factor = 0.93 if bg.get_luminance() >= 127 else 1.07
        if Settings.get_alt_list_color():
            bg.brightness(factor)
        self.SetAlternateRowColour(wx.Colour(*bg.get_rgb()))
        self.create_image_list()
        self.Refresh()

    def on_color_change(self, event):
        """Handle color change."""

        self.update_colors()

        if event:
            event.Skip()

    def setup_virtual(self, virtual_list):
        """Setup virtual list."""

        virtual_list = [x for x in virtual_list if (0 <= x < self.column_count)]
        if len(virtual_list) != len(set(virtual_list)):
            new_list = []
            for x in virtual_list:
                if x not in new_list:
                    new_list.append(x)
            virtual_list = new_list
        if len(virtual_list) > self.column_count:
            virtual_list = [x for x in virtual_list if x < self.column_count]
        if len(virtual_list) < self.column_count - 1:
            for x in range(self.column_count):
                if x not in virtual_list:
                    virtual_list.append(x)

        for real, virt in enumerate(virtual_list, 0):
            self.col2virt[real] = virt
        self.virt2col = {v: k for k, v in self.col2virt.items()}
        self.virtual_list = virtual_list
        return virtual_list

    def update_virtual(self, virtual_list):
        """Update virtual."""

        self.complete = False
        column, order = self.GetSortState()
        if column != -1:
            column = self.get_real_col(column)

        old_widest = {}
        for virt, size in enumerate(self.widest_cell):
            old_widest[self.get_real_col(virt)] = size

        virtual_list = self.setup_virtual(virtual_list)
        for virt in range(self.column_count):
            self.widest_cell[virt] = old_widest[self.get_real_col(virt)]

        self.DeleteAllColumns()
        self.setup_columns()
        self.SetColumnCount(self.column_count)
        if column != -1:
            self.SortListItems(self.get_virt_col(column), order)
        self.Refresh()
        self.virtual_list = virtual_list
        self.complete = True
        return virtual_list

    def get_virt_col(self, index):
        """Get virtual column from real column."""

        return self.virt2col.get(index, index)

    def get_real_col(self, index):
        """Get real column from virtual column."""

        return self.col2virt.get(index, index)

    def set_hidden_columns(self, hidden):
        """Set hidden columns."""

        self.hidden_columns = set(hidden)
        for i in range(0, self.column_count):
            real = self.get_real_col(i)
            if real in self.hidden_columns:
                self.SetColumnWidth(i, 0)
            elif self.GetColumnWidth(i) == 0:
                self.SetColumnWidth(i, MINIMUM_COL_SIZE)

    def destroy(self):
        """Destroy."""

        self.dc.Destroy()

    def set_keybindings(self, keybindings=None):
        """
        Method to easily set key bindings.

        Also sets up debug key bindings and events.
        """

        if keybindings is None:
            keybindings = []

        # Add key bindings.
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
        last_column = -1
        for i in range(0, self.column_count):
            w = self.GetColumnWidth(i)
            total_width += w
            last_width = w
            if w > 0:
                last_column = i

        if total_width < (self.GetSize()[0] - 20) and last_column > -1:
            self.SetColumnWidth(last_column, last_width + self.GetSize()[0] - total_width)

    def setup_columns(self):
        """Setup columns."""

        for x in range(0, self.column_count):
            real = self.get_real_col(x)
            lw = self.dc.GetFullTextExtent(self.headers[real])[0]
            width = lw + 30
            if width > self.widest_cell[x]:
                self.widest_cell[x] = width
            self.InsertColumn(x, self.headers[real])
        for i in range(0, self.column_count):
            real = self.get_real_col(i)
            if real not in self.hidden_columns:
                self.SetColumnWidth(i, self.widest_cell[i])
            else:
                self.SetColumnWidth(i, 0)

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

        return self.itemDataMap[self.itemIndexMap[idx] if not absolute else idx][self.get_real_col(col)]

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
        self.SetColumnCount(self.column_count)
        self.setup_columns()
        self.Refresh()

    def load_list(self, last=False):
        """Load the list of items from the item map."""

        self.SetItemCount(len(self.itemDataMap))
        if not self.resize_complete:
            for i in range(0, self.column_count):
                real = self.get_real_col(i)
                if real not in self.hidden_columns:
                    self.SetColumnWidth(i, self.widest_cell[i])
                else:
                    self.SetColumnWidth(i, 0)
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

        return util.to_ustr(self.itemDataMap[self.itemIndexMap[idx] if not absolute else idx][self.get_real_col(col)])

    def GetSecondarySortValues(self, col, key1, key2):
        """
        Get secondary sort values.

        Virtual columns are handled in `__ColumnSorter`.
        """

        sscol = 1 if col == 0 else 0
        return (self.itemDataMap[key1][sscol], self.itemDataMap[key2][sscol])

    def GetColumnSorter(self):
        """Returns a callable object to be used for comparing column values when sorting."""

        return self._custom_sorter

    def _custom_sorter(self, key1, key2):
        """Custom virtual columns sorter."""

        col = self._col
        ascending = self._colSortFlag[col]
        real = self.get_real_col(col)
        item1 = self.itemDataMap[key1][real]
        item2 = self.itemDataMap[key2][real]

        # Internationalization of string sorting with locale module
        if isinstance(item1, str) and isinstance(item2, str):
            cmpVal = locale.strcoll(item1, item2)
        elif isinstance(item1, bytes) or isinstance(item2, bytes):
            cmpVal = locale.strcoll(str(item1), str(item2))
        else:
            cmpVal = cmp(item1, item2)

        # If the items are equal, then pick something else to make the sort value unique
        if cmpVal == 0:
            cmpVal = cmp(*self.GetSecondarySortValues(col, key1, key2))

        if ascending:
            return cmpVal
        else:
            return -cmpVal

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

    def OnGetItemImage(self, item):
        """Override method to get the image for the given item."""

        return 0

    def GetSortImages(self):
        """Override method to provide sort images in column headers."""

        return self.sort_down, self.sort_up

    def GetListCtrl(self):
        """Get `ListCtrl` object (self)."""

        return self
