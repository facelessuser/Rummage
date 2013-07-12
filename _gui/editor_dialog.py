"""
Editor Dialog

Licensed under MIT
Copyright (c) 2013 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import wx
import sys
import _gui.gui as gui
from _gui.arg_dialog import ArgDialog


class EditorDialog(gui.EditorDialog):
    def __init__(self, parent, editor=[]):
        super(EditorDialog, self).__init__(parent)
        self.editor = editor

        self.set_keybindings(
            [(wx.ACCEL_CMD if sys.platform == "darwin" else wx.ACCEL_CTRL, ord('A'), self.on_textctrl_selectall)]
        )

        if len(editor) != 0:
            self.m_editor_picker.SetPath(editor[0])

        if len(editor) > 1:
            self.m_arg_list.Clear()
            for x in range(1, len(editor)):
                self.m_arg_list.Append(editor[x])

        best = self.m_editor_panel.GetBestSize()
        current = self.m_editor_panel.GetSize()
        offset = best[1] - current[1]
        mainframe = self.GetSize()
        self.SetSize(wx.Size(mainframe[0], mainframe[1] + offset + 15))
        self.SetMinSize(self.GetSize())

    def set_keybindings(self, keybindings):
        tbl = []
        for binding in keybindings:
            keyid = wx.NewId()
            self.Bind(wx.EVT_MENU, binding[2], id=keyid)
            tbl.append((binding[0], binding[1], keyid))

        if len(keybindings):
            self.SetAcceleratorTable(wx.AcceleratorTable(tbl))

    def on_textctrl_selectall(self, event):
        text = self.FindFocus()
        if isinstance(text, wx.TextCtrl):
            text.SelectAll()
        event.Skip()

    def on_arg_enter(self, event):
        self.add_arg()
        event.Skip()

    def on_add(self, event):
        self.add_arg()
        event.Skip()

    def add_arg(self):
        value = self.m_arg_text.GetValue()
        if value != "":
            self.m_arg_list.Append(value)
            value = self.m_arg_text.SetValue("")

    def on_edit(self, event):
        value = self.m_arg_list.GetSelection()
        if value >= 0:
            dlg = ArgDialog(self, self.m_arg_list.GetString(value))
            dlg.ShowModal()
            string = dlg.get_arg()
            dlg.Destroy()

            items = []
            for x in range(0, self.m_arg_list.GetCount()):
                if x == value:
                    items.append(string)
                if x != value:
                    items.append(self.m_arg_list.GetString(x))
            self.m_arg_list.Clear()
            for x in items:
                self.m_arg_list.Append(x)

    def on_up(self, event):
        value = self.m_arg_list.GetSelection()
        if value > 0:
            string = self.m_arg_list.GetString(value)
            items = []
            for x in range(0, self.m_arg_list.GetCount()):
                if x == value - 1:
                    items.append(string)
                if x != value:
                    items.append(self.m_arg_list.GetString(x))
            self.m_arg_list.Clear()
            for x in items:
                self.m_arg_list.Append(x)

    def on_down(self, event):
        value = self.m_arg_list.GetSelection()
        count = self.m_arg_list.GetCount()
        if value < count - 1:
            string = self.m_arg_list.GetString(value)
            items = []
            for x in range(0, count):
                if x != value:
                    items.append(self.m_arg_list.GetString(x))
                    if x == value + 1:
                        items.append(string)
            self.m_arg_list.Clear()
            for x in items:
                self.m_arg_list.Append(x)

    def on_remove(self, event):
        value = self.m_arg_list.GetSelection()
        if value >= 0:
            items = []
            for x in range(0, self.m_arg_list.GetCount()):
                if x != value:
                    items.append(self.m_arg_list.GetString(x))
            self.m_arg_list.Clear()
            for x in items:
                self.m_arg_list.Append(x)

    def on_apply(self, event):
        editor = []
        app = self.m_editor_picker.GetPath()
        if app != "":
            editor.append(app)
        for x in range(0, self.m_arg_list.GetCount()):
            editor.append(self.m_arg_list.GetString(x))
        self.editor = editor
        self.Close()

    def on_cancel(self, event):
        self.Close()

    def get_editor(self):
        return self.editor
