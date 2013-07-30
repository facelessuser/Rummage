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

from _lib.localization import get as _


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
        self.stand_alone = stand_alone
        self.regex_event_code = -1
        self.testing = False
        self.init_regex_timer()
        self.start_regex_timer()

        self.m_regex_text.SetValue(text)

        self.localize()

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

    def localize(self):
        """
        Localize dialog
        """

        self.SetTitle(_("Regex Tester"))
        self.m_use_regex_button.SetLabel(_("Use"))
        self.m_close_button.SetLabel(_("Close"))
        self.m_case_checkbox.SetLabel(_("Search case-sensitive"))
        self.m_dot_checkbox.SetLabel(_("Dot matches newline"))
        self.m_test_text.GetContainingSizer().GetStaticBox().SetLabel(_("Text"))
        self.m_regex_text.GetContainingSizer().GetStaticBox().SetLabel(_("Regex Input"))
        self.Fit()

    def init_regex_timer(self):
        """
        Init the update Timer object]
        """

        self.regex_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.regex_event, self.regex_timer)

    def start_regex_timer(self):
        """
        Start update timer
        """

        if not self.regex_timer.IsRunning():
            self.regex_timer.Start(500)

    def stop_regex_timer(self):
        """
        Stop update timer
        """

        if self.regex_timer.IsRunning():
            self.regex_timer.Stop()

    def regex_event(self, event):
        if self.regex_event_code == 0:
            if not self.testing:
                self.test_regex()
                self.regex_event_code -= 1
            else:
                event.Skip()
        else:
            if self.regex_event_code > 0:
                self.regex_event_code = 0
            event.Skip()

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

    def on_close(self, event):
        """
        Enable parent Rummage Dialog "Test Regex" button on close
        """

        self.stop_regex_timer()

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

    def test_regex(self):
        """
        Test and highlight search results in content buffer
        """
        if not self.testing:
            self.testing = True
            if self.m_regex_text.GetValue() == "":
                self.m_test_text.SetStyle(
                    0,
                    self.m_test_text.GetLastPosition(),
                    wx.TextAttr(colText=wx.Colour(0, 0, 0), colBack=wx.Colour(255, 255, 255))
                )
                self.testing = False
                return

            flags = 0
            if not self.m_case_checkbox.GetValue():
                flags |= ure.IGNORECASE
            if self.m_dot_checkbox:
                flags |= ure.DOTALL

            try:
                test = ure.compile(self.m_regex_text.GetValue(), flags)
            except:
                self.testing = False
                return

            try:
                text = self.m_test_text.GetValue()
                # Reset Colors
                self.m_test_text.SetStyle(
                    0,
                    self.m_test_text.GetLastPosition(),
                    wx.TextAttr(colText=wx.Colour(0, 0, 0), colBack=wx.Colour(255, 255, 255))
                )

                for m in test.finditer(text):
                    try:
                        self.m_test_text.SetStyle(
                            m.start(0),
                            m.end(0),
                            wx.TextAttr(colBack=wx.Colour(0xFF, 0xCC, 0x00))
                        )
                    except:
                        pass
            except:
                print(str(traceback.format_exc()))
                pass
            self.testing = False

    def regex_start_event(self, event):
        self.regex_event_code += 1
        event.Skip()

    def on_test_changed(self, event):
        if not self.testing:
            self.regex_start_event(event)
        else:
            event.Skip()

    on_regex_changed = regex_start_event

    on_case_toggle = regex_start_event

    on_dot_toggle = regex_start_event
