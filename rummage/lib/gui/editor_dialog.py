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
from .localization import _
from . import gui
from .. import util


class EditorDialog(gui.EditorDialog):
    """EditorDialog."""

    WRAP_OFFSET = 40 if util.platform() == "windows" else 20

    def __init__(self, parent, editor=""):
        """Init EditorDialog object."""

        super(EditorDialog, self).__init__(parent)
        if util.platform() == "windows":
            self.SetDoubleBuffered(True)
        self.resizing = False
        self.localize()

        self.editor = editor

        # Ensure OS platform selectall shortcut works
        self.set_keybindings(
            [(wx.ACCEL_CMD if util.platform() == "osx" else wx.ACCEL_CTRL, ord('A'), self.on_textctrl_selectall)]
        )

        self.m_editor_textbox.SetValue(editor)

        self.refresh_localization()

        # Ensure good size for frame
        self.m_editor_panel.Fit()
        self.Fit()
        self.SetMinSize(wx.Size(400, self.GetSize()[1]))
        self.m_help_text.Wrap(380)
        self.m_editor_panel.GetSizer().Layout()
        self.SetSize(wx.Size(400, self.GetSize()[1]))
        self.SetMaxSize(wx.Size(-1, self.GetSize()[1]))
        self.Fit()

    def localize(self):
        """Translate strings."""

        self.TITLE = _("Configure Editor")
        self.OKAY = _("Apply")
        self.CLOSE = _("Cancel")
        self.HELP = _(
            "Use the vairable {$file} to insert the file path, "
            "{$line} to insert the line number, and {$col} to "
            "insert the line column.\n\n"
            "Double quote paths and parameters that "
            "contain spaces. {$file} should be double "
            "quoted as well.\n\n"
            "Check your editor's command line options for "
            "to proper setup."
        )

    def on_resize(self, event):
        """Handle resize."""

        if not self.resizing:
            self.resizing = True
            width = self.GetSize().GetWidth()
            self.SetMaxSize(wx.Size(-1, -1))
            self.m_help_text.SetLabelText(self.HELP)
            self.m_help_text.Wrap(width - self.WRAP_OFFSET)
            self.m_editor_panel.GetSizer().Layout()
            height = self.GetBestSize()[1]
            self.SetMaxSize(wx.Size(-1, height))
            self.SetSize(wx.Size(width, height))
            self.resizing = False
        event.Skip()

    def refresh_localization(self):
        """Localize dialog."""

        self.SetTitle(self.TITLE)
        self.m_apply_button.SetLabel(self.OKAY)
        self.m_cancel_button.SetLabel(self.CLOSE)
        self.m_help_text.SetLabelText(self.HELP)
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

    def on_textctrl_selectall(self, event):
        """Selectall for TextCtrl."""

        text = self.FindFocus()
        if isinstance(text, wx.TextCtrl):
            text.SelectAll()
        event.Skip()

    def on_test_click(self, event):
        """Test editor option."""

    def on_apply_click(self, event):
        """Set editor command with arguments on apply."""

        self.editor = self.m_editor_textbox.GetValue().strip()
        self.Close()

    def on_cancel_click(self, event):
        """Close on cancel."""

        self.Close()
