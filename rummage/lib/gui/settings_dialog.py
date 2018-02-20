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
from .settings import Settings
from .editor_dialog import EditorDialog
from .file_ext_dialog import FileExtDialog
from .generic_dialogs import yesno, errormsg
from .localization import _
from . import gui
from .. import rumcore
from .. import util

# We really need a better validator
BACKUP_VALIDATOR = re.compile(r'^[-_a-zA-Z\d.]+$')

MINIMUM_COL_SIZE = 100
COLUMN_SAMPLE_SIZE = 100


class SettingsDialog(gui.SettingsDialog):
    """SettingsDialog."""

    def __init__(self, parent):
        """Init SettingsDialog object."""

        super(SettingsDialog, self).__init__(parent)
        if util.platform() == "windows":
            self.m_general_panel.SetDoubleBuffered(True)
            self.m_regex_panel.SetDoubleBuffered(True)
            self.m_editor_panel.SetDoubleBuffered(True)
            self.m_notify_panel.SetDoubleBuffered(True)
            self.m_history_panel.SetDoubleBuffered(True)
            self.m_backup_panel.SetDoubleBuffered(True)

        self.m_encoding_list.Bind(wx.EVT_LEFT_DCLICK, self.on_dclick)

        self.localize()

        self.history_types = [
            "target",
            "regex_search",
            "literal_search",
            "regex_folder_exclude",
            "folder_exclude",
            "regex_file_search",
            "file_search"
        ]
        history_records = Settings.get_history_record_count(self.history_types)
        self.history_records_cleared = False

        self.editor = Settings.get_editor()
        if isinstance(self.editor, (tuple, list)):
            self.m_editor_text.SetValue(" ".join(self.editor) if len(self.editor) != 0 else "")
        else:
            self.m_editor_text.SetValue(self.editor if self.editor else "")
        self.m_single_checkbox.SetValue(Settings.get_single_instance())
        self.m_history_label.SetLabel(self.RECORDS % history_records)
        self.m_history_clear_button.Enable(history_records > 0)
        mode = Settings.get_regex_mode()
        self.m_bregex_radio.SetValue(mode == rumcore.BREGEX_MODE)
        self.m_regex_radio.SetValue(mode == rumcore.REGEX_MODE)
        self.m_bre_radio.SetValue(mode == rumcore.BRE_MODE)
        self.m_re_radio.SetValue(mode == rumcore.RE_MODE)
        self.m_regex_ver_choice.SetSelection(Settings.get_regex_version())
        if Settings.is_regex_available():
            self.m_regex_radio.Enable(True)
            self.m_bregex_radio.Enable(True)
            self.m_regex_version_label.Enable(True)
            self.m_regex_ver_choice.Enable(True)
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
        self.m_regex_panel.Fit()
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
        """Translage strings."""

        self.TITLE = _("Preferences")
        self.GENERAL_TAB = _("General")
        self.REGEX_TAB = _("Regex")
        self.EDITOR_TAB = _("Editor")
        self.NOTIFICATIONS_TAB = _("Notifications")
        self.HISTORY_TAB = _("History")
        self.SINGLE_INSTANCE = _("Single Instance (applies to new instances)")
        self.NOTIFY_POPUP = _("Notification popup")
        self.ALERT = _("Alert Sound")
        self.TERM_NOTIFY_PATH = _("Path to terminal-notifier")
        self.LANGUAGE = _("Language (restart required)")
        self.RE = _("Use re module")
        self.BRE = _("Use re module with backrefs")
        self.REGEX = _("Use regex module")
        self.BREGEX = _("Use regex module with backrefs")
        self.REGEX_VER = _("Regex module version to use")
        self.CHANGE = _("Change")
        self.CLEAR = _("Clear")
        self.CLOSE = _("Close")
        self.SAVE = _("Save")
        self.RECORDS = _("%d Records")
        self.WARN_EDITOR_FORMAT = _(
            "Editor setting format has changed!\n\n"
            "Continuing will delete the old setting and require you to\n"
            "reconfigure the option in the new format.\n\n"
            "Ensure that you double quote paths and options with spaces,\n"
            "inlcuding options that contain '{$file}'.\n\n"
            "Example:\n"
            "\"/My path/to editor\" --flag --path \"{$file}:{$line}:{$col}\""
        )
        self.CONTINUE = _("Continue")
        self.CANCEL = _("Cancel")
        self.WARNING_TITLE = _("Warning: Format Change")
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

    def refresh_localization(self):
        """Localize dialog."""

        self.SetTitle(self.TITLE)
        self.m_settings_notebook.SetPageText(0, self.GENERAL_TAB)
        self.m_settings_notebook.SetPageText(1, self.REGEX_TAB)
        self.m_settings_notebook.SetPageText(2, self.ENCODING)
        self.m_settings_notebook.SetPageText(3, self.EDITOR_TAB)
        self.m_settings_notebook.SetPageText(4, self.NOTIFICATIONS_TAB)
        self.m_settings_notebook.SetPageText(5, self.HISTORY_TAB)
        self.m_single_checkbox.SetLabel(self.SINGLE_INSTANCE)
        self.m_visual_alert_checkbox.SetLabel(self.NOTIFY_POPUP)
        self.m_audio_alert_checkbox.SetLabel(self.ALERT)
        self.m_term_note_label.SetLabel(self.TERM_NOTIFY_PATH)
        self.m_language_label.SetLabel(self.LANGUAGE)
        self.m_re_radio.SetLabel(self.RE)
        self.m_bre_radio.SetLabel(self.BRE)
        self.m_regex_radio.SetLabel(self.REGEX)
        self.m_bregex_radio.SetLabel(self.BREGEX)
        self.m_regex_version_label.SetLabel(self.REGEX_VER)
        self.m_editor_button.SetLabel(self.CHANGE)
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

        encoding = Settings.get_chardet_mode()
        cchardet_available = Settings.is_cchardet_available()
        options = self.CHARDET_CHOICE if cchardet_available else self.CHARDET_CHOICE[:1]
        for x in options:
            self.m_encoding_choice.Append(x)
        self.m_encoding_choice.SetSelection(encoding)

        self.reload_list()

        self.Fit()

    def reload_list(self):
        """Reload list."""

        self.m_encoding_list.reset_list()
        encoding_ext = Settings.get_encoding_ext()
        keys = sorted(encoding_ext.keys())
        for key in keys:
            self.m_encoding_list.set_item_map(key, key, ', '.join(encoding_ext[key]))
        self.m_encoding_list.load_list(True)

    def history_cleared(self):
        """Return if history was cleared."""

        return self.history_records_cleared

    def on_chardet(self, event):
        """Handle chardet selection."""

        Settings.set_chardet_mode(self.m_encoding_choice.GetCurrentSelection())

    def on_check(self, event):
        """Check updates."""

        self.GetParent().update_request(Settings.get_prerelease())

    def on_editor_change(self, event):
        """Show editor dialog and update setting on return."""

        if isinstance(self.editor, (list, tuple)):
            # Using old format
            if not yesno(self.WARN_EDITOR_FORMAT, title=self.WARNING_TITLE, yes=self.CONTINUE, no=self.CANCEL):
                # Warn user about new format changes
                return
            else:
                # Clear old format
                self.editor = ""
                Settings.set_editor("")
                self.m_editor_text.SetValue("")

        dlg = EditorDialog(self, self.editor)
        dlg.ShowModal()
        self.editor = dlg.get_editor()
        Settings.set_editor(self.editor)
        self.m_editor_text.SetValue(self.editor)
        dlg.Destroy()
        event.Skip()

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

    def on_single_toggle(self, event):
        """Update if single instance is used."""

        Settings.set_single_instance(self.m_single_checkbox.GetValue())

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

        if self.m_bregex_radio.GetValue():
            mode = rumcore.BREGEX_MODE
        elif self.m_regex_radio.GetValue():
            mode = rumcore.REGEX_MODE
        elif self.m_bre_radio.GetValue():
            mode = rumcore.BRE_MODE
        else:
            mode = rumcore.RE_MODE
        Settings.set_regex_mode(mode)

    def on_close(self, event):
        """Handle on close event."""

        self.m_encoding_list.destroy()
        event.Skip()

    on_bregex_toggle = on_change_module

    on_regex_toggle = on_change_module

    on_bre_toggle = on_change_module

    on_re_toggle = on_change_module
