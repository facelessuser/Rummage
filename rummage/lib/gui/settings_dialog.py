"""
Settings Dialog.

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
import json
from .settings import Settings
from .file_ext_dialog import FileExtDialog
from .generic_dialogs import errormsg
from .localization import _
from . import gui
from . import notify
from .. import rumcore
from .. import util
from .controls import webview

EDITOR_HELP = _("""
Enter in the appropriate command to open files in your editor.
Double quote paths with spaces and parameters that *may* contain spaces after substitution.

Use the following variables for parameter substitution:

Variable | Description
-------- | -----------
`{$file}`| Insert the file path.
`{$line}`| Insert the line number.
`{$col}` | Insert the line column.

!!! example "Example"

    ```bash
    "C:\\Program Files\\Sublime Text 3\\subl.exe" "{$file}:{$line}:{$col}"
    ```
""")

# We really need a better validator
BACKUP_VALIDATOR = re.compile(r'^[-_a-zA-Z\d.]+$')

MINIMUM_COL_SIZE = 100
COLUMN_SAMPLE_SIZE = 100


class SettingsDialog(webview.WebViewMixin, gui.SettingsDialog):
    """Settings dialog."""

    def __init__(self, parent):
        """Initialize settings dialog object."""

        super(SettingsDialog, self).__init__(parent)
        self.setup_html(self.m_help_html)
        if util.platform() == "windows":
            self.m_general_panel.SetDoubleBuffered(True)
            self.m_search_panel.SetDoubleBuffered(True)
            self.m_editor_panel.SetDoubleBuffered(True)
            self.m_notify_panel.SetDoubleBuffered(True)
            self.m_history_panel.SetDoubleBuffered(True)
            self.m_backup_panel.SetDoubleBuffered(True)

        self.m_encoding_list.Bind(wx.EVT_LEFT_DCLICK, self.on_dclick)

        self.localize()

        # Ensure OS platform select all shortcut works
        self.set_keybindings(
            [(wx.ACCEL_CMD if util.platform() == "osx" else wx.ACCEL_CTRL, ord('A'), self.on_textctrl_selectall)]
        )

        self.history_types = [
            "target",
            "regex_search",
            "literal_search",
            "regex_folder_exclude",
            "folder_exclude",
            "regex_file_search",
            "file_search",
            "replace_plugin"
        ]
        history_records = Settings.get_history_record_count(self.history_types)
        self.history_records_cleared = False

        self.editor = Settings.get_editor()
        if isinstance(self.editor, (tuple, list)):
            self.m_editor_text.SetValue(" ".join(self.editor) if len(self.editor) != 0 else "")
        else:
            self.m_editor_text.SetValue(self.editor if self.editor else "")
        self.m_single_checkbox.SetValue(Settings.get_single_instance())
        self.m_time_output_checkbox.SetValue(Settings.get_international_time())
        self.m_history_label.SetLabel(self.RECORDS % history_records)
        self.m_cache_textbox.SetValue(self.get_history())
        self.m_history_clear_button.Enable(history_records > 0)
        mode = Settings.get_regex_mode()
        self.m_regex_radio.SetValue(mode in rumcore.REGEX_MODES)
        self.m_re_radio.SetValue(mode in rumcore.RE_MODES)
        self.m_regex_ver_choice.SetSelection(Settings.get_regex_version())
        self.m_backrefs_checkbox.SetValue(mode in rumcore.BACKREFS_MODES)
        if Settings.is_regex_available():
            self.m_regex_radio.Enable(True)
            self.m_regex_ver_choice.Enable(True)
        self.m_extmatch_checkbox.SetValue(Settings.get_extmatch())
        self.m_brace_checkbox.SetValue(Settings.get_brace_expansion())
        self.m_case_checkbox.SetValue(Settings.get_file_case_sensitive())
        self.m_fullpath_checkbox.SetValue(Settings.get_full_exclude_path())
        self.m_fullfile_checkbox.SetValue(Settings.get_full_file_path())
        self.m_globstar_checkbox.SetValue(Settings.get_globstar())
        self.m_matchbase_checkbox.SetValue(Settings.get_matchbase())
        self.m_visual_alert_checkbox.SetValue(Settings.get_notify())
        self.m_audio_alert_checkbox.SetValue(Settings.get_alert())
        self.alert_methods = Settings.get_platform_notify()
        self.m_notify_choice.Clear()
        for a in self.alert_methods:
            self.m_notify_choice.Append(a)
        self.m_notify_choice.SetStringSelection(Settings.get_notify_method())
        self.m_lang_choice.Clear()
        for l in Settings.get_languages():
            self.m_lang_choice.Append(l)
        locale = Settings.get_language()
        if locale is None:
            locale = "en_US"
        self.m_lang_choice.SetStringSelection(locale)
        self.m_term_note_picker.SetPath(Settings.get_term_notifier())
        if util.platform() != "osx":
            self.m_term_note_label.Hide()
            self.m_term_note_picker.Hide()
        else:
            is_native = Settings.get_notify_method() == "default"
            self.m_term_note_label.Enable(is_native)
            self.m_term_note_picker.Enable(is_native)

        self.backup_ext = Settings.get_backup_ext()
        self.backup_folder = Settings.get_backup_folder()
        self.m_back_ext_textbox.SetValue(self.backup_ext)
        self.m_back_folder_textbox.SetValue(self.backup_folder)
        self.m_back2folder_checkbox.SetValue(bool(Settings.get_backup_type()))
        self.m_back_ext_button.Enable(False)
        self.m_back_folder_button.Enable(False)
        self.m_update_checkbox.SetValue(bool(Settings.get_check_updates()))
        self.m_prerelease_checkbox.SetValue(bool(Settings.get_prerelease()))

        self.refresh_localization()

        self.m_general_panel.Fit()
        self.m_search_panel.Fit()
        self.m_encoding_panel.Fit()
        self.m_editor_panel.Fit()
        self.m_notify_panel.Fit()
        self.m_history_panel.Fit()
        self.m_backup_panel.Fit()
        self.m_settings_notebook.Fit()
        self.m_settings_panel.Fit()
        self.Fit()
        if self.GetSize()[1] < 550:
            self.SetSize(wx.Size(550, self.GetSize()[1]))
        self.SetMinSize(wx.Size(550, self.GetSize()[1]))

    def localize(self):
        """Translate strings."""

        self.TITLE = _("Preferences")
        self.GENERAL_TAB = _("General")
        self.SEARCH_TAB = _("Search")
        self.EDITOR_TAB = _("Editor")
        self.NOTIFICATIONS_TAB = _("Notifications")
        self.HISTORY_TAB = _("History")
        self.SINGLE_INSTANCE = _("Single Instance (applies to new instances)")
        self.INTERNATIONAL_TIME = _("International time format for file results")
        self.NOTIFY_TEST_TITLE = _("Rummage Test")
        self.NOTIFY_TEST_MSG = _("Test complete!")
        self.NOTIFY_POPUP = _("Notification popup")
        self.ALERT = _("Alert Sound")
        self.TERM_NOTIFY_PATH = _("Path to terminal-notifier")
        self.TEST = _("Test")
        self.LANGUAGE = _("Language (restart required)")
        self.EXTMATCH = _("Extended match")
        self.BRACES = _("Brace expansion")
        self.CASE = _("Case sensitive")
        self.FULL_PATH = _("Full path directory match")
        self.FULL_FILE = _("Full path file match")
        self.GLOBSTAR = _("Globstar (full path)")
        self.MATCHBASE = _("Match base (full path)")
        self.REGEX_GROUP = _("Regular Expressions")
        self.FILE_MATCH_GROUP = _("File/Folder Matching")
        self.RE = _("Use Re module")
        self.REGEX = _("Use Regex module")
        self.BACKREFS = _("Enable Backrefs")
        self.CLEAR = _("Clear")
        self.CLOSE = _("Close")
        self.SAVE = _("Save")
        self.RECORDS = _("%d Records")
        self.BACK_EXT = _("Backup extension")
        self.BACK_FOLDER = _("Backup folder")
        self.BACK_2_FOLDER = _("Backup to folder")
        self.ERR_INVALID_EXT = _(
            "Invalid extension! Please enter a valid extension.\n\n"
            "Extensions must be alphanumeric and can contain\n"
            "hypens, underscores, and dots."
        )
        self.ERR_INVALID_FOLDER = _(
            "Invalid folder! Please enter a valid folder.\n\n"
            "Folders must be alphanumeric and can contain\n"
            "hypens, underscores, and dots."
        )
        self.CHECK_UPDATES = _("Check updates daily")
        self.PRERELEASES = _("Include pre-releases")
        self.CHECK_NOW = _("Check now")
        self.ENCODING = _("Encoding")
        self.CHARDET_CHOICE = [
            _("Fastest"),
            _("chardet (pure python)"),
            _("cchardet (C)")
        ]
        self.SPECIAL = _("Special file types:")
        self.EDITOR_HELP = EDITOR_HELP

    def refresh_localization(self):
        """Localize dialog."""

        self.SetTitle(self.TITLE)
        self.m_settings_notebook.SetPageText(0, self.GENERAL_TAB)
        self.m_settings_notebook.SetPageText(1, self.SEARCH_TAB)
        self.m_settings_notebook.SetPageText(2, self.ENCODING)
        self.m_settings_notebook.SetPageText(3, self.EDITOR_TAB)
        self.m_settings_notebook.SetPageText(4, self.NOTIFICATIONS_TAB)
        self.m_settings_notebook.SetPageText(5, self.HISTORY_TAB)
        self.m_search_panel.GetSizer().GetItem(0).GetSizer().GetStaticBox().SetLabel(self.REGEX_GROUP)
        self.m_search_panel.GetSizer().GetItem(1).GetSizer().GetStaticBox().SetLabel(self.FILE_MATCH_GROUP)
        self.m_single_checkbox.SetLabel(self.SINGLE_INSTANCE)
        self.m_time_output_checkbox.SetLabel(self.INTERNATIONAL_TIME)
        self.m_visual_alert_checkbox.SetLabel(self.NOTIFY_POPUP)
        self.m_audio_alert_checkbox.SetLabel(self.ALERT)
        self.m_term_note_label.SetLabel(self.TERM_NOTIFY_PATH)
        self.m_notify_test_button.SetLabel(self.TEST)
        self.m_language_label.SetLabel(self.LANGUAGE)
        self.m_re_radio.SetLabel(self.RE)
        self.m_regex_radio.SetLabel(self.REGEX)
        self.m_backrefs_checkbox.SetLabel(self.BACKREFS)
        self.m_extmatch_checkbox.SetLabel(self.EXTMATCH)
        self.m_brace_checkbox.SetLabel(self.BRACES)
        self.m_case_checkbox.SetLabel(self.CASE)
        self.m_fullpath_checkbox.SetLabel(self.FULL_PATH)
        self.m_fullfile_checkbox.SetLabel(self.FULL_FILE)
        self.m_globstar_checkbox.SetLabel(self.GLOBSTAR)
        self.m_matchbase_checkbox.SetLabel(self.MATCHBASE)
        self.m_editor_button.SetLabel(self.SAVE)
        self.m_history_clear_button.SetLabel(self.CLEAR)
        self.m_back_ext_label.SetLabel(self.BACK_EXT)
        self.m_back_folder_label.SetLabel(self.BACK_FOLDER)
        self.m_back2folder_checkbox.SetLabel(self.BACK_2_FOLDER)
        self.m_close_button.SetLabel(self.CLOSE)
        self.m_back_ext_button.SetLabel(self.SAVE)
        self.m_back_folder_button.SetLabel(self.SAVE)
        self.m_update_checkbox.SetLabel(self.CHECK_UPDATES)
        self.m_prerelease_checkbox.SetLabel(self.PRERELEASES)
        self.m_check_update_button.SetLabel(self.CHECK_NOW)
        self.m_filetype_label.SetLabel(self.SPECIAL)

        self.load_help(self.EDITOR_HELP)

        encoding = Settings.get_chardet_mode()
        cchardet_available = Settings.is_cchardet_available()
        options = self.CHARDET_CHOICE if cchardet_available else self.CHARDET_CHOICE[:1]
        for x in options:
            self.m_encoding_choice.Append(x)
        self.m_encoding_choice.SetSelection(encoding)

        self.reload_list()

        self.Fit()

    def load_help(self, text):
        """Handle copy event."""

        self.load_html(self.m_help_html, text, 'Editor Settings', webview.MARKDOWN_STRING)

    def set_keybindings(self, keybindings):
        """Set key bindings for frame."""

        tbl = []
        for binding in keybindings:
            keyid = wx.NewId()
            self.Bind(wx.EVT_MENU, binding[2], id=keyid)
            tbl.append((binding[0], binding[1], keyid))

        if len(keybindings):
            self.SetAcceleratorTable(wx.AcceleratorTable(tbl))

    def on_textctrl_selectall(self, event):
        """Select all for `TextCtrl`."""

        text = self.FindFocus()
        if isinstance(text, wx.TextCtrl):
            text.SelectAll()
        event.Skip()

    def reload_list(self):
        """Reload list."""

        self.m_encoding_list.reset_list()
        encoding_ext = Settings.get_encoding_ext()
        keys = sorted(encoding_ext.keys())
        for key in keys:
            self.m_encoding_list.set_item_map(key, key, ', '.join(encoding_ext[key]))
        self.m_encoding_list.load_list(True)

    def get_history(self):
        """Get history for display."""

        return json.dumps(
            Settings.get_history(self.history_types),
            sort_keys=True,
            indent=4,
            separators=(',', ': ')
        ) + '\n'

    def history_cleared(self):
        """Return if history was cleared."""

        return self.history_records_cleared

    def on_chardet(self, event):
        """Handle `chardet` selection."""

        Settings.set_chardet_mode(self.m_encoding_choice.GetCurrentSelection())

    def on_check(self, event):
        """Check updates."""

        self.GetParent().on_check_update(event)

    def on_editor_changed(self, event):
        """Handle on editor changed."""

        self.m_editor_button.Enable(self.m_editor_text.GetValue() != self.editor)

    def on_editor_change(self, event):
        """Show editor dialog and update setting on return."""

        self.editor = self.m_editor_text.GetValue()
        Settings.set_editor(self.editor)
        self.m_editor_text.SetValue(self.editor)

    def on_update_toggle(self, event):
        """Update toggle."""

        Settings.set_check_updates(self.m_update_checkbox.GetValue())
        event.Skip()

    def on_prerelease_toggle(self, event):
        """Prerelease toggle."""

        Settings.set_prerelease(self.m_prerelease_checkbox.GetValue())
        event.Skip()

    def on_clear_history(self, event):
        """Clear history."""

        Settings.clear_history_records(self.history_types)
        self.history_records_cleared = True
        self.m_cache_textbox.SetValue(self.get_history())
        self.m_history_label.SetLabel(self.RECORDS % 0)
        self.m_history_clear_button.Enable(False)

    def on_term_note_change(self, event):
        """Update term path."""

        Settings.set_term_notifier(self.m_term_note_picker.GetPath())

    def on_notify_choice(self, event):
        """Update notify method."""

        string_choice = self.m_notify_choice.GetStringSelection()
        is_native = string_choice == "default"
        if util.platform() == "osx":
            self.m_term_note_picker.Enable(is_native)
            self.m_term_note_label.Enable(is_native)
        Settings.set_notify_method(self.m_notify_choice.GetStringSelection())
        event.Skip()

    def on_notify_toggle(self, event):
        """Update whether notifications are used."""

        Settings.set_notify(self.m_visual_alert_checkbox.GetValue())
        event.Skip()

    def on_alert_toggle(self, event):
        """Update if alert sound is used."""

        Settings.set_alert(self.m_audio_alert_checkbox.GetValue())
        event.Skip()

    def on_notify_test_click(self, event):
        """Handle notification test."""

        if Settings.get_notify():
            notify.info(
                self.NOTIFY_TEST_TITLE,
                self.NOTIFY_TEST_MSG,
                sound=Settings.get_alert()
            )
        elif Settings.get_alert():
            notify.play_alert()

        event.Skip()

    def on_single_toggle(self, event):
        """Update if single instance is used."""

        Settings.set_single_instance(self.m_single_checkbox.GetValue())

    def on_time_output_toggle(self, event):
        """Update international time output."""

        itime = self.m_time_output_checkbox.GetValue()
        Settings.set_international_time(itime)
        self.GetParent().set_international_time_output(itime)

    def on_language(self, event):
        """Set selected on_language."""

        value = self.m_lang_choice.GetStringSelection()
        Settings.set_language(value)
        event.Skip()

    def on_regex_ver_choice(self, event):
        """Set regex version."""

        Settings.set_regex_version(self.m_regex_ver_choice.GetSelection())

    def on_back_ext_click(self, event):
        """Handle on change ext."""

        value = self.m_back_ext_textbox.GetValue()
        if value and value not in ('.', '..') and BACKUP_VALIDATOR.match(value) is not None:
            Settings.set_backup_ext(value)
            self.backup_ext = value
            self.m_back_ext_button.Enable(False)
        else:
            errormsg(self.ERR_INVALID_EXT)

    def on_back_folder_click(self, event):
        """Handle on change ext."""

        value = self.m_back_folder_textbox.GetValue()
        if value and value not in ('.', '..') and BACKUP_VALIDATOR.match(value) is not None:
            Settings.set_backup_folder(value)
            self.backup_folder = value
            self.m_back_ext_button.Enable(False)
        else:
            errormsg(self.ERR_INVALID_FOLDER)

    def on_back_ext_changed(self, event):
        """Handle text change event."""

        self.m_back_ext_button.Enable(self.m_back_ext_textbox.GetValue() != self.backup_ext)

    def on_back_folder_changed(self, event):
        """Handle text change event."""

        self.m_back_folder_button.Enable(self.m_back_folder_textbox.GetValue() != self.backup_folder)

    def on_back2folder_toggle(self, event):
        """Handle on change folder."""

        Settings.set_backup_type(int(self.m_back2folder_checkbox.GetValue()))

    def on_cancel(self, event):
        """Close on cancel."""

        self.Close()

    def on_dclick(self, event):
        """Handle double click."""

        pos = event.GetPosition()
        item = self.m_encoding_list.HitTestSubItem(pos)[0]
        if item != -1:
            key = self.m_encoding_list.GetItemText(item, 0)
            extensions = self.m_encoding_list.GetItemText(item, 1)
            dlg = FileExtDialog(self, extensions)
            dlg.ShowModal()
            value = dlg.extensions
            dlg.Destroy()
            if extensions != value:
                Settings.set_encoding_ext({key: value.split(', ')})
                self.m_encoding_list.SetItem(item, 1, value)
                self.reload_list()
        event.Skip()

    def on_change_module(self, event):
        """Change the module."""

        if self.m_regex_radio.GetValue():
            if self.m_backrefs_checkbox.GetValue():
                mode = rumcore.BREGEX_MODE
            else:
                mode = rumcore.REGEX_MODE
        elif self.m_backrefs_checkbox.GetValue():
            mode = rumcore.BRE_MODE
        else:
            mode = rumcore.RE_MODE
        Settings.set_regex_mode(mode)

    def on_extmatch_toggle(self, event):
        """Handle `extmatch` toggle."""

        Settings.set_extmatch(self.m_extmatch_checkbox.GetValue())

    def on_brace_toggle(self, event):
        """Handle brace toggle."""

        Settings.set_brace_expansion(self.m_brace_checkbox.GetValue())

    def on_case_toggle(self, event):
        """Handle case toggle."""

        Settings.set_file_case_sensitive(self.m_case_checkbox.GetValue())

    def on_fullpath_toggle(self, event):
        """Handle full path toggle."""

        Settings.set_full_exclude_path(self.m_fullpath_checkbox.GetValue())

    def on_fullfile_toggle(self, event):
        """Handle full file toggle."""

        Settings.set_full_file_path(self.m_fullfile_checkbox.GetValue())

    def on_globstar_toggle(self, event):
        """Handle globstar toggle."""

        Settings.set_globstar(self.m_globstar_checkbox.GetValue())

    def on_matchbase_toggle(self, event):
        """Handle `matchbase` toggle."""

        Settings.set_matchbase(self.m_matchbase_checkbox.GetValue())

    def on_close(self, event):
        """Handle on close event."""

        self.m_encoding_list.destroy()
        event.Skip()

    on_regex_toggle = on_change_module

    on_re_toggle = on_change_module

    on_backrefs_toggle = on_change_module
