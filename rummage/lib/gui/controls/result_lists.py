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
from ..actions import checksum

CONTENT_PATH = 0
CONTENT_LINE = 1
CONTENT_MATCH = 2
CONTENT_EXT = 3
CONTENT_TEXT = 4
CONTENT_KEY = 5
CONTENT_COL = 6
CONTENT_ENC = 7

FILE_NAME = 0
FILE_MATCH = 1
FILE_EXT = 2
FILE_SIZE = 3
FILE_PATH = 4
FILE_ENC = 5
FILE_MOD = 6
FILE_CRE = 7
FILE_LINE = 8
FILE_COL = 9

BULK_MAX = 20

COPY_NAME = 0
COPY_PATH = 1
COPY_CONTENT = 2


class ContextMenu(wx.Menu):
    """Context Menu."""

    def __init__(self, menu):
        """Attach the context menu to to the parent with the defined items."""

        wx.Menu.__init__(self)
        self.create_menu(self, menu)

    def create_menu(self, parent, menu):
        """Create menu."""
        for i in menu:
            if i is None:
                parent.AppendSeparator()
            elif i is not None:
                if isinstance(i[1], list):
                    submenu = wx.Menu()
                    self.create_menu(submenu, i[1])
                    item = parent.AppendSubMenu(submenu, i[0])
                    if len(i) > 2 and not i[2]:
                        parent.Enable(item.GetId(), False)
                else:
                    menuid = wx.NewId()
                    item = wx.MenuItem(self, menuid, i[0])
                    parent.Append(item)
                    if len(i) > 2 and not i[2]:
                        parent.Enable(menuid, False)
                    if util.platform() == 'windows':
                        self.Bind(wx.EVT_MENU, i[1], item)
                    else:
                        parent.Bind(wx.EVT_MENU, i[1], item)


