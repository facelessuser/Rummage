"""
Editor Dialog.

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
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
from __future__ import unicode_literals
import wx
from .arg_dialog import ArgDialog
from .localization import _
from . import gui
from .. import util


class EditorDialog(gui.EditorDialog):
    """EditorDialog."""

    def __init__(self, parent, editor=[]):
        """Init EditorDialog object."""

        super(EditorDialog, self).__init__(parent)
        self.localize()

        self.editor = editor

        # Ensure OS platform selectall shortcut works
        self.set_keybindings(
            [(wx.ACCEL_CMD if util.platform() == "osx" else wx.ACCEL_CTRL, ord('A'), self.on_textctrl_selectall)]
        )

        if len(editor) != 0:
            self.m_editor_picker.SetPath(editor[0])

        if len(editor) > 1:
            for x in range(1, len(editor)):
                self.m_arg_list.Insert(editor[x], x - 1)

        self.refresh_localization()

        # Ensure good size for frame
        best = self.m_editor_panel.GetBestSize()
        current = self.m_editor_panel.GetSize()
        offset = best[1] - current[1]
        mainframe = self.GetSize()
        self.SetSize(wx.Size(mainframe[0], mainframe[1] + offset + 15))
        self.SetMinSize(self.GetSize())

    def localize(self):
        """Translate strings."""

        self.TITLE = _("Configure Editor")
        self.OKAY = _("Apply")
        self.CLOSE = _("Cancel")
        self.ADD = _("Add")
        self.DELETE = _("Delete")
        self.EDIT = _("Edit")
        self.UP = _("Up")
        self.DOWN = _("Down")
        self.APPLICATION = _("Application")
        self.ARGUMENTS = _("Arguments")
        self.INSTRUCTIONS = _(
            "Select the application and then set the arguments.\n\n"
            "Special variables:\n"
            "{$file} --> file path\n"
            "{$line} --> line number\n"
            "{$col} --> column number"
        )

    def refresh_localization(self):
        """Localize dialog."""

        self.SetTitle(self.TITLE)
        self.m_add_arg_button.SetLabel(self.ADD)
        self.m_remove_arg_button.SetLabel(self.DELETE)
        self.m_edit_button.SetLabel(self.EDIT)
        self.m_up_button.SetLabel(self.UP)
        self.m_down_button.SetLabel(self.DOWN)
        self.m_apply_button.SetLabel(self.OKAY)
        self.m_cancel_button.SetLabel(self.CLOSE)
        self.m_instructions_label.SetLabel(self.INSTRUCTIONS)
        self.m_instructions_label.Wrap(325)
        self.m_editor_panel.GetSizer().GetItem(1).GetSizer().GetStaticBox().SetLabel(self.APPLICATION)
        self.m_editor_panel.GetSizer().GetItem(2).GetSizer().GetStaticBox().SetLabel(self.ARGUMENTS)
        self.Fit()

    def get_editor(self):
        """Get the selected editor."""

        return self.editor

    def set_keybindings(self, keybindings):
        """Set keybindings for frame."""

        tbl = []
        for binding in keybindings:
            keyid = wx.NewId()
            self.Bind(wx.EVT_MENU, binding[2], id=keyid)
            tbl.append((binding[0], binding[1], keyid))

        if len(keybindings):
            self.SetAcceleratorTable(wx.AcceleratorTable(tbl))

    def add_arg(self):
        """Add argument."""

        value = self.m_arg_text.GetValue()
        if value != "":
            index = self.m_arg_list.GetSelected()
            if index == wx.NOT_FOUND:
                self.m_arg_list.Insert(value, self.m_arg_list.GetCount())
            else:
                self.m_arg_list.Insert(value, index)

    def on_textctrl_selectall(self, event):
        """Selectall for TextCtrl."""

        text = self.FindFocus()
        if isinstance(text, wx.TextCtrl):
            text.SelectAll()
        event.Skip()

    def on_arg_enter(self, event):
        """Add argument on enter key."""

        self.add_arg()
        event.Skip()

    def on_add(self, event):
        """Add argument button event."""

        self.add_arg()
        event.Skip()

    def on_edit(self, event):
        """Edit argument."""

        index = self.m_arg_list.GetSelected()
        if index > wx.NOT_FOUND:
            dlg = ArgDialog(self, self.m_arg_list.GetString(index))
            dlg.ShowModal()
            string = dlg.get_arg()
            dlg.Destroy()

            self.m_arg_list.Delete(index)
            self.m_arg_list.Insert(string, index)

    def on_up(self, event):
        """Move argument up."""

        index = self.m_arg_list.GetSelected()
        if index > 0:
            search = self.m_arg_list.GetString(index)
            self.m_arg_list.Delete(index)
            self.m_arg_list.Insert(search, index - 1)
            self.m_arg_list.Select(index - 1)

    def on_down(self, event):
        """Move argument down."""

        count = self.m_arg_list.GetCount()
        index = self.m_arg_list.GetSelected()
        if wx.NOT_FOUND < index < count - 1:
            search = self.m_arg_list.GetString(index)
            self.m_arg_list.Delete(index)
            self.m_arg_list.Insert(search, index + 1)
            self.m_arg_list.Select(index + 1)

    def on_remove(self, event):
        """Remove argument."""

        index = self.m_arg_list.GetSelected()
        selected = self.m_arg_list.IsSelected(index)
        if index != wx.NOT_FOUND:
            self.m_arg_list.Delete(index)
            count = self.m_arg_list.GetCount()
            if selected and count and index <= count - 1:
                self.m_arg_list.Select(index)

    def on_apply(self, event):
        """Set editor command with arguments on apply."""

        editor = []
        app = self.m_editor_picker.GetPath()
        if app != "":
            editor.append(app)
        for x in range(0, self.m_arg_list.GetCount()):
            editor.append(self.m_arg_list.GetString(x))
        self.editor = editor
        self.Close()

    def on_cancel(self, event):
        """Close on cancel."""

        self.Close()
