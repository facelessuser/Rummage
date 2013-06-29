"""
Sorted Columns

Licensed under MIT
Copyright (c) 2013 Isaac Muse <isaacmuse@gmail.com>
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import wx
import wx.lib.mixins.listctrl as listmix
from wx.lib.embeddedimage import PyEmbeddedImage

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


class MixinSortPanel(listmix.ColumnSorterMixin):
    def setup(self, l, c):
        self.list = l
        self.column_count = c
        self.itemDataMap = {}
        self.images = wx.ImageList(16, 16)
        self.doc = self.images.Add(doc.GetBitmap())
        self.sort_up = self.images.Add(up_arrow.GetBitmap())
        self.sort_down = self.images.Add(down_arrow.GetBitmap())
        self.list.SetImageList(self.images, wx.IMAGE_LIST_SMALL)
        listmix.ColumnSorterMixin.__init__(self, self.column_count)

    def reset_item_map(self):
        self.itemDataMap = {}

    def set_item_map(self, idx, *args):
        self.itemDataMap[idx] = tuple([a for a in args])

    def init_sort(self):
        self.SortListItems(col=0, ascending=1)

    def GetListCtrl(self):
        return self.list

    def GetSortImages(self):
        return self.sort_down, self.sort_up

    def get_map_item(self, idx, col=0):
        return self.itemDataMap[idx][col]

def extend(instance, extension):
    instance.__class__ = type(
        '%s_extended_with_%s' % (instance.__class__.__name__, extension.__name__),
        (instance.__class__, extension),
        {}
    )

def extend_list(l, p, c):
    extend(p, MixinSortPanel)
    p.setup(l, c)
