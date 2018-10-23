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
from .settings import Settings
from .generic_dialogs import errormsg, yesno
from .localization import _
from . import gui
from .. import util

RE_KEY = re.compile(r'[\w-]+')


class EditSearchChainDialog(gui.EditSearchChainDialog):
    """Edit search chain dialog."""

    def __init__(self, parent, chain=None):
        """Initialize dialog."""

        super(EditSearchChainDialog, self).__init__(parent)
        if util.platform() == "windows":
            self.SetDoubleBuffered(True)
        self.localize()

        self.saved = False
        self.search_count = 0
        self.load_searches()

        self.original_name = ""
        if chain:
            self.load_chain(chain)

        self.refresh_localization()

        # Ensure good sizing of frame
        self.m_chain_panel.Fit()
        self.Fit()
        self.SetMinSize(self.GetSize())

    def localize(self):
        """Translate strings."""

        self.TITLE = _("Edit/Create Search Chain")
        self.OVERWRITE = _("'%s' already exists. Overwrite?")
        self.ADD = _("Add")
        self.DELETE = _("Delete")
        self.UP = _("Up")
        self.DOWN = _('Down')
        self.OKAY = _('Apply')
        self.CLOSE = _('Cancel')
        self.NAME = _("Name")
        self.CHAIN = _("Chain")
        self.ERR_SEARCH_NOT_EXISTS = _("Search '%s' does not exist!")
        self.ERR_CHAIN_MISSING = _("Please specify a chain name!")
        self.ERR_CHAIN_FORMAT = _("Chain names can only contain Unicode word chars, '_', and '-'!")
        self.ERR_CHAIN_EMPTY = _("Chain must contain at least one search!")

    def refresh_localization(self):
        """Localize dialog."""

        self.SetTitle(self.TITLE)
        self.m_add_button.SetLabel(self.ADD)
        self.m_remove_button.SetLabel(self.DELETE)
        self.m_up_button.SetLabel(self.UP)
        self.m_down_button.SetLabel(self.DOWN)
        self.m_apply_button.SetLabel(self.OKAY)
        self.m_cancel_button.SetLabel(self.CLOSE)
        self.m_chain_panel.GetSizer().GetItem(0).GetSizer().GetStaticBox().SetLabel(self.NAME)
        self.m_chain_panel.GetSizer().GetItem(1).GetSizer().GetStaticBox().SetLabel(self.CHAIN)

    def load_searches(self):
        """Load search list in `wxChoice`."""

        searches = Settings.get_search()
        keys = list(searches.keys())
        self.search_count = len(keys)
        self.m_search_choice.Set(keys)
        if self.search_count:
            self.m_search_choice.SetSelection(0)
        self.keys = set(keys)

    def load_chain(self, chain):
        """Load an existing chain."""

        chains = Settings.get_chains()
        if chain in chains:
            self.original_name = chain
            self.m_chain_textbox.SetValue(chain)
            searches = chains[chain]
            for x in range(len(searches)):
                self.m_search_list.Insert(searches[x], x)

    def on_add_click(self, event):
        """Add search selection to list."""

        search = self.m_search_choice.GetSelection()
        if search != wx.NOT_FOUND:
            index = self.m_search_list.GetSelection()
            if index == wx.NOT_FOUND:
                self.m_search_list.Insert(
                    self.m_search_choice.GetString(search),
                    self.m_search_list.GetCount()
                )
            else:
                self.m_search_list.Insert(self.m_search_choice.GetString(search), index)

    def on_remove_click(self, event):
        """Remove search from chain."""

        index = self.m_search_list.GetSelection()
        selected = self.m_search_list.IsSelected(index)
        if index != wx.NOT_FOUND:
            self.m_search_list.Delete(index)
            count = self.m_search_list.GetCount()
            if selected and count and index <= count - 1:
                self.m_search_list.Select(index)

    def on_up_click(self, event):
        """Move up."""

        index = self.m_search_list.GetSelection()
        if index > 0:
            search = self.m_search_list.GetString(index)
            self.m_search_list.Delete(index)
            self.m_search_list.Insert(search, index - 1)
            self.m_search_list.Select(index - 1)

    def on_down_click(self, event):
        """Move up."""

        count = self.m_search_list.GetCount()
        index = self.m_search_list.GetSelection()
        if wx.NOT_FOUND < index < count - 1:
            search = self.m_search_list.GetString(index)
            self.m_search_list.Delete(index)
            self.m_search_list.Insert(search, index + 1)
            self.m_search_list.Select(index + 1)

    def on_apply_click(self, event):
        """Add/modify chain in list."""

        string = self.m_chain_textbox.GetValue()
        chains = Settings.get_chains()
        err = False

        if not string:
            errormsg(self.ERR_CHAIN_MISSING)
            err = True
        elif RE_KEY.match(string) is None:
            errormsg(self.ERR_CHAIN_FORMAT)
            err = True

        if not err and string in chains and string != self.original_name and not yesno(self.OVERWRITE % string):
            err = True

        searches = []
        for index in range(self.m_search_list.GetCount()):
            text = self.m_search_list.GetString(index)
            if text not in self.keys:
                errormsg(self.ERR_SEARCH_NOT_EXISTS % text)
                err = True
                break
            searches.append(text)

        if not err and not searches:
            errormsg(self.ERR_CHAIN_EMPTY)
            err = True

        if not err:
            if self.original_name and string != self.original_name:
                Settings.delete_chain(self.original_name)
            Settings.add_chain(string, searches)
            self.saved = True
            self.Close()

    def on_cancel_click(self, event):
        """Close dialog."""

        self.Close()
