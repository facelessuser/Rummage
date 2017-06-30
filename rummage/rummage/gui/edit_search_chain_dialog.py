"""
Edit Search chain dialog.

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
import re
from . import gui
from .settings import Settings
from ..localization import _
from .custom_app import error
from .generic_dialogs import errormsg, yesno

RE_KEY = re.compile(r'[\w-]+')
OVERWRITE = _("'%s' already exists. Overwrite?")
ERR_SEARCH_NOT_EXISTS = _("Search '%s' does not exist!")
ERR_CHAIN_MISSING = _("Please specify a chain name!")
ERR_CHAIN_FORMAT = _("Chain names can only contain Unicode word chars, '_', and '-'!")
ERR_CHAIN_EMPTY = _("Chain must contain at least one search!")


class EditSearchChainDialog(gui.EditSearchChainDialog):
    """Edit search chain dialog."""

    def __init__(self, parent, chain=None):
        """Init SaveSearchDialog object."""

        super(EditSearchChainDialog, self).__init__(parent)
        self.m_search_list.AppendColumn('searches')

        self.search_count = 0
        self.load_searches()
        self.m_search_list.setResizeColumn(0)

        if chain:
            self.load_chain(chain)
            self.original_name = chain
        else:
            self.original_name = ""

        # Ensure good sizing of frame
        best = self.m_chain_panel.GetBestSize()
        current = self.m_chain_panel.GetSize()
        offset = best[1] - current[1]
        mainframe = self.GetSize()
        self.SetSize(wx.Size(mainframe[0], mainframe[1] + offset + 15))
        self.SetMinSize(self.GetSize())

    def load_searches(self):
        """Load search list in wxChoice."""

        searches = Settings.get_search()
        keys = list(searches.keys())
        self.search_count = len(keys)
        self.m_search_choice.Set(keys)
        if self.search_count:
            self.m_search_choice.SetSelection(0)
        self.keys = set(keys)

    def load_chain(self, chain):
        """Load an existing chain."""

    def on_add_click(self, event):
        """Add search selection to list."""

        search = self.m_search_choice.GetSelection()
        if search != wx.NOT_FOUND:
            index = self.m_search_list.GetFirstSelected()
            if index == wx.NOT_FOUND:
                self.m_search_list.InsertItem(
                    self.m_search_list.GetItemCount(),
                    self.m_search_choice.GetString(search)
                )
            else:
                self.m_search_list.InsertItem(index, self.m_search_choice.GetString(search))

    def on_remove_click(self, event):
        """Remove search from chain."""

        index = self.m_search_list.GetFirstSelected()
        selected = self.m_search_list.IsSelected(index)
        if index != wx.NOT_FOUND:
            self.m_search_list.DeleteItem(index)
            count = self.m_search_list.GetItemCount()
            if selected and count and index <= count - 1:
                self.m_search_list.Select(index)

    def on_up_click(self, event):
        """Move up."""

        index = self.m_search_list.GetFirstSelected()
        if index > 0:
            search = self.m_search_list.GetItemText(index)
            self.m_search_list.DeleteItem(index)
            self.m_search_list.InsertItem(index - 1, search)
            self.m_search_list.Select(index - 1)

    def on_down_click(self, event):
        """Move up."""

        count = self.m_search_list.GetItemCount()
        index = self.m_search_list.GetFirstSelected()
        print(index)
        if wx.NOT_FOUND < index < count - 1:
            search = self.m_search_list.GetItemText(index)
            self.m_search_list.DeleteItem(index)
            self.m_search_list.InsertItem(index + 1, search)
            self.m_search_list.Select(index + 1)

    def on_apply_click(self, event):
        """Add/modify chain in list."""

        string = self.m_chain_textbox.GetValue()
        chains = Settings.get_chains()
        err = False

        if not string:
            errormsg(ERR_CHAIN_MISSING)
            err = True
        elif RE_KEY.match(string) is None:
            errormsg(ERR_CHAIN_FORMAT)
            err = True

        if not err and string in chains and string != self.original_name and not yesno(OVERWRITE % string):
            err = True

        searches = []
        for index in range(self.m_search_list.GetItemCount()):
            text = self.m_search_list.GetItemText(index)
            if text not in self.keys:
                errormsg(ERR_SEARCH_NOT_EXISTS % text)
                err = True
                break
            searches.append(text)

        if not err and not searches:
            errormsg(ERR_CHAIN_EMPTY)
            err = True

        if not err:
            Settings.add_chain(string, searches)
            self.Close()

    def on_cancel_click(self, event):
        """Close dialog."""

        self.Close()
