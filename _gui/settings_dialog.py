"""
Settings Dialog

Licensed under MIT
Copyright (c) 2013 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import wx
import _gui.gui as gui
from _lib.settings import Settings
from _gui.editor_dialog import EditorDialog
from _gui.platform_window_focus import platform_window_focus


class SettingsDialog(gui.SettingsDialog):
    def __init__(self, parent):
        """
        Init SettingsDialog object
        """

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

        self.editor = Settings.get_editor()
        self.m_editor_text.SetValue(" ".join(self.editor) if len(self.editor) != 0 else "")
        self.m_single_checkbox.SetValue(Settings.get_single_instance())
        self.m_history_label.SetLabel("%d Records" % history_records)
        self.m_history_clear_button.Enable(history_records > 0)
        self.m_debug_checkbox.SetValue(Settings.get_debug())

        self.m_visual_alert_checkbox.SetValue(Settings.get_notify())
        self.m_audio_alert_checkbox.SetValue(Settings.get_alert())
        self.alert_methods = Settings.get_platform_notify()
        self.m_notify_choice.Clear()
        for a in self.alert_methods:
            self.m_notify_choice.Append(a)
        self.m_notify_choice.SetStringSelection(Settings.get_notify_method())

        best = self.m_settings_panel.GetBestSize()
        current = self.m_settings_panel.GetSize()
        offset = best[1] - current[1]
        mainframe = self.GetSize()
        self.SetSize(wx.Size(mainframe[0], mainframe[1] + offset + 15))
        self.SetMinSize(self.GetSize())

    def history_cleared(self):
        """
        Return if history was cleared
        """

        return self.history_records_cleared

    def on_editor_change(self, event):
        """
        Show editor dialog and update setting on return
        """

        dlg = EditorDialog(self, self.editor)
        dlg.ShowModal()
        self.editor = dlg.get_editor()
        Settings.set_editor(self.editor)
        self.m_editor_text.SetValue(" ".join(self.editor) if len(self.editor) != 0 else "")
        dlg.Destroy()
        event.Skip()

    def on_clear_history(self, event):
        """
        Clear history
        """

        Settings.clear_history_records(self.history_types)
        self.history_records_cleared = True
        self.m_history_label.SetLabel("0 Records")
        self.m_history_clear_button.Enable(False)

    def on_notify_choice(self, event):
        """
        Update notify method
        """

        Settings.set_notify_method(self.m_notify_choice.GetStringSelection())
        event.Skip()

    def on_notify_toggle(self, event):
        """
        Update whether notifications are used
        """

        Settings.set_notify(self.m_visual_alert_checkbox.GetValue())
        event.Skip()

    def on_alert_toggle(self, event):
        """
        Update if alert sound is used
        """

        Settings.set_alert(self.m_audio_alert_checkbox.GetValue())
        event.Skip()

    def on_single_toggle(self, event):
        """
        Update if single instance is used
        """

        Settings.set_single_instance(self.m_single_checkbox.GetValue())

    def on_debug_toggle(self, event):
        """
        Update if debug logging is used
        """

        Settings.set_debug(self.m_debug_checkbox.GetValue())

    def on_show_log(self, event):
        """
        Show log
        """

        self.GetParent().open_debug_console()
        stdiowin = wx.GetApp().stdioWin
        if stdiowin is not None:
            platform_window_focus(stdiowin.frame)

    def on_cancel(self, event):
        """
        Close on cancel
        """

        self.Close()
