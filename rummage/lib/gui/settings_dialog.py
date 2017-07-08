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
from .settings import Settings
from .editor_dialog import EditorDialog
from .localization import _
from . import gui
from .. import rumcore
from .. import util

TITLE = _("Preferences")
EDITOR = _("Editor")
GENERAL = _("General")
REGEX_MODULES = _("Regular Expression Modules")
NOTIFICATIONS = _("Notifications")
HISTORY = _("History")
SINGLE_INSTANCE = _("Single Instance (applies to new instances)")
NOTIFY_POPUP = _("Notification popup")
ALERT = _("Alert Sound")
TERM_NOTIFY_PATH = _("Path to terminal-notifier")
LANGUAGE = _("Language (restart required)")
RE = _("Use re module")
BRE = _("Use re module with backrefs")
REGEX = _("Use regex module")
BREGEX = _("Use regex module with backrefs")
REGEX_VER = _("Regex module version to use")
CHANGE = _("Change")
CLEAR = _("Clear")
CLOSE = _("Close")
RECORDS = _("%d Records")


class SettingsDialog(gui.SettingsDialog):
    """SettingsDialog."""

    def __init__(self, parent):
        """Init SettingsDialog object."""

        super(SettingsDialog, self).__init__(parent)

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
        mode = Settings.get_regex_mode()

        self.editor = Settings.get_editor()
        self.m_editor_text.SetValue(" ".join(self.editor) if len(self.editor) != 0 else "")
        self.m_single_checkbox.SetValue(Settings.get_single_instance())
        self.m_history_label.SetLabel(RECORDS % history_records)
        self.m_history_clear_button.Enable(history_records > 0)
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
        if util.platform() == "osx":
            is_native = Settings.get_notify_method() == "default"
            self.m_term_note_label.Show()
            self.m_term_note_picker.Show()
            self.m_term_note_label.Enable(is_native)
            self.m_term_note_picker.Enable(is_native)

        self.localize()

        best = self.m_settings_panel.GetBestSize()
        current = self.m_settings_panel.GetSize()
        offset = best[1] - current[1]
        mainframe = self.GetSize()
        self.SetSize(wx.Size(mainframe[0], mainframe[1] + offset + 15))
        self.SetMinSize(self.GetSize())

    def localize(self):
        """Localize dialog."""

        self.SetTitle(TITLE)
        main_sizer = self.m_settings_panel.GetSizer()
        main_sizer.GetItem(0).GetSizer().GetStaticBox().SetLabel(EDITOR)
        main_sizer.GetItem(1).GetSizer().GetStaticBox().SetLabel(GENERAL)
        main_sizer.GetItem(2).GetSizer().GetStaticBox().SetLabel(REGEX_MODULES)
        main_sizer.GetItem(3).GetSizer().GetStaticBox().SetLabel(NOTIFICATIONS)
        main_sizer.GetItem(4).GetSizer().GetStaticBox().SetLabel(HISTORY)
        self.m_single_checkbox.SetLabel(SINGLE_INSTANCE)
        self.m_visual_alert_checkbox.SetLabel(NOTIFY_POPUP)
        self.m_audio_alert_checkbox.SetLabel(ALERT)
        self.m_term_note_label.SetLabel(TERM_NOTIFY_PATH)
        self.m_language_label.SetLabel(LANGUAGE)
        self.m_re_radio.SetLabel(RE)
        self.m_bre_radio.SetLabel(BRE)
        self.m_regex_radio.SetLabel(REGEX)
        self.m_bregex_radio.SetLabel(BREGEX)
        self.m_regex_version_label.SetLabel(REGEX_VER)
        self.m_editor_button.SetLabel(CHANGE)
        self.m_history_clear_button.SetLabel(CLEAR)
        self.m_close_button.SetLabel(CLOSE)
        self.Fit()

    def history_cleared(self):
        """Return if history was cleared."""

        return self.history_records_cleared

    def on_editor_change(self, event):
        """Show editor dialog and update setting on return."""

        dlg = EditorDialog(self, self.editor)
        dlg.ShowModal()
        self.editor = dlg.get_editor()
        Settings.set_editor(self.editor)
        self.m_editor_text.SetValue(" ".join(self.editor) if len(self.editor) != 0 else "")
        dlg.Destroy()
        event.Skip()

    def on_clear_history(self, event):
        """Clear history."""

        Settings.clear_history_records(self.history_types)
        self.history_records_cleared = True
        self.m_history_label.SetLabel(RECORDS % 0)
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

    def on_cancel(self, event):
        """Close on cancel."""

        self.Close()

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

    on_bregex_toggle = on_change_module

    on_regex_toggle = on_change_module

    on_bre_toggle = on_change_module

    on_re_toggle = on_change_module
