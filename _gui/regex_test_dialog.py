"""
Regex Test dialog

Licensed under MIT
Copyright (c) 2013 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import wx
import traceback
import sys
import _gui.gui as gui
import _lib.ure as ure
from _icons.rum_ico import rum_64


class RegexTestDialog(gui.RegexTestDialog):
    def __init__(self, parent, is_case, is_dot, text="", stand_alone=False):
        """
        Init Regex Test Dialog object
        """

        super(RegexTestDialog, self).__init__(None)
        self.SetIcon(rum_64.GetIcon())
        self.parent = parent

        # Ensure OS selectall shortcut works in text inputs
        self.set_keybindings(
            [(wx.ACCEL_CMD if sys.platform == "darwin" else wx.ACCEL_CTRL, ord('A'), self.on_textctrl_selectall)]
        )

        self.m_case_checkbox.SetValue(is_case)
        self.m_dot_checkbox.SetValue(is_dot)
        self.m_regex_text.SetValue(text)
        self.stand_alone = stand_alone

        # If launched as a "stand alone" (main frame) disable unneeded objects
        if stand_alone:
            self.m_use_regex_button.Hide()
            self.m_use_regex_button.GetParent().GetSizer().Layout()

        # Ensure good sizing of frame
        best = self.m_tester_panel.GetBestSize()
        current = self.m_tester_panel.GetSize()
        offset = best[1] - current[1]
        mainframe = self.GetSize()
        self.SetSize(wx.Size(mainframe[0], mainframe[1] + offset + 15))
        self.SetMinSize(self.GetSize())

    def set_keybindings(self, keybindings):
        """
        Sets keybindings for frame
        """

        tbl = []
        for binding in keybindings:
            keyid = wx.NewId()
            self.Bind(wx.EVT_MENU, binding[2], id=keyid)
            tbl.append((binding[0], binding[1], keyid))

        if len(keybindings):
            self.SetAcceleratorTable(wx.AcceleratorTable(tbl))

    def on_textctrl_selectall(self, event):
        """
        Selectall content of textctrl
        """

        text = self.FindFocus()
        if isinstance(text, wx.TextCtrl):
            text.SelectAll()
        event.Skip()

    def on_size(self, event):
        """
        Ensure good sizing
        """

        self.GetSizer().Layout()
        event.Skip()

    def on_close(self, event):
        """
        Enable parent Rummage Dialog "Test Regex" button on close
        """

        if not self.stand_alone:
            self.parent.m_regex_test_button.Enable(True)
        event.Skip()

    def on_use(self, event):
        """
        Copy regex to parent Rummage Dialog search input
        """

        self.parent.m_searchfor_textbox.SetValue(self.m_regex_text.GetValue())
        self.parent.m_regex_search_checkbox.SetValue(True)
        self.Close()

    def on_cancel(self, event):
        """
        Close dialog
        """

        self.Close()

    def test_regex(self, event):
        """
        Test and highlight search results in content buffer
        """

        flags = 0
        if not self.m_case_checkbox.GetValue():
            flags |= ure.IGNORECASE
        if self.m_dot_checkbox:
            flags |= ure.DOTALL

        try:
            test = ure.compile(self.m_regex_text.GetValue(), flags)
            text = self.m_test_text.GetValue()
            # Reset Colors
            self.m_test_text.SetStyle(
                0,
                self.m_test_text.GetLastPosition(),
                wx.TextAttr(colText=wx.Colour(0, 0, 0), colBack=wx.Colour(255, 255, 255))
            )

            for m in test.finditer(text):
                self.m_test_text.SetStyle(
                    m.start(0),
                    m.end(0),
                    wx.TextAttr(colBack=wx.Colour(0xFF, 0xCC, 0x00))
                )
        except:
            print(str(traceback.format_exc()))
            pass
        event.Skip()

    on_test_changed = test_regex

    on_regex_changed = test_regex

    on_case_toggle = test_regex

    on_dot_toggle = test_regex
