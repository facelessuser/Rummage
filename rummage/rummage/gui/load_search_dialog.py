"""
Load Search Dialog.

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

from .settings import Settings
from . import gui
from ..localization import _

SEARCH_REGEX = _("Regex")
SEARCH_LITERAL = _("Text")
SEARCH_TYPE = {
    SEARCH_LITERAL: "Text",
    SEARCH_REGEX: "Regex"
}


class LoadSearchDialog(gui.LoadSearchDialog):
    """Load search dialog."""

    def __init__(self, parent):
        """Init LoadSearchDialog."""

        super(LoadSearchDialog, self).__init__(parent)

        self.parent = parent
        self.localize()

        best = self.m_load_panel.GetBestSize()
        current = self.m_load_panel.GetSize()
        offset = best[1] - current[1]
        mainframe = self.GetSize()
        self.SetSize(wx.Size(mainframe[0], mainframe[1] + offset + 15))
        self.SetMinSize(self.GetSize())

        self.load_searches()
        self.m_search_list.SetFocus()

    def localize(self):
        """Localize dialog."""

        self.SetTitle(_("Searches"))
        self.m_delete_button.SetLabel(_("Remove"))
        self.m_load_button.SetLabel(_("Load"))
        self.m_cancel_button.SetLabel(_("Cancel"))
        self.Fit()

    def load_searches(self):
        """Populate list with search entries."""

        count = 0
        for x in Settings.get_search():
            # TODO: Added with replace feature
            # remove some time in the future.
            # Also consider adding version number to properly upgrade
            # saves.
            if len(x) == 3:
                x.insert(2, '')
            if len(x) == 4:
                x.insert(3, '')
            search_type = SEARCH_REGEX if x[4] else SEARCH_LITERAL
            self.m_search_list.set_item_map(count, x[0], x[1], x[2], x[3], search_type)
            count += 1
        self.m_search_list.load_list()

    def on_load(self, event):
        """Select the search entry for use."""

        item = self.m_search_list.GetFirstSelected()
        if item == -1:
            return
        search = self.m_search_list.get_map_item(item, col=1)
        replace = self.m_search_list.get_map_item(item, col=2)
        flags = self.m_search_list.get_map_item(item, col=3)
        is_regex = SEARCH_TYPE[self.m_search_list.get_map_item(item, col=4)] == "Regex"

        self.parent.m_searchfor_textbox.SetValue(search)
        self.parent.m_replace_textbox.SetValue(replace)
        self.parent.m_regex_search_checkbox.SetValue(is_regex)
        self.parent.m_case_checkbox.SetValue("i" not in flags)
        self.parent.m_dotmatch_checkbox.SetValue("s" in flags)
        self.parent.m_unicode_checkbox.SetValue("u" in flags)
        self.parent.m_bestmatch_checkbox.SetValue("b" in flags)
        self.parent.m_enhancematch_checkbox.SetValue("e" in flags)
        self.parent.m_word_checkbox.SetValue("w" in flags)
        self.parent.m_reverse_checkbox.SetValue("r" in flags)
        self.parent.m_posix_checkbox.SetValue("p" in flags)
        self.parent.m_fullcase_checkbox.SetValue("f" in flags)
        self.parent.m_format_replace_checkbox.SetValue("F" in flags)

        self.Close()

    def on_delete(self, event):
        """Delete search entry."""

        item = self.m_search_list.GetFirstSelected()
        if item == -1:
            return
        idx = self.m_search_list.itemIndexMap[item]
        Settings.delete_search(idx)
        self.m_search_list.reset_list()
        self.load_searches()

    def on_cancel(self, event):
        """Close dialog."""

        self.Close()
