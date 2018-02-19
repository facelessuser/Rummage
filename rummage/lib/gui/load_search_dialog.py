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
from .localization import _
from .save_search_dialog import SaveSearchDialog
from . import gui


class LoadSearchDialog(gui.LoadSearchDialog):
    """Load search dialog."""

    def __init__(self, parent):
        """Init LoadSearchDialog."""

        super(LoadSearchDialog, self).__init__(parent)
        self.localize()
        self.refresh_localization()

        self.m_search_list.Bind(wx.EVT_LEFT_DCLICK, self.on_dclick)
        self.parent = parent

        self.m_load_panel.Fit()
        self.Fit()
        self.SetMinSize(self.GetSize())

        self.load_searches()
        self.m_search_list.SetFocus()

    def localize(self):
        """Translate strings."""

        self.TITLE = _("Searches")
        self.REMOVE = _("Remove")
        self.OKAY = _("Load")
        self.CLOSE = _("Cancel")

        self.SEARCH_REGEX = _("Regex")
        self.SEARCH_LITERAL = _("Text")
        self.SEARCH_TYPE = {
            self.SEARCH_LITERAL: "Text",
            self.SEARCH_REGEX: "Regex"
        }

        self.REPLACE_PATTERN = _("Pattern")
        self.REPLACE_PLUGIN = _("Plugin")
        self.REPLACE_TYPE = {
            self.REPLACE_PATTERN: "Pattern",
            self.REPLACE_PLUGIN: "Plugin"
        }

    def refresh_localization(self):
        """Localize dialog."""

        self.SetTitle(self.TITLE)
        self.m_delete_button.SetLabel(self.REMOVE)
        self.m_load_button.SetLabel(self.OKAY)
        self.m_cancel_button.SetLabel(self.CLOSE)
        self.Fit()

    def load_searches(self):
        """Populate list with search entries."""

        count = 0
        searches = Settings.get_search()
        for key in sorted(searches.keys()):
            s = searches[key]
            search_type = self.SEARCH_REGEX if s['is_regex'] else self.SEARCH_LITERAL
            replace_type = self.REPLACE_PLUGIN if s['is_function'] else self.REPLACE_PATTERN
            self.m_search_list.set_item_map(
                count,
                key,
                s['name'],
                s['search'],
                s['replace'],
                s['flags'],
                search_type,
                replace_type
            )
            count += 1
        self.m_search_list.load_list(True)

    def edit(self, item):
        """Edit the saved search."""

        name = self.m_search_list.get_map_item(item, col=0)
        comment = self.m_search_list.get_map_item(item, col=1)
        search = self.m_search_list.get_map_item(item, col=2)
        replace = self.m_search_list.get_map_item(item, col=3)
        flags = self.m_search_list.get_map_item(item, col=4)
        is_regex = self.SEARCH_TYPE[self.m_search_list.get_map_item(item, col=5)] == "Regex"
        is_plugin = self.REPLACE_TYPE[self.m_search_list.get_map_item(item, col=6)] == "Plugin"

        dlg = SaveSearchDialog(self, (name, comment, search, replace, flags, is_regex, is_plugin))
        dlg.ShowModal()
        if dlg.saved:
            self.m_search_list.reset_list()
            self.load_searches()
        dlg.Destroy()

    def on_load(self, event):
        """Select the search entry for use."""

        item = self.m_search_list.GetFirstSelected()
        if item == -1:
            return
        search = self.m_search_list.get_map_item(item, col=2)
        replace = self.m_search_list.get_map_item(item, col=3)
        flags = self.m_search_list.get_map_item(item, col=4)
        is_regex = self.SEARCH_TYPE[self.m_search_list.get_map_item(item, col=5)] == "Regex"
        is_plugin = self.REPLACE_TYPE[self.m_search_list.get_map_item(item, col=6)] == "Plugin"

        # Disable chain mode if enabled
        if self.parent.m_chains_checkbox.GetValue():
            self.parent.m_chains_checkbox.SetValue(False)
            self.parent.on_chain_toggle(None)

        if self.parent.m_replace_plugin_checkbox.GetValue() != is_plugin:
            self.parent.m_replace_plugin_checkbox.SetValue(is_plugin)
            self.parent.on_plugin_function_toggle(None)

        if self.parent.m_regex_search_checkbox.GetValue() != is_regex:
            self.parent.m_regex_search_checkbox.SetValue(is_regex)
            self.parent.on_regex_search_toggle(None)

        self.parent.m_searchfor_textbox.SetValue(search)
        self.parent.m_replace_textbox.SetValue(replace)
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
        name = self.m_search_list.get_item_text(item, 0)
        Settings.delete_search(name)
        self.m_search_list.reset_list()
        self.load_searches()

    def on_edit_click(self, event):
        """Edit on button click."""

        item = self.m_search_list.GetFirstSelected()
        if item != -1:
            self.edit(item)

    def on_dclick(self, event):
        """Edit saved search on double click (just name and comment)."""

        pos = event.GetPosition()
        item = self.m_search_list.HitTestSubItem(pos)[0]
        if item != -1:
            self.edit(item)

    def on_cancel(self, event):
        """Close dialog."""

        self.Close()

    def on_close(self, event):
        """Handle on close event."""

        self.m_search_list.destroy()
        event.Skip()
