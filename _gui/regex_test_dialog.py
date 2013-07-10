import wx
import traceback
import _gui.gui as gui
import _lib.ure as ure
from _icons.rum_ico import rum_64


class RegexTestDialog(gui.RegexTestDialog):
    def __init__(self, parent, is_case, is_dot, text="", stand_alone=False):
        super(RegexTestDialog, self).__init__(None)
        self.SetIcon(rum_64.GetIcon())
        self.parent = parent

        self.m_case_checkbox.SetValue(is_case)
        self.m_dot_checkbox.SetValue(is_dot)
        self.m_regex_text.SetValue(text)
        self.stand_alone = stand_alone

        if stand_alone:
            self.m_use_regex_button.Hide()
            self.m_use_regex_button.GetParent().GetSizer().Layout()

        best = self.m_tester_panel.GetBestSize()
        current = self.m_tester_panel.GetSize()
        offset = best[1] - current[1]
        mainframe = self.GetSize()
        self.SetSize(wx.Size(mainframe[0], mainframe[1] + offset + 15))
        self.SetMinSize(self.GetSize())

    def on_size(self, event):
        self.GetSizer().Layout()
        event.Skip()

    def on_close(self, event):
        if not self.stand_alone:
            self.parent.m_regex_test_button.Enable(True)
        event.Skip()

    def on_use(self, event):
        self.parent.m_searchfor_textbox.SetValue(self.m_regex_text.GetValue())
        self.parent.m_regex_search_checkbox.SetValue(True)
        self.Close()

    def on_cancel(self, event):
        self.Close()

    def test_regex(self, event):
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
