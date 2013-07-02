"""
Load Search Dialog

Licensed under MIT
Copyright (c) 2013 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import wx
import gui
from _lib.settings import Settings
from _lib.sorted_columns import extend_list


class LoadSearchDialog(gui.LoadSearchDialog):
    def __init__(self, parent):
        super(LoadSearchDialog, self).__init__(parent)

        self.search = None
        self.is_regex = None

        self.reset_table()
        extend_list(self.m_search_list, self.m_load_panel, 3)

        best = self.m_load_panel.GetBestSize()
        current = self.m_load_panel.GetSize()
        offset = best[1] - current[1]
        mainframe = self.GetSize()
        self.SetSize(wx.Size(mainframe[0], mainframe[1] + offset + 15))
        self.SetMinSize(self.GetSize())

        self.load_searches()

    def load_searches(self):
        count = 0
        for x in Settings.get_search():
            search_type = "Regex" if x[2] else "Text"
            self.m_search_list.InsertStringItem(count, x[0])
            self.m_search_list.SetStringItem(count, 1, x[1])
            self.m_search_list.SetStringItem(count, 2, search_type)
            self.m_search_list.SetItemData(count, count)
            self.m_search_list.SetItemImage(count, -1)
            self.m_load_panel.set_item_map(count, x[0], x[1], search_type)
            count += 1
        if count:
            self.column_resize(self.m_search_list, count)

    def on_load(self, event):
        item = self.m_search_list.GetFirstSelected()
        if item == -1:
            return
        idx = self.m_search_list.GetItemData(item)
        self.search = self.m_load_panel.get_map_item(idx, col=1)
        self.is_regex = self.m_load_panel.get_map_item(idx, col=2) == "Regex"
        self.Close()

    def get_search(self):
        return self.search, self.is_regex

    def column_resize(self, obj, count, minimum=100):
        for i in range(0, count):
            obj.SetColumnWidth(i, wx.LIST_AUTOSIZE)
            if obj.GetColumnWidth(i) < minimum:
                obj.SetColumnWidth(i, minimum)

    def reset_table(self):
        self.m_search_list.ClearAll()
        self.m_search_list.InsertColumn(0, "Name")
        self.m_search_list.InsertColumn(1, "Search")
        self.m_search_list.InsertColumn(2, "Type")
        wx.GetApp().Yield()

    def on_delete(self, event):
        item = self.m_search_list.GetFirstSelected()
        if item == -1:
            return
        idx = self.m_search_list.GetItemData(item)
        Settings.delete_search(idx)
        self.m_load_panel.reset_item_map()
        self.reset_table()
        self.load_searches()

    def on_cancel(self, event):
        self.Close()
