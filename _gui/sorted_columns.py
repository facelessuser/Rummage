"""
Sorted Columns

Licensed under MIT
Copyright (c) 2013 Isaac Muse <isaacmuse@gmail.com>
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from time import ctime
import wx
import wx.lib.mixins.listctrl as listmix
from wx.lib.embeddedimage import PyEmbeddedImage
import subprocess
import sys
from os.path import normpath, join

from _lib.settings import Settings

from _gui.custom_app import debug, debug_struct, info, error

MINIMUM_COL_SIZE = 100
COLUMN_SAMPLE_SIZE = 100

up_arrow = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmJLR0QA/wD/AP+gvaeTAAAA"
    "CXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH3QYcDzITlWnqRAAAACZpVFh0Q29tbWVudAAA"
    "AAAAQ3JlYXRlZCB3aXRoIEdJTVAgb24gYSBNYWOV5F9bAAAA6klEQVQ4y2NgGAXM+CSdnZ29"
    "lJSUZikpKb2+f//+bWxqmPBolv7161fe06dP3zEwMOQ6OztLE+0CZ2dn5p8/f3a/f/9ejJWV"
    "lfPbt28sLCwsuqqqqtvu37//n6ALvn37lv7u3TtFZmZmBlFRUZiYIgMDQyJBFxgZGVl8+/Yt"
    "l4WFhRmmmZubm+HFixdMf/780dXR0Tl///79l1hdsGrVKvHfv39XsbGxMSorK6MYrKioyMDC"
    "wsL48ePHOmdnZ26YOAuyouvXr5c6ODhwc3FxMbCxsTHw8fFhhjoTE8+2bdvyGRgY2kYTMZUA"
    "AElBSjR/j22+AAAAAElFTkSuQmCC")

down_arrow = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmJLR0QA/wD/AP+gvaeTAAAA"
    "CXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH3QYcDzAUOTsdZQAAACZpVFh0Q29tbWVudAAA"
    "AAAAQ3JlYXRlZCB3aXRoIEdJTVAgb24gYSBNYWOV5F9bAAABIklEQVQ4y+2Sv0uFUBTHz33v"
    "KnIfqZGgIgg6NLk0tARtzu//aYuGlmpobm1sCu54l4SWoNlBuA0paEtqgb/otvTCeq+3tEVn"
    "O+f7+X6X7wH4n18PGi9BEJx6nreT5/mkaRro+37JIIRoHce5YYwdAwDgsVhV1UkYhhdRFG0U"
    "RQGSJH0xE0LAdd2XOI7PF7fpGCjL8tV13SdZlvcRQqht209N13UwDEMkSXLAGHtcGfABPkiS"
    "tEkI2RZCoK7rQFEUIIS8pWl6xRijY34pgHMuTNO8wxjvaZq2pSgKWJYFdV0nTdMccc7F2oBF"
    "iG3b97PZbK6qaltV1WQYhkNKaf6dnf5UD+e89n0fYYx3syw7o5TeruLwuo4ty7oEgGvG2PMf"
    "fuV31ftuS80saUMAAAAASUVORK5CYII=")

doc = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQAgMAAABinRfyAAAADFBMVEUAAABEQkJjY2P///93"
    "ZMrLAAAAAXRSTlMAQObYZgAAAClJREFUCFtjYEAFjKEhQOL/XSDx6r4DkHUVSLzaD2L9B7FW"
    "42OFhjoAAPlQF/qFKDe3AAAAAElFTkSuQmCC")


def editor_open(filename, line, col):
    returncode = None

    debug(filename, line, col)
    cmd = Settings.get_editor(filename=filename, line=line, col=col)
    if len(cmd) == 0:
        errormsg("No editor is currently set!")
        return
    debug(cmd)

    if sys.platform.startswith('win'):
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        process = subprocess.Popen(
            cmd,
            startupinfo=startupinfo,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE,
            shell=False
        )
    else:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE,
            shell=False
        )
    process.communicate()
    returncode = process.returncode
    return returncode


class ResultList(wx.ListCtrl, listmix.ColumnSorterMixin):
    def __init__(self, parent, columns):
        super(ResultList, self).__init__(parent, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_VIRTUAL)
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

        self.images = wx.ImageList(16, 16)
        self.doc = self.images.Add(doc.GetBitmap())
        self.sort_up = self.images.Add(up_arrow.GetBitmap())
        self.sort_down = self.images.Add(down_arrow.GetBitmap())
        self.SetImageList(self.images, wx.IMAGE_LIST_SMALL)

    def resize_columns(self, minimum=MINIMUM_COL_SIZE):
        for i in range(0, self.column_count):
            self.SetColumnWidth(i, wx.LIST_AUTOSIZE)
            if self.GetColumnWidth(i) < minimum:
                self.SetColumnWidth(i, minimum)

    def init_column_size(self, minimum=MINIMUM_COL_SIZE):
        for i in range(0, self.column_count):
            self.SetColumnWidth(i, self.widest_cell[i])
        self.size_sample = 0

    def get_column_count(self):
        return self.column_count

    def set_item_map(self, idx, *args):
        self.itemDataMap[idx] = tuple([a for a in args])
        # Sample the first "size_sample" to determine
        # column width for when table first loads
        if self.size_sample:
            for x in range(0, self.column_count):
                text = self.get_item_text(idx, x, True)
                lw, _, _, _ = self.dc.GetFullTextExtent(text)
                width = lw + 10
                if width > self.widest_cell[x]:
                    self.widest_cell[x] = width
            self.size_guess -= 1

    def get_map_item(self, idx, col=0, abs=False):
        return self.itemDataMap[self.itemIndexMap[idx] if not abs else idx][col]

    def load_list(self):
        for x in range(0, self.column_count):
            self.InsertColumn(x, self.headers[x])
        self.SetItemCount(len(self.itemDataMap))
        listmix.ColumnSorterMixin.__init__(self, self.column_count)
        self.SortListItems(col=0, ascending=1)
        self.init_column_size()

    def SortItems(self,sorter=cmp):
        items = list(self.itemDataMap.keys())
        items.sort(sorter)
        self.itemIndexMap = items

        # redraw the list
        self.Refresh()

    def OnGetItemText(self, item, col):
        return self.get_item_text(item, col)

    def get_item_text(self, idx, col, abs=False):
        return unicode(self.itemDataMap[self.itemIndexMap[idx] if not abs else idx][col])

    def OnGetItemAttr(self, item):
        if item % 2 == 0:
            return self.attr1
        return -1

    def OnGetItemImage (self, item):
        return 0

    def GetSortImages(self):
        return self.sort_down, self.sort_up

    def GetListCtrl(self):
        return self


class ResultFileList(ResultList):
    def __init__(self, parent):
        super(ResultFileList, self).__init__(parent, ["File", "Size", "Matches", "Path", "Encoding", "Time"])
        self.Bind(wx.EVT_LEFT_DCLICK, self.on_dclick)

    def get_item_text(self, item, col, abs=False):
        if not abs:
            item = self.itemIndexMap[item]
        if col == 1:
            return u'%.2fKB' % self.itemDataMap[item][col]
        elif col == 5:
            return ctime(self.itemDataMap[item][col])
        else:
            return unicode(self.itemDataMap[item][col])

    def on_dclick(self, event):
        pos = event.GetPosition()
        item = self.HitTestSubItem(pos)[0]
        if item != -1:
            filename = self.GetItem(item, col=0).GetText()
            path = self.GetItem(item, col=3).GetText()
            line = str(self.get_map_item(item, col=6))
            col = str(self.get_map_item(item, col=7))
            editor_open(join(normpath(path), filename), line, col)
        event.Skip()


class ResultContentList(ResultList):
    def __init__(self, parent):
        super(ResultContentList, self).__init__(parent, ["File", "Line", "Context"])
        self.Bind(wx.EVT_LEFT_DCLICK, self.on_dclick)

    def on_dclick(self, event):
        pos = event.GetPosition()
        item = self.HitTestSubItem(pos)[0]
        if item != -1:
            filename = self.GetItem(item, col=0).GetText()
            line = self.GetItem(item, col=1).GetText()
            file_row = self.get_map_item(item, col=3)
            col = str(self.get_map_item(item, col=4))
            path = self.GetParent().GetParent().GetParent().m_result_file_panel.list.get_map_item(file_row, col=3, abs=True)
            editor_open(join(normpath(path), filename), line, col)
        event.Skip()


class FileResultPanel(wx.Panel):
    def __init__(self, parent, obj):
        super(FileResultPanel, self).__init__(parent)
        self.list = obj(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.list, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(sizer)
        self.Layout()

    def set_item_map(self, idx, *args):
        self.list.set_item_map(idx, *args)

    def get_map_item(self, idx, col=0):
        return self.list.get_map_item(idx, col)

    def load_table(self):
        self.list.load_list()