class ResultFileList(DynamicList):
    """ResultFileList."""

    def __init__(self, parent):
        """Init ResultFileList object."""

        self.localize()

        super(ResultFileList, self).__init__(
            parent,
            [
                self.FILE,
                self.MATCHES,
                self.EXTENSION,
                self.SIZE,
                self.PATH,
                self.ENCODING,
                self.MODIFIED,
                self.CREATED
            ],
            False
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
        self.EXTENSION = _('Extensions')
        self.PATH = _("Path")
        self.ENCODING = _("Encoding")
        self.MODIFIED = _("Modified")
        self.CREATED = _("Created")
        self.EDITOR_LABEL = _("Open in Editor")
        self.REVEAL_LABEL = {
            "windows": _("Reveal in Explorer"),
            "osx": _("Reveal in Finder"),
            "linux": _("Reveal in File Manager")
        }
        self.COPY_NAME = _("Copy File Names")
        self.COPY_PATH = _("Copy File Paths")
        self.CHECKSUM_LABEL = _("Checksum")
        self.DELETE_LABEL = _("Delete")
        self.RECYCLE_LABEL = _("Send to Trash")

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
                os.path.basename(obj.name),
                0,
                obj.ext,
                decimal.Decimal(obj.size) / decimal.Decimal(1024),
                os.path.dirname(obj.name),
                '',
                obj.modified,
                obj.created,
                1,
                1
            )
        else:
            item_id = "%d" % obj.info.id
            if item_id in self.itemDataMap:
                self.increment_match_count(item_id)
            else:
                self.set_item_map(
                    item_id,
                    os.path.basename(obj.info.name),
                    1,
                    obj.info.ext,
                    decimal.Decimal(obj.info.size) / decimal.Decimal(1024),
                    os.path.dirname(obj.info.name),
                    obj.info.encoding,
                    obj.info.modified,
                    obj.info.created,
                    obj.match.lineno,
                    obj.match.colno
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
                    self.last_moused = (actual_item, os.path.join(d[FILE_PATH], d[FILE_NAME]))
                self.main_window.m_statusbar.set_timed_status(self.last_moused[1])
        event.Skip()

    def get_item_text(self, item, col, absolute=False):
        """Return the text for the given item and col."""

        if not absolute:
            item = self.itemIndexMap[item]
        if col == FILE_SIZE:
            return '%.2fKB' % round(self.itemDataMap[item][FILE_SIZE], 2)
        elif col in (FILE_MOD, FILE_CRE):
            return ctime(self.itemDataMap[item][col])
        else:
            return util.to_ustr(self.itemDataMap[item][col])

    def OnGetItemImage(self, item):
        """Override method to get the image for the given item."""

        encoding = self.itemDataMap[self.itemIndexMap[item]][FILE_ENC]
        return 1 if encoding == "BIN" else 0

    def increment_match_count(self, idx):
        """Increment the match count of the given item."""

        entry = list(self.itemDataMap[idx])
        entry[FILE_MATCH] += 1
        self.itemDataMap[idx] = tuple(entry)
        # Sample the first "size_sample" to determine
        # column width for when table first loads
        if idx <= self.last_idx_sized or not USE_SAMPLE_SIZE:
            text = self.get_item_text(idx, FILE_MATCH, True)
            lw = self.dc.GetFullTextExtent(text)[0]
            width = lw + 30
            if width > self.widest_cell[FILE_MATCH]:
                self.widest_cell[FILE_MATCH] = width

    def on_dclick(self, event):
        """Open file at in editor with optional line and column argument."""

        pos = event.GetPosition()
        item = self.HitTestSubItem(pos)[0]
        if item != -1:
            self.open_editor(event, item)
        event.Skip()

    def open_editor(self, event, item):
        """Open file(s) in editor."""

        if item != -1:
            target = None
            with self.wait:
                filename = self.GetItem(item, col=FILE_NAME).GetText()
                path = self.GetItem(item, col=FILE_PATH).GetText()
                target = os.path.join(path, filename)
                line = str(self.get_map_item(item, col=FILE_LINE))
                col = str(self.get_map_item(item, col=FILE_COL))
            if target:
                fileops.open_editor(target, line, col)
        else:
            item = self.GetFirstSelected()
            while item != -1:
                target = None
                with self.wait:
                    filename = self.GetItem(item, col=FILE_NAME).GetText()
                    path = self.GetItem(item, col=FILE_PATH).GetText()
                    target = os.path.join(path, filename)
                    line = str(self.get_map_item(item, col=FILE_LINE))
                    col = str(self.get_map_item(item, col=FILE_COL))
                if target:
                    fileops.open_editor(target, line, col)
                item = self.GetNextSelected(item)

    def copy(self, event, col):
        """Copy the content time from the result list."""

        copy_bfr = []

        item = self.GetFirstSelected()
        while item != -1:
            with self.wait:
                if col == FILE_NAME:
                    copy_bfr.append(self.GetItem(item, col=FILE_NAME).GetText())
                elif col == FILE_PATH:
                    copy_bfr.append(self.GetItem(item, col=FILE_PATH).GetText())
            item = self.GetNextSelected(item)

        if copy_bfr:
            if wx.TheClipboard.Open():
                try:
                    wx.TheClipboard.SetData(wx.TextDataObject('\n'.join(copy_bfr)))
                except Exception:
                    pass
                wx.TheClipboard.Close()

    def get_selected_files(self):
        """Get selected files filtering out duplicates."""

        files = set()
        with self.wait:
            item = self.GetNextItem(-1)
            while item != -1:
                if self.IsSelected(item):
                    filename = self.GetItem(item, col=FILE_NAME).GetText()
                    path = self.GetItem(item, col=FILE_PATH).GetText()
                    files.add(os.path.join(path, filename))
                item = self.GetNextItem(item)
        return sorted(list(files))

    def on_rclick(self, event):
        """Show context menu on right click."""

        target = None
        enabled = False
        bulk_enabled = False
        with self.wait:
            pos = event.GetPosition()
            item = self.HitTestSubItem(pos)[0]
            if item != -1:
                filename = self.GetItem(item, col=FILE_NAME).GetText()
                path = self.GetItem(item, col=FILE_PATH).GetText()
                target = os.path.join(path, filename)
                selected = self.IsSelected(item)
                select_count = self.GetSelectedItemCount()
                enabled = not selected or (selected and select_count == 1)
                bulk_enabled = not selected or (selected and select_count <= BULK_MAX)
                # Select if not already
                if not selected:
                    s = self.GetFirstSelected()
                    while s != -1:
                        if s != item:
                            self.Select(s, False)
                        s = self.GetNextSelected(s)
        if target is not None:
            if not enabled:
                item = -1

            hash_entries = []
            for h in checksum.VALID_HASH:
                hash_entries.append((h, functools.partial(self.main_window.on_checksum, h=h, target=target)))

            # Open menu
            menu = ContextMenu(
                [
                    (self.COPY_NAME, functools.partial(self.copy, col=FILE_NAME)),
                    (self.COPY_PATH, functools.partial(self.copy, col=FILE_PATH)),
                    None,
                    (self.REVEAL_LABEL[util.platform()], functools.partial(fileops.reveal, target=target), enabled),
                    (self.EDITOR_LABEL, functools.partial(self.open_editor, item=item), bulk_enabled),
                    (self.CHECKSUM_LABEL, hash_entries, (enabled and self.complete)),
                    None,
                    (
                        self.DELETE_LABEL,
                        functools.partial(self.main_window.on_delete_files, recycle=False, listctrl=self),
                        self.complete
                    ),
                    (
                        self.RECYCLE_LABEL,
                        functools.partial(self.main_window.on_delete_files, recycle=True, listctrl=self),
                        self.complete
                    )
                ]
            )
            self.PopupMenu(menu, pos)
            menu.Destroy()
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
                self.EXTENSION,
                self.CONTEXT
            ],
            False
        )
        self.last_moused = (-1, "")
        self.Bind(wx.EVT_LEFT_DCLICK, self.on_dclick)
        self.Bind(wx.EVT_MOTION, self.on_motion)
        self.Bind(wx.EVT_ENTER_WINDOW, self.on_enter_window)
        self.Bind(wx.EVT_RIGHT_DOWN, self.on_rclick)

    def localize(self):
        """Translate strings."""

        self.FILE = _("File")
        self.LINE = _("Line")
        self.MATCHES = _("Matches")
        self.EXTENSION = _("Extension")
        self.CONTEXT = _("Context")
        self.EDITOR_LABEL = _("Open in Editor")
        self.REVEAL_LABEL = {
            "windows": _("Reveal in Explorer"),
            "osx": _("Reveal in Finder"),
            "linux": _("Reveal in File Manager")
        }
        self.COPY_NAME = _("Copy File Names")
        self.COPY_PATH = _("Copy File Paths")
        self.COPY_CONTENT = _("Copy File Content")
        self.CHECKSUM_LABEL = _("Checksum")
        self.DELETE_LABEL = _("Delete")
        self.RECYCLE_LABEL = _("Send to Trash")

    def GetSecondarySortValues(self, col, key1, key2):
        """Get secondary sort values."""

        if col == CONTENT_LINE:
            return (self.itemDataMap[key1][CONTENT_PATH], self.itemDataMap[key2][CONTENT_PATH])
        elif col == CONTENT_PATH:
            return (self.itemDataMap[key1][CONTENT_LINE], self.itemDataMap[key2][CONTENT_LINE])
        else:
            return (
                (self.itemDataMap[key1][CONTENT_PATH], self.itemDataMap[key1][CONTENT_LINE]),
                (self.itemDataMap[key2][CONTENT_PATH], self.itemDataMap[key2][CONTENT_LINE])
            )

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
                    pth = self.itemDataMap[actual_item][CONTENT_PATH]
                    self.last_moused = (actual_item, os.path.join(pth[1], pth[0]))
                self.main_window.m_statusbar.set_timed_status(self.last_moused[1])
        event.Skip()

    def get_item_text(self, item, col, absolute=False):
        """Return the text for the given item and col."""

        if not absolute:
            item = self.itemIndexMap[item]
        if col == CONTENT_PATH:
            return util.to_ustr(self.itemDataMap[item][CONTENT_PATH][0])
        else:
            return util.to_ustr(self.itemDataMap[item][col])

    def increment_match_count(self, idx):
        """Increment the match count of the given item."""

        entry = list(self.itemDataMap[idx])
        entry[CONTENT_MATCH] += 1
        self.itemDataMap[idx] = tuple(entry)
        # Sample the first "size_sample" to determine
        # column width for when table first loads
        if idx <= self.last_idx_sized or not USE_SAMPLE_SIZE:
            text = self.get_item_text(idx, CONTENT_MATCH, True)
            lw = self.dc.GetFullTextExtent(text)[0]
            width = lw + 30
            if width > self.widest_cell[CONTENT_MATCH]:
                self.widest_cell[CONTENT_MATCH] = width

    def set_match(self, obj):
        """Set the match."""

        item_id = "%d:%d" % (obj.info.id, obj.match.lineno)
        if item_id in self.itemDataMap:
            self.increment_match_count(item_id)
        else:
            self.set_item_map(
                item_id,
                (os.path.basename(obj.info.name), os.path.dirname(obj.info.name)),
                obj.match.lineno,
                1,
                obj.info.ext,
                obj.match.lines.replace("\r", "").split("\n")[0],
                "%d" % obj.info.id,
                obj.match.colno,
                obj.info.encoding
            )

    def OnGetItemImage(self, item):
        """Override method to get the image for the given item."""

        encoding = self.itemDataMap[self.itemIndexMap[item]][CONTENT_ENC]
        return 1 if encoding == "BIN" else 0

    def on_dclick(self, event):
        """Open file at in editor with optional line and column argument."""

        with self.wait:
            pos = event.GetPosition()
            item = self.HitTestSubItem(pos)[0]
            if item != -1:
                filename = self.GetItem(item, col=CONTENT_PATH).GetText()
                line = self.GetItem(item, col=CONTENT_LINE).GetText()
                file_row = self.get_map_item(item, col=CONTENT_KEY)
                col = str(self.get_map_item(item, col=CONTENT_COL))
                path = self.main_window.m_result_file_list.get_map_item(
                    file_row, col=FILE_PATH, absolute=True
                )
                fileops.open_editor(os.path.join(os.path.normpath(path), filename), line, col)
        event.Skip()

    def open_editor(self, event, item):
        """Open file(s) in editor."""

        if item != -1:
            target = None
            with self.wait:
                file_row = self.get_map_item(item, col=CONTENT_KEY)
                filename = self.GetItem(item, col=CONTENT_PATH).GetText()
                path = self.main_window.m_result_file_list.get_map_item(
                    file_row, col=FILE_PATH, absolute=True
                )
                target = os.path.join(path, filename)
                line = self.GetItem(item, col=CONTENT_LINE).GetText()
                col = str(self.get_map_item(item, col=CONTENT_COL))
            if target:
                fileops.open_editor(target, line, col)
        else:
            found = set()
            item = self.GetFirstSelected()
            while item != -1:
                target = None
                with self.wait:
                    file_row = self.get_map_item(item, col=CONTENT_KEY)
                    filename = self.GetItem(item, col=CONTENT_PATH).GetText()
                    path = self.main_window.m_result_file_list.get_map_item(
                        file_row, col=FILE_PATH, absolute=True
                    )
                    target = os.path.join(path, filename)
                    line = self.GetItem(item, col=CONTENT_LINE).GetText()
                    col = str(self.get_map_item(item, col=CONTENT_COL))
                if target and target not in found:
                    found.add(target)
                    fileops.open_editor(target, line, col)
                item = self.GetNextSelected(item)

    def copy(self, event, col, from_file_tab=False):
        """Copy the content time from the result list."""

        copy_bfr = []

        item = self.GetFirstSelected()
        while item != -1:
            with self.wait:
                if col == CONTENT_PATH:
                    if from_file_tab:
                        file_row = self.get_map_item(item, col=CONTENT_KEY)
                        path = self.main_window.m_result_file_list.get_map_item(
                            file_row, col=FILE_PATH, absolute=True
                        )
                        filename = self.GetItem(item, col=CONTENT_PATH).GetText()
                        copy_bfr.append(os.path.join(path, filename))
                    else:
                        copy_bfr.append(self.GetItem(item, col=CONTENT_PATH).GetText())
                else:
                    copy_bfr.append(self.GetItem(item, col=CONTENT_TEXT).GetText())
            item = self.GetNextSelected(item)

        if copy_bfr:
            if wx.TheClipboard.Open():
                try:
                    wx.TheClipboard.SetData(wx.TextDataObject('\n'.join(copy_bfr)))
                except Exception:
                    pass
                wx.TheClipboard.Close()

    def get_selected_files(self):
        """Get selected files filtering out duplicates."""

        files = set()
        with self.wait:
            item = self.GetNextItem(-1)
            while item != -1:
                if self.IsSelected(item):
                    file_row = self.get_map_item(item, col=CONTENT_KEY)
                    path = self.main_window.m_result_file_list.get_map_item(
                        file_row, col=FILE_PATH, absolute=True
                    )
                    filename = self.GetItem(item, col=CONTENT_PATH).GetText()
                    files.add(os.path.join(path, filename))
                item = self.GetNextItem(item)
        return sorted(list(files))

    def on_rclick(self, event):
        """Show context menu on right click."""

        target = None
        enabled = False
        bulk_enabled = False
        with self.wait:
            pos = event.GetPosition()
            item = self.HitTestSubItem(pos)[0]
            if item != -1:
                file_row = self.get_map_item(item, col=CONTENT_KEY)
                filename = self.GetItem(item, col=CONTENT_PATH).GetText()
                path = self.main_window.m_result_file_list.get_map_item(
                    file_row, col=FILE_PATH, absolute=True
                )
                target = os.path.join(path, filename)
                selected = self.IsSelected(item)
                select_count = self.GetSelectedItemCount()
                enabled = not selected or (selected and select_count == 1)
                bulk_enabled = not selected or (selected and select_count <= BULK_MAX)
                # Select if not already
                if not selected:
                    s = self.GetFirstSelected()
                    while s != -1:
                        if s != item:
                            self.Select(s, False)
                        s = self.GetNextSelected(s)
        if target is not None:
            if not enabled:
                item = -1

            hash_entries = []
            for h in checksum.VALID_HASH:
                hash_entries.append((h, functools.partial(self.main_window.on_checksum, h=h, target=target)))

            # Open menu
            menu = ContextMenu(
                [
                    (self.COPY_NAME, functools.partial(self.copy, col=CONTENT_PATH)),
                    (self.COPY_PATH, functools.partial(self.copy, col=CONTENT_PATH, from_file_tab=True)),
                    (self.COPY_CONTENT, functools.partial(self.copy, col=CONTENT_TEXT)),
                    None,
                    (self.REVEAL_LABEL[util.platform()], functools.partial(fileops.reveal, target=target), enabled),
                    (self.EDITOR_LABEL, functools.partial(self.open_editor, item=item), bulk_enabled),
                    (self.CHECKSUM_LABEL, hash_entries, (enabled and self.complete)),
                    None,
                    (
                        self.DELETE_LABEL,
                        functools.partial(self.main_window.on_delete_files, recycle=False, listctrl=self),
                        self.complete
                    ),
                    (
                        self.RECYCLE_LABEL,
                        functools.partial(self.main_window.on_delete_files, recycle=True, listctrl=self),
                        self.complete
                    )
                ]
            )
            self.PopupMenu(menu, pos)
            menu.Destroy()
        event.Skip()
