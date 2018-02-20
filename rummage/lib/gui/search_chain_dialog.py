"""
Search chain dialog.

Licensed under MIT
Copyright (c) 2017 Isaac Muse <isaacmuse@gmail.com>

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
from .settings import Settings
from .edit_search_chain_dialog import EditSearchChainDialog
from .localization import _
from . import gui


class SearchChainDialog(gui.SearchChainDialog):
    """Search chain dialog."""

    def __init__(self, parent, chain=None):
        """Init SaveSearchDialog object."""

        super(SearchChainDialog, self).__init__(parent)
        self.localize()
        self.refresh_localization()

        self.m_chain_list.Bind(wx.EVT_LEFT_DCLICK, self.on_dclick)

        # Ensure good sizing of frame
        self.m_chain_panel.Fit()
        self.Fit()
        self.SetMinSize(self.GetSize())

        self.load_chains()
        self.m_chain_list.SetFocus()

    def localize(self):
        """Translate strings."""

        self.TITLE = _("Search Chains")
        self.ADD = _("Add")
        self.EDIT = _("Edit")
        self.DELETE = _("Delete")
        self.CLOSE = _("Cancel")

    def refresh_localization(self):
        """Localize."""

        self.SetTitle(self.TITLE)
        self.m_add_button.SetLabel(self.ADD)
        self.m_edit_button.SetLabel(self.EDIT)
        self.m_remove_button.SetLabel(self.DELETE)
        self.m_cancel_button.SetLabel(self.CLOSE)

    def load_chains(self):
        """Populate list with chain entries."""

        count = 0
        chains = Settings.get_chains()
        for key in sorted(chains.keys()):
            c = chains[key]
            searches = ';'.join(c)
            self.m_chain_list.set_item_map(count, key, searches)
            count += 1
        self.m_chain_list.load_list(True)

    def edit_chain(self, name=None):
        """Edit chain."""

        dlg = EditSearchChainDialog(self, chain=name)
        dlg.ShowModal()
        if dlg.saved:
            self.m_chain_list.reset_list()
            self.load_chains()
        dlg.Destroy()

    def on_remove_click(self, event):
        """Delete chain entry."""

        item = self.m_chain_list.GetFirstSelected()
        if item == -1:
            return
        name = self.m_chain_list.get_item_text(item, 0)
        Settings.delete_chain(name)
        self.m_chain_list.reset_list()
        self.load_chains()

    def on_edit_click(self, event):
        """Edit chain on button click."""

        item = self.m_chain_list.GetFirstSelected()
        if item == -1:
            return

        name = self.m_chain_list.get_item_text(item, 0)
        self.edit_chain(name)

    def on_add_click(self, event):
        """Add new chain."""

        self.edit_chain()

    def on_dclick(self, event):
        """Edit on double click."""

        pos = event.GetPosition()
        item = self.m_chain_list.HitTestSubItem(pos)[0]
        if item != -1:
            name = self.m_chain_list.GetItem(item, col=0).GetText()
            self.edit_chain(name)

    def on_cancel_click(self, event):
        """Close window."""

        self.Close()

    def on_close(self, event):
        """Handle on close event."""

        self.m_chain_list.destroy()
        event.Skip()
