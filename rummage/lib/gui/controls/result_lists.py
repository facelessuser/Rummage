"""
Result lists.

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
from time import ctime
import wx
import decimal
import os
import functools
from .dynamic_lists import DynamicList, USE_SAMPLE_SIZE
from ..actions import fileops
from ..localization import _
from .. import data
from ... import util


class ContextMenu(wx.Menu):
    """Context Menu."""

    def __init__(self, parent, menu, pos):
        """Attach the context menu to to the parent with the defined items."""

        wx.Menu.__init__(self)
        self._callbacks = {}

        for i in menu:
            menuid = wx.NewId()
            item = wx.MenuItem(self, menuid, i[0])
            self._callbacks[menuid] = i[1]
            self.Append(item)
            if len(i) > 2 and not i[2]:
                self.Enable(menuid, False)
            self.Bind(wx.EVT_MENU, self.on_callback, item)

        parent.PopupMenu(self, pos)

    def on_callback(self, event):
        """Execute the menu item callback."""

        menuid = event.GetId()
        self._callbacks[menuid](event)
        event.Skip()


class ResultFileList(DynamicList):
    """ResultFileList."""

    def __init__(self, parent):
        """Init ResultFileList object."""

        self.localize()

        super(ResultFileList, self).__init__(
            parent,
            [
                self.FILE,
                self.SIZE,
                self.MATCHES,
                self.PATH,
                self.ENCODING,
                self.MODIFIED,
                self.CREATED
            ]
        )
        self.last_moused = (-1, "")
        self.Bind(wx.EVT_LEFT_DCLICK, self.on_dclick)
        self.Bind(wx.EVT_MOTION, self.on_motion)
        self.Bind(wx.EVT_ENTER_WINDOW, self.on_enter_window)
        self.Bind(wx.EVT_RIGHT_DOWN, self.on_rclick)

    def localize(self):
        """Translate strings."""

        self.FILE = _("File")
        self.SIZE = _("Size")
        self.MATCHES = _("Matches")
        self.PATH = _("Path")
        self.ENCODING = _("Encoding")
        self.MODIFIED = _("Modified")
        self.CREATED = _("Created")
        self.REVEAL_LABEL = {
            "windows": _("Reveal in Explorer"),
            "osx": _("Reveal in Finder"),
            "linux": _("Reveal in File Manager")
        }

    def create_image_list(self):
        """Create the image list."""

        self.images = wx.ImageList(16, 16)
        self.doc = self.images.Add(data.get_bitmap('doc.png'))
        self.bin = self.images.Add(data.get_bitmap('binary.png'))
        self.sort_up = self.images.Add(data.get_bitmap('su.png'))
        self.sort_down = self.images.Add(data.get_bitmap('sd.png'))
        self.SetImageList(self.images, wx.IMAGE_LIST_SMALL)

    def set_match(self, obj, file_search=False):
        """Set match."""

        if file_search:
            self.set_item_map(
                obj.name,
                os.path.basename(obj.name), decimal.Decimal(obj.size) / decimal.Decimal(1024), 0,
                os.path.dirname(obj.name), '', obj.modified,
                obj.created, 1, 1
            )
        else:
            item_id = "%d" % obj.info.id
            if item_id in self.itemDataMap:
                self.increment_match_count(item_id)
            else:
                self.set_item_map(
                    item_id,
                    os.path.basename(obj.info.name), decimal.Decimal(obj.info.size) / decimal.Decimal(1024), 1,
                    os.path.dirname(obj.info.name), obj.info.encoding, obj.info.modified,
                    obj.info.created, obj.match.lineno, obj.match.colno
                )

    def on_enter_window(self, event):
        """Reset last moused over item tracker on mouse entering the window."""

        self.last_moused = (-1, "")
        event.Skip()

    def on_motion(self, event):
        """Display full file path in status bar on item mouseover."""

        if self.complete:
            pos = event.GetPosition()
            item = self.HitTestSubItem(pos)[0]
            if item != -1:
                actual_item = self.itemIndexMap[item]
                if actual_item != self.last_moused[0]:
                    d = self.itemDataMap[actual_item]
                    self.last_moused = (actual_item, os.path.join(d[3], d[0]))
                self.GetParent().GetParent().GetParent().GetParent().m_statusbar.set_timed_status(self.last_moused[1])
        event.Skip()

    def get_item_text(self, item, col, absolute=False):
        """Return the text for the given item and col."""

        if not absolute:
            item = self.itemIndexMap[item]
        if col == 1:
            return '%.2fKB' % round(self.itemDataMap[item][col], 2)
        elif col in [5, 6]:
            return ctime(self.itemDataMap[item][col])
        else:
            return util.to_ustr(self.itemDataMap[item][col])

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
            lw = self.dc.GetFullTextExtent(text)[0]
            width = lw + 30
            if width > self.widest_cell[2]:
                self.widest_cell[2] = width

    def on_dclick(self, event):
        """Open file at in editor with optional line and column argument."""

        with self.wait:
            pos = event.GetPosition()
            item = self.HitTestSubItem(pos)[0]
            if item != -1:
                filename = self.GetItem(item, col=0).GetText()
                path = self.GetItem(item, col=3).GetText()
                line = str(self.get_map_item(item, col=7))
                col = str(self.get_map_item(item, col=8))
                fileops.open_editor(os.path.join(os.path.normpath(path), filename), line, col)
        event.Skip()

    def on_rclick(self, event):
        """Show context menu on right click."""

        target = None
        enabled = False
        with self.wait:
            pos = event.GetPosition()
            item = self.HitTestSubItem(pos)[0]
            if item != -1:
                filename = self.GetItem(item, col=0).GetText()
                path = self.GetItem(item, col=3).GetText()
                target = os.path.join(path, filename)
                selected = self.IsSelected(item)
                select_count = self.GetSelectedItemCount()
                enabled = not selected or (selected and select_count == 1)
                # Select if not already
                if not selected:
                    self.Select(item)
        if target is not None:
            # Open menu
            ContextMenu(
                self,
                [
                    (self.REVEAL_LABEL[util.platform()], functools.partial(fileops.reveal, target=target), enabled)
                ],
                pos
            )
        event.Skip()


class ResultContentList(DynamicList):
    """ResultContentList."""

    def __init__(self, parent):
        """Init ResultContentFileList object."""

        self.localize()

        super(ResultContentList, self).__init__(
            parent,
            [
                self.FILE,
                self.LINE,
                self.MATCHES,
                self.CONTEXT
            ]
        )
        self.last_moused = (-1, "")
        self.Bind(wx.EVT_LEFT_DCLICK, self.on_dclick)
        self.Bind(wx.EVT_MOTION, self.on_motion)
        self.Bind(wx.EVT_ENTER_WINDOW, self.on_enter_window)

    def localize(self):
        """Translate strings."""

        self.FILE = _("File")
        self.LINE = _("Line")
        self.MATCHES = _("Matches")
        self.CONTEXT = _("Context")

    def create_image_list(self):
        """Create the image list."""

        self.images = wx.ImageList(16, 16)
        self.doc = self.images.Add(data.get_bitmap('doc.png'))
        self.bin = self.images.Add(data.get_bitmap('binary.png'))
        self.sort_up = self.images.Add(data.get_bitmap('su.png'))
        self.sort_down = self.images.Add(data.get_bitmap('sd.png'))
        self.SetImageList(self.images, wx.IMAGE_LIST_SMALL)

    def on_enter_window(self, event):
        """Reset last moused over item tracker on mouse entering the window."""

        self.last_moused = (-1, "")
        event.Skip()

    def on_motion(self, event):
        """Display full file path in status bar on item mouseover."""

        if self.complete:
            pos = event.GetPosition()
            item = self.HitTestSubItem(pos)[0]
            if item != -1:
                actual_item = self.itemIndexMap[item]
                if actual_item != self.last_moused[0]:
                    pth = self.itemDataMap[actual_item][0]
                    self.last_moused = (actual_item, os.path.join(pth[1], pth[0]))
                self.GetParent().GetParent().GetParent().GetParent().m_statusbar.set_timed_status(self.last_moused[1])
        event.Skip()

    def get_item_text(self, item, col, absolute=False):
        """Return the text for the given item and col."""

        if not absolute:
            item = self.itemIndexMap[item]
        if col == 0:
            return util.to_ustr(self.itemDataMap[item][col][0])
        else:
            return util.to_ustr(self.itemDataMap[item][col])

    def increment_match_count(self, idx):
        """Increment the match count of the given item."""

        entry = list(self.itemDataMap[idx])
        entry[2] += 1
        self.itemDataMap[idx] = tuple(entry)
        # Sample the first "size_sample" to determine
        # column width for when table first loads
        if idx <= self.last_idx_sized or not USE_SAMPLE_SIZE:
            text = self.get_item_text(idx, 2, True)
            lw = self.dc.GetFullTextExtent(text)[0]
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
                (os.path.basename(obj.info.name), os.path.dirname(obj.info.name)),
                obj.match.lineno, 1,
                obj.match.lines.replace("\r", "").split("\n")[0],
                "%d" % obj.info.id, obj.match.colno, obj.info.encoding
            )

    def OnGetItemImage(self, item):
        """Override method to get the image for the given item."""

        encoding = self.itemDataMap[self.itemIndexMap[item]][6]
        return 1 if encoding == "BIN" else 0

    def on_dclick(self, event):
        """Open file at in editor with optional line and column argument."""

        while self.wait:
            pos = event.GetPosition()
            item = self.HitTestSubItem(pos)[0]
            if item != -1:
                filename = self.GetItem(item, col=0).GetText()
                line = self.GetItem(item, col=1).GetText()
                file_row = self.get_map_item(item, col=4)
                col = str(self.get_map_item(item, col=5))
                path = self.GetParent().GetParent().GetParent().GetParent().m_result_file_list.get_map_item(
                    file_row, col=3, absolute=True
                )
                fileops.open_editor(os.path.join(os.path.normpath(path), filename), line, col)
        event.Skip()
