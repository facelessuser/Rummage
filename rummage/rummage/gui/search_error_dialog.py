"""
Search Error Dialog.

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

from . import gui
from ..localization import _
from .custom_app import error
from .messages import error_icon
from .. import data


class MixinSortList(listmix.ColumnSorterMixin, listmix.ListRowHighlighter):

    """Mixin Sort List."""

    def setup(self):
        """Init MixinSortList object."""

        self.column_count = 2
        self.itemDataMap = {}
        self.images = wx.ImageList(16, 16)
        graphic = error_icon.GetImage()
        graphic.Rescale(16, 16)
        self.error_symbol = self.images.Add(wx.BitmapFromImage(graphic))
        self.sort_up = self.images.Add(data.get_image('su.png').GetBitmap())
        self.sort_down = self.images.Add(data.get_image('sd.png').GetBitmap())
        self.SetImageList(self.images, wx.IMAGE_LIST_SMALL)
        listmix.ColumnSorterMixin.__init__(self, self.column_count)
        listmix.ListRowHighlighter.__init__(self, (0xEE, 0xEE, 0xEE))

    def reset_item_map(self):
        """Reset the item map."""

        self.itemDataMap = {}

    def set_item_map(self, idx, *args):
        """Add entry to item map."""

        self.itemDataMap[idx] = tuple([a for a in args])

    def init_sort(self):
        """Do the intial sort."""

        self.SortListItems(col=0, ascending=1)
        self.RefreshRows()

    def GetListCtrl(self):
        """Return ListCtrl object (self)."""

        return self

    def GetSortImages(self):
        """Return the sort arrows for the header."""

        return self.sort_down, self.sort_up

    def get_map_item(self, idx, col=0):
        """Get map element from mapping entry."""

        return self.itemDataMap[idx][col]

    def OnSortOrderChanged(self):
        """Refresh the rows on sort."""

        self.RefreshRows()


def extend(instance, extension):
    """Extend object with extension class."""

    instance.__class__ = type(
        b'%s_extended_with_%s' % (instance.__class__.__name__, extension.__name__),
        (instance.__class__, extension),
        {}
    )


def extend_list(l):
    """Extend list with with special sorting class."""

    extend(l, MixinSortList)
    l.setup()


class SearchErrorDialog(gui.SearchErrorDialog):

    """Load search dialog."""

    def __init__(self, parent, errors):
        """Init LoadSearchDialog."""

        super(SearchErrorDialog, self).__init__(parent)

        self.reset_table()
        extend_list(self.m_error_list)

        self.localize()

        best = self.m_error_panel.GetBestSize()
        current = self.m_error_panel.GetSize()
        offset = best[1] - current[1]
        mainframe = self.GetSize()
        self.SetSize(wx.Size(mainframe[0], mainframe[1] + offset + 15))
        self.SetMinSize(self.GetSize())

        self.load_errors(errors)
        self.m_error_list.SetFocus()

    def localize(self):
        """Localize dialog."""

        self.SetTitle(_("Errors"))
        self.Fit()

    def load_errors(self, errors):
        """Populate list with error entries."""

        count = 0
        for e in errors:
            if hasattr(e, 'info'):
                name = e.info.name if e.info.name is not None else ''
            else:
                name = '<NA>'
            error(
                _("Cound not process %s:\n%s") % (name, e.error[1] + e.error[0])
            )
            self.m_error_list.InsertStringItem(count, e.error[0])
            self.m_error_list.SetStringItem(count, 1, name)
            self.m_error_list.SetItemData(count, count)
            self.m_error_list.SetItemImage(count, 0)
            self.m_error_list.set_item_map(count, e.error[0], name)
            count += 1
        if count:
            self.column_resize(self.m_error_list, count)
        self.m_error_list.init_sort()

    def column_resize(self, obj, count, minimum=100, maximum=-1):
        """Resize columns."""

        for i in range(0, count):
            obj.SetColumnWidth(i, wx.LIST_AUTOSIZE)
            width = obj.GetColumnWidth(i)
            if maximum != -1 and width > maximum:
                obj.SetColumnWidth(i, maximum)
            elif width < minimum:
                obj.SetColumnWidth(i, minimum)

    def reset_table(self):
        """Clear and reset the list."""

        self.m_error_list.ClearAll()
        self.m_error_list.InsertColumn(0, _("Error"))
        self.m_error_list.InsertColumn(1, _("File Name"))
        wx.GetApp().Yield()
