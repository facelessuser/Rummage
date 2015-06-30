"""
Result Panels.

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
from time import ctime
import wx
import wx.lib.mixins.listctrl as listmix
from os.path import normpath, join, basename, dirname
from .open_editor import open_editor
from ..localization import _
from .. import data

MINIMUM_COL_SIZE = 100
COLUMN_SAMPLE_SIZE = 100
USE_SAMPLE_SIZE = True


class ResultList(wx.ListCtrl, listmix.ColumnSorterMixin):

    """Result list."""

    def __init__(self, parent, columns):
        """Init the base class ResultList object."""

        super(ResultList, self).__init__(
            parent, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
            style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_VIRTUAL
        )
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

        self.images = wx.ImageList(16, 16)
        self.doc = self.images.Add(data.get_image('doc.png').GetBitmap())
        self.bin = self.images.Add(data.get_image('binary.png').GetBitmap())
        self.sort_up = self.images.Add(data.get_image('su.png').GetBitmap())
        self.sort_down = self.images.Add(data.get_image('sd.png').GetBitmap())
        self.SetImageList(self.images, wx.IMAGE_LIST_SMALL)

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
                lw, lh, d, e = self.dc.GetFullTextExtent(text)
                width = lw + 30
                if width > self.widest_cell[x]:
                    self.widest_cell[x] = width
            self.last_idx_sized = idx
            self.size_sample -= 1

    def get_map_item(self, idx, col=0, absolute=False):
        """Get attribute in in item map entry and the given index."""

        return self.itemDataMap[self.itemIndexMap[idx] if not absolute else idx][col]

    def load_list(self):
        """Load the list of items from the item map."""

        for x in range(0, self.column_count):
            self.InsertColumn(x, self.headers[x])
        self.SetItemCount(len(self.itemDataMap))
        listmix.ColumnSorterMixin.__init__(self, self.column_count)
        self.SortListItems(col=0, ascending=1)
        self.init_column_size()

    def SortItems(self, sorter=cmp):
        """Sort items."""

        items = list(self.itemDataMap.keys())
        items.sort(sorter)
        self.itemIndexMap = items

        # redraw the list
        self.Refresh()

    def OnGetItemText(self, item, col):
        """Override method to return the text for the given item and col."""

        return self.get_item_text(item, col)

    def get_item_text(self, idx, col, absolute=False):
        """Return the text for the given item and col."""

        return unicode(self.itemDataMap[self.itemIndexMap[idx] if not absolute else idx][col])

    def OnGetItemAttr(self, item):
        """Override method to get attributes for the cells in the given item."""

        if item % 2 == 0:
            return self.attr1
        return -1

    def OnGetItemImage(self, item):
        """Override method to get the image for the given item."""

        return 0

    def GetSortImages(self):
        """Override method to provide sort images in column headers."""

        return self.sort_down, self.sort_up

    def GetListCtrl(self):
        """Get ListCtrl object (self)."""

        return self


class ResultFileList(ResultList):

    """ResultFileList."""

    def __init__(self, parent):
        """Init ResultFileList object."""

        super(ResultFileList, self).__init__(
            parent,
            [
                _("File"),
                _("Size"),
                _("Matches"),
                _("Path"),
                _("Encoding"),
                _("Modified"),
                _("Created")
            ]
        )
        self.last_moused = (-1, "")
        self.Bind(wx.EVT_LEFT_DCLICK, self.on_dclick)
        self.Bind(wx.EVT_MOTION, self.on_motion)
        self.Bind(wx.EVT_ENTER_WINDOW, self.on_enter_window)

    def set_match(self, obj):
        """Set match."""

        item_id = "%d" % obj.info.id
        if item_id in self.itemDataMap:
            self.increment_match_count(item_id)
        else:
            self.set_item_map(
                item_id,
                basename(obj.info.name), float(obj.info.size.strip("KB")), 1,
                dirname(obj.info.name), obj.info.encoding, obj.info.modified,
                obj.info.created, obj.match.lineno, obj.match.colno
            )

    def on_enter_window(self, event):
        """Reset last moused over item tracker on mouse entering the window."""

        self.last_moused = (-1, "")
        event.Skip()

    def on_motion(self, event):
        """Display full file path in status bar on item mouseover."""

        pos = event.GetPosition()
        item = self.HitTestSubItem(pos)[0]
        if item != -1:
            actual_item = self.itemIndexMap[item]
            if actual_item != self.last_moused[0]:
                d = self.itemDataMap[actual_item]
                self.last_moused = (actual_item, join(d[3], d[0]))
            self.GetParent().GetParent().GetParent().m_statusbar.set_timed_status(self.last_moused[1])
        event.Skip()

    def get_item_text(self, item, col, absolute=False):
        """Return the text for the given item and col."""

        if not absolute:
            item = self.itemIndexMap[item]
        if col == 1:
            return u'%.2fKB' % self.itemDataMap[item][col]
        elif col in [5, 6]:
            return ctime(self.itemDataMap[item][col])
        else:
            return unicode(self.itemDataMap[item][col])

    def OnGetItemImage(self, item):
        """Override method to get the image for the given item."""

        encoding = self.itemDataMap[self.itemIndexMap[item]][4]
        return 1 if encoding == "BIN" else 0

    def increment_match_count(self, idx):
        """Increment the match count of the given item."""

        entry = list(self.itemDataMap[idx])
        entry[2] += 1
        self.itemDataMap[idx] = tuple(entry)
        # Sample the first "size_sample" to determine
        # column width for when table first loads
        if idx <= self.last_idx_sized or not USE_SAMPLE_SIZE:
            text = self.get_item_text(idx, 2, True)
            lw, lh, d, e = self.dc.GetFullTextExtent(text)
            width = lw + 30
            if width > self.widest_cell[2]:
                self.widest_cell[2] = width

    def on_dclick(self, event):
        """Open file at in editor with optional line and column argument."""

        pos = event.GetPosition()
        item = self.HitTestSubItem(pos)[0]
        if item != -1:
            filename = self.GetItem(item, col=0).GetText()
            path = self.GetItem(item, col=3).GetText()
            line = str(self.get_map_item(item, col=7))
            col = str(self.get_map_item(item, col=8))
            open_editor(join(normpath(path), filename), line, col)
        event.Skip()


class ResultContentList(ResultList):

    """ResultContentList."""

    hex_tx_table = ("." * 32) + "".join(chr(c) for c in range(32, 127)) + ("." * 129)

    def __init__(self, parent):
        """Init ResultContentFileList object."""

        super(ResultContentList, self).__init__(
            parent,
            [
                _("File"),
                _("Line"),
                _("Matches"),
                _("Context")
            ]
        )
        self.last_moused = (-1, "")
        self.Bind(wx.EVT_LEFT_DCLICK, self.on_dclick)
        self.Bind(wx.EVT_MOTION, self.on_motion)
        self.Bind(wx.EVT_ENTER_WINDOW, self.on_enter_window)

    def on_enter_window(self, event):
        """Reset last moused over item tracker on mouse entering the window."""

        self.last_moused = (-1, "")
        event.Skip()

    def on_motion(self, event):
        """Display full file path in status bar on item mouseover."""

        pos = event.GetPosition()
        item = self.HitTestSubItem(pos)[0]
        if item != -1:
            actual_item = self.itemIndexMap[item]
            if actual_item != self.last_moused[0]:
                pth = self.itemDataMap[actual_item][0]
                self.last_moused = (actual_item, join(pth[1], pth[0]))
            self.GetParent().GetParent().GetParent().m_statusbar.set_timed_status(self.last_moused[1])
        event.Skip()

    def _tx_bin(self, content):
        """Format binary data in a friendly way. Display only ASCII."""

        if not isinstance(content, unicode):
            return unicode(content.__repr__()[1:-1])
        else:
            return unicode(content)

    def get_item_text(self, item, col, absolute=False):
        """Return the text for the given item and col."""

        if not absolute:
            item = self.itemIndexMap[item]
        if col == 0:
            return unicode(self.itemDataMap[item][col][0])
        else:
            return unicode(self.itemDataMap[item][col])

    def increment_match_count(self, idx):
        """Increment the match count of the given item."""

        entry = list(self.itemDataMap[idx])
        entry[2] += 1
        self.itemDataMap[idx] = tuple(entry)
        # Sample the first "size_sample" to determine
        # column width for when table first loads
        if idx <= self.last_idx_sized or not USE_SAMPLE_SIZE:
            text = self.get_item_text(idx, 2, True)
            lw, lh, d, e = self.dc.GetFullTextExtent(text)
            width = lw + 30
            if width > self.widest_cell[2]:
                self.widest_cell[2] = width

    def set_match(self, obj):
        """Set the match."""

        item_id = "%d:%d" % (obj.info.id, obj.match.lineno)
        if item_id in self.itemDataMap:
            self.increment_match_count(item_id)
        else:
            self.set_item_map(
                item_id,
                (basename(obj.info.name), dirname(obj.info.name)),
                obj.match.lineno, 1,
                self._tx_bin(obj.match.lines).replace("\r", "").split("\n")[0],
                "%d" % obj.info.id, obj.match.colno, obj.info.encoding
            )

    def OnGetItemImage(self, item):
        """Override method to get the image for the given item."""

        encoding = self.itemDataMap[self.itemIndexMap[item]][6]
        return 1 if encoding == "BIN" else 0

    def on_dclick(self, event):
        """Open file at in editor with optional line and column argument."""

        pos = event.GetPosition()
        item = self.HitTestSubItem(pos)[0]
        if item != -1:
            filename = self.GetItem(item, col=0).GetText()
            line = self.GetItem(item, col=1).GetText()
            file_row = self.get_map_item(item, col=4)
            col = str(self.get_map_item(item, col=5))
            path = self.GetParent().GetParent().GetParent().m_result_file_panel.list.get_map_item(
                file_row, col=3, absolute=True
            )
            open_editor(join(normpath(path), filename), line, col)
        event.Skip()


class FileResultPanel(wx.Panel):

    """FileResultPanel."""

    def __init__(self, parent, obj):
        """Init the FileResultPanel obj."""

        super(FileResultPanel, self).__init__(parent)
        self.list = obj(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.list, 1, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(sizer)
        self.Layout()

    def set_match(self, obj):
        """Set match."""

        self.list.set_match(obj)

    def increment_match_count(self, idx):
        """Increment the match count of the given item."""

        self.list.increment_match_count(idx)

    def set_item_map(self, idx, *args):
        """Set the given item in the item map."""

        self.list.set_item_map(idx, *args)

    def get_map_item(self, idx, col=0):
        """Get the given item in the item map."""

        return self.list.get_map_item(idx, col)

    def load_table(self):
        """Load the list of items."""

        self.list.load_list()
