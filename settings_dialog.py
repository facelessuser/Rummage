"""
Settings Dialog

Licensed under MIT
Copyright (c) 2013 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import wx
import gui
from _lib.settings import Settings
from editor_dialog import EditorDialog


class SettingsDialog(gui.SettingsDialog):
    def __init__(self, parent):
        super(SettingsDialog, self).__init__(parent)

        self.editor = Settings.get_editor()
        self.m_editor_text.SetValue(" ".join(self.editor) if len(self.editor) != 0 else "")
        self.m_single_checkbox.SetValue(Settings.get_single_instance())

        best = self.m_settings_panel.GetBestSize()
        current = self.m_settings_panel.GetSize()
        offset = best[1] - current[1]
        mainframe = self.GetSize()
        self.SetSize(wx.Size(mainframe[0], mainframe[1] + offset + 15))
        self.SetMinSize(self.GetSize())

    def on_editor_change(self, event):
        dlg = EditorDialog(self, self.editor)
        dlg.ShowModal()
        self.editor = dlg.get_editor()
        Settings.set_editor(self.editor)
        self.m_editor_text.SetValue(" ".join(self.editor) if len(self.editor) != 0 else "")
        dlg.Destroy()
        event.Skip()

    def on_single_toggle(self, event):
        Settings.set_single_instance(self.m_single_checkbox.GetValue())

    def on_cancel(self, event):
        self.Close()
