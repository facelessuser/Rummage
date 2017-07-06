"""
Save Search Dialog.

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
import re
from . import gui
from .settings import Settings, rumcore
from .generic_dialogs import errormsg, yesno
from ..localization import _
from .. import util

RE_NAME = re.compile(r'[\w-]', re.UNICODE)
OVERWRITE = _("'%s' already exists. Overwrite?")
ERR_NO_NAME = _("Please give the search a name!")
ERR_INVALID_NAME = _("Names can only be Unicode word characters, '_', and '-'")


class SaveSearchDialog(gui.SaveSearchDialog):
    """Save search dialog."""

    def __init__(self, parent, data=None):
        """Init SaveSearchDialog object."""

        super(SaveSearchDialog, self).__init__(parent)

        # Ensure OS selectall shortcut works in text inputs
        self.set_keybindings(
            [(wx.ACCEL_CMD if util.platform() == "osx" else wx.ACCEL_CTRL, ord('A'), self.on_textctrl_selectall)]
        )

        self.parent = parent
        self.saved = False

        self.original_name = ""
        if data:
            self.original_name = data[0]
        self.setup(data)

        self.localize()

        # Ensure good sizing for dialog
        best = self.m_save_panel.GetBestSize()
        current = self.m_save_panel.GetSize()
        offset = best[1] - current[1]
        mainframe = self.GetSize()
        self.SetSize(wx.Size(mainframe[0], mainframe[1] + offset + 15))
        self.SetMinSize(self.GetSize())
        self.m_name_text.SetFocus()

    def localize(self):
        """Localize the dialog."""

        self.SetTitle(_("Save Search and Replace"))
        self.m_apply_button.SetLabel(_("Save"))
        self.m_cancel_button.SetLabel(_("Cancel"))
        self.m_name_label.SetLabel(_("Name"))
        self.m_comment_label.SetLabel(_("Optional comment"))
        self.m_search_label.SetLabel(_("Search pattern"))
        self.m_replace_label.SetLabel(_("Replace pattern"))
        self.m_flags_label.SetLabel(_("Flags"))

        self.Fit()

    def setup(self, data):
        """Setup."""

        if data is not None:
            self.m_name_text.SetValue(data[0])
            self.m_comment_textbox.SetValue(data[1])
            self.m_search_textbox.SetValue(data[2])
            self.m_replace_textbox.SetValue(data[3])
            self.m_flags_textbox.SetValue(data[4])
            self.is_regex = data[5]
            self.is_plugin = data[6]
        else:
            self.m_search_textbox.SetValue(self.parent.m_searchfor_textbox.GetValue())
            self.m_replace_textbox.SetValue(self.parent.m_replace_textbox.GetValue())
            self.is_regex = self.parent.m_regex_search_checkbox.GetValue()
            self.is_plugin = self.parent.m_replace_plugin_checkbox.GetValue()
            flags = self.get_flag_string()
            self.m_flags_textbox.SetValue(flags)
        self.m_type_checkbox.SetValue(not self.is_regex)
        self.m_replace_plugin_checkbox.SetValue(self.is_plugin)

    def get_flag_string(self):
        """Get flags in a string representation."""

        flags = ""

        mode = Settings.get_regex_mode()
        version = Settings.get_regex_version()

        if not self.parent.m_case_checkbox.GetValue():
            flags += "i"
        if self.parent.m_unicode_checkbox.GetValue():
            flags += "u"
        if mode in rumcore.REGEX_MODES and version == 0 and self.parent.m_fullcase_checkbox.GetValue():
            flags += "f"

        if self.is_regex:
            if self.parent.m_dotmatch_checkbox.GetValue():
                flags += "s"
            if mode in rumcore.REGEX_MODES:
                if self.parent.m_bestmatch_checkbox.GetValue():
                    flags += "b"
                if self.parent.m_enhancematch_checkbox.GetValue():
                    flags += "e"
                if self.parent.m_word_checkbox.GetValue():
                    flags += "w"
                if self.parent.m_reverse_checkbox.GetValue():
                    flags += "r"
                if self.parent.m_posix_checkbox.GetValue():
                    flags += "p"
                if self.parent.m_format_replace_checkbox.GetValue():
                    flags += "F"
        return flags

    def set_keybindings(self, keybindings):
        """Set keybindings for frame."""

        tbl = []
        for binding in keybindings:
            keyid = wx.NewId()
            self.Bind(wx.EVT_MENU, binding[2], id=keyid)
            tbl.append((binding[0], binding[1], keyid))

        if len(keybindings):
            self.SetAcceleratorTable(wx.AcceleratorTable(tbl))

    def on_textctrl_selectall(self, event):
        """Selectall content of textctrl."""

        text = self.FindFocus()
        if isinstance(text, wx.TextCtrl):
            text.SelectAll()
        event.Skip()

    def on_apply(self, event):
        """Ensure there is a name, and proceed to add saved regex to settings."""

        name = self.m_name_text.GetValue()
        if name == "":
            errormsg(ERR_NO_NAME)
            return

        if RE_NAME.match(name) is None:
            errormsg(ERR_INVALID_NAME)
            return

        if name in Settings.get_search() and name != self.original_name and not yesno(OVERWRITE % name):
            return

        comment = self.m_comment_textbox.GetValue()
        search = self.m_search_textbox.GetValue()
        replace = self.m_replace_textbox.GetValue()
        flags = self.m_flags_textbox.GetValue()

        if self.original_name and name != self.original_name:
            Settings.delete_search(self.original_name)

        Settings.add_search(name, comment, search, replace, flags, self.is_regex, self.is_plugin)
        self.saved = True
        self.Close()

    def on_toggle(self, event):
        """Prevent toggling."""

        obj = event.GetEventObject()
        obj.SetValue(not obj.GetValue())

    def on_cancel(self, event):
        """Close dialog."""

        self.Close()
