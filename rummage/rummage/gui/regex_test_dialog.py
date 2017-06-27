"""
Regex Test dialog.

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
import re
import traceback
import wx
import functools
from . import gui
from .. import data
from .settings import Settings
from ..localization import _
from .. import rumcore
from .. import util
from backrefs import bre, bregex


class RegexTestDialog(gui.RegexTestDialog):
    """Regex test dialog."""

    def __init__(self, parent):
        """Init Regex Test Dialog object."""

        super(RegexTestDialog, self).__init__(None)
        self.SetIcon(
            data.get_image('rummage_medium.png' if util.platform() == 'linux' else 'rummage_large.png').GetIcon()
        )
        self.parent = parent
        self.regex_mode = Settings.get_regex_mode()
        self.regex_version = Settings.get_regex_version()

        # Ensure OS selectall shortcut works in text inputs
        self.set_keybindings(
            [
                (wx.ACCEL_CMD if util.platform() == "osx" else wx.ACCEL_CTRL, ord('A'), self.on_textctrl_selectall)
            ]
        )

        self.m_case_checkbox.SetValue(parent.m_case_checkbox.GetValue() if parent else False)
        self.m_dotmatch_checkbox.SetValue(parent.m_dotmatch_checkbox.GetValue() if parent else False)
        self.m_unicode_checkbox.SetValue(parent.m_unicode_checkbox.GetValue() if parent else False)
        if self.regex_mode in rumcore.REGEX_MODES:
            self.m_bestmatch_checkbox.SetValue(parent.m_bestmatch_checkbox.GetValue() if parent else False)
            self.m_enhancematch_checkbox.SetValue(parent.m_enhancematch_checkbox.GetValue() if parent else False)
            self.m_word_checkbox.SetValue(parent.m_word_checkbox.GetValue() if parent else False)
            self.m_reverse_checkbox.SetValue(parent.m_reverse_checkbox.GetValue() if parent else False)
            self.m_posix_checkbox.SetValue(parent.m_posix_checkbox.GetValue() if parent else False)
            self.m_format_replace_checkbox.SetValue(parent.m_format_replace_checkbox.GetValue() if parent else False)
            self.m_bestmatch_checkbox.Show()
            self.m_enhancematch_checkbox.Show()
            self.m_word_checkbox.Show()
            self.m_reverse_checkbox.Show()
            self.m_posix_checkbox.Show()
            self.m_format_replace_checkbox.Show()
            if self.regex_version == 0:
                self.m_fullcase_checkbox.SetValue(parent.m_fullcase_checkbox.GetValue() if parent else False)
                self.m_fullcase_checkbox.Show()
        self.regex_event_code = -1
        self.testing = False
        self.init_regex_timer()
        self.start_regex_timer()

        self.m_regex_text.SetValue(parent.m_searchfor_textbox.GetValue() if parent else "")
        self.m_replace_text.SetValue(parent.m_replace_textbox.GetValue() if parent else "")

        self.localize()

        # Ensure good sizing of frame
        best = self.m_tester_panel.GetBestSize()
        current = self.m_tester_panel.GetSize()
        offset = best[1] - current[1]
        mainframe = self.GetSize()
        self.SetSize(wx.Size(mainframe[0], mainframe[1] + offset + 15))
        self.SetMinSize(self.GetSize())

    def localize(self):
        """Localize dialog."""

        self.SetTitle(_("Regex Tester"))
        self.m_use_regex_button.SetLabel(_("Use"))
        self.m_close_button.SetLabel(_("Close"))
        self.m_case_checkbox.SetLabel(_("Search case-sensitive"))
        self.m_dotmatch_checkbox.SetLabel(_("Dot matches newline"))
        self.m_unicode_checkbox.SetLabel(_("Use Unicode properties"))
        self.m_bestmatch_checkbox.SetLabel(_("Best fuzzy match"))
        self.m_enhancematch_checkbox.SetLabel(_("Improve fuzzy fit"))
        self.m_word_checkbox.SetLabel(_("Unicode word break"))
        self.m_reverse_checkbox.SetLabel(_("Reverse match"))
        self.m_posix_checkbox.SetLabel(_("Use POSIX matching"))
        self.m_format_replace_checkbox.SetLabel(_("Format style replacements"))
        self.m_fullcase_checkbox.SetLabel(_("Full case-folding"))
        self.m_test_text.GetContainingSizer().GetStaticBox().SetLabel(_("Text"))
        self.m_test_replace_text.GetContainingSizer().GetStaticBox().SetLabel(_("Result"))
        main_sizer = self.m_tester_panel.GetSizer()
        main_sizer.GetItem(2).GetSizer().GetStaticBox().SetLabel(_("Regex Input"))
        self.m_find_label.SetLabel(_("Find"))
        self.m_replace_label.SetLabel(_("Replace"))
        self.Fit()

    def init_regex_timer(self):
        """Init the update Timer object]."""

        self.regex_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.regex_event, self.regex_timer)

    def regex_expand(self, m, replace):
        """Regex module expand."""

        return m.expandf(replace) if self.m_format_replace_checkbox.GetValue() else m.expand(replace)

    def start_regex_timer(self):
        """Start update timer."""

        if not self.regex_timer.IsRunning():
            self.regex_timer.Start(500)

    def stop_regex_timer(self):
        """Stop update timer."""

        if self.regex_timer.IsRunning():
            self.regex_timer.Stop()

    def regex_event(self, event):
        """Event for regex."""

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
        """Set keybindings for frame."""

        tbl = []
        for binding in keybindings:
            keyid = wx.NewId()
            self.Bind(wx.EVT_MENU, binding[2], id=keyid)
            tbl.append((binding[0], binding[1], keyid))

        if len(keybindings):
            self.SetAcceleratorTable(wx.AcceleratorTable(tbl))

    def on_textctrl_selectall(self, event):
        """Selectall content of textctrl."""

        text = self.FindFocus()
        if isinstance(text, wx.TextCtrl):
            text.SelectAll()
        event.Skip()

    def on_close(self, event):
        """Enable parent Rummage Dialog "Test Regex" button on close."""

        self.stop_regex_timer()
        event.Skip()

    def on_use(self, event):
        """Copy regex to parent Rummage Dialog search input."""

        self.parent.m_searchfor_textbox.SetValue(self.m_regex_text.GetValue())
        self.parent.m_replace_textbox.SetValue(self.m_replace_text.GetValue())
        self.parent.m_regex_search_checkbox.SetValue(True)
        self.parent.m_unicode_checkbox.SetValue(self.m_unicode_checkbox.GetValue())
        self.parent.m_case_checkbox.SetValue(self.m_case_checkbox.GetValue())
        self.parent.m_dotmatch_checkbox.SetValue(self.m_dotmatch_checkbox.GetValue())
        if self.regex_mode in rumcore.REGEX_MODES:
            self.parent.m_bestmatch_checkbox.SetValue(self.m_bestmatch_checkbox.GetValue())
            self.parent.m_enhancematch_checkbox.SetValue(self.m_enhancematch_checkbox.GetValue())
            self.parent.m_word_checkbox.SetValue(self.m_word_checkbox.GetValue())
            self.parent.m_reverse_checkbox.SetValue(self.m_reverse_checkbox.GetValue())
            self.parent.m_posix_checkbox.SetValue(self.m_posix_checkbox.GetValue())
            self.parent.m_format_replace_checkbox.SetValue(self.m_format_replace_checkbox.GetValue())
            if self.regex_version == 0:
                self.parent.m_fullcase_checkbox.SetValue(self.m_fullcase_checkbox.GetValue())
        self.Close()

    def on_cancel(self, event):
        """Close dialog."""

        self.Close()

    def reset_highlights(self):
        """Reset highlights."""

        # Reset Colors
        self.m_test_text.SetStyle(
            0,
            self.m_test_text.GetLastPosition(),
            wx.TextAttr(wx.Colour(0, 0, 0), colBack=wx.Colour(255, 255, 255))
        )

    def test_regex(self):
        """Test and highlight search results in content buffer."""

        # Replace functions
        def replace_bregex_format(m, replace=None):
            """Replace for bregex format."""
            return m.expandf(replace)

        def replace_regex(m, replace=None):
            """Replace for regex."""
            return self.regex_expand(m, replace)

        def replace_re(m, replace=None):
            """Replace for re."""
            return m.expand(replace)

        if self.regex_mode == rumcore.REGEX_MODE:
            import regex

        if not self.testing:
            self.testing = True
            if self.m_regex_text.GetValue() == "":
                self.m_test_text.SetStyle(
                    0,
                    self.m_test_text.GetLastPosition(),
                    wx.TextAttr(wx.Colour(0, 0, 0), colBack=wx.Colour(255, 255, 255))
                )
                self.testing = False
                return

            if self.regex_mode == rumcore.BREGEX_MODE:
                flags = bregex.MULTILINE
                if self.regex_version == 1:
                    flags |= bregex.VERSION1
                else:
                    flags |= bregex.VERSION0
                if self.m_dotmatch_checkbox.GetValue():
                    flags |= bregex.DOTALL
                if not self.m_case_checkbox.GetValue():
                    flags |= bregex.IGNORECASE
                if self.m_unicode_checkbox.GetValue():
                    flags |= bregex.UNICODE
                else:
                    flags |= bregex.ASCII
                if self.m_bestmatch_checkbox.GetValue():
                    flags |= bregex.BESTMATCH
                if self.m_enhancematch_checkbox.GetValue():
                    flags |= bregex.ENHANCEMATCH
                if self.m_word_checkbox.GetValue():
                    flags |= bregex.WORD
                if self.m_reverse_checkbox.GetValue():
                    flags |= bregex.REVERSE
                if self.m_posix_checkbox.GetValue():
                    flags |= bregex.POSIX
                if flags & bregex.VERSION0 and self.m_fullcase_checkbox.GetValue():
                    flags |= bregex.FULLCASE
            elif self.regex_mode == rumcore.REGEX_MODE:
                flags = regex.MULTILINE
                if self.regex_version == 1:
                    flags |= regex.VERSION1
                else:
                    flags |= regex.VERSION0
                if self.m_dotmatch_checkbox.GetValue():
                    flags |= regex.DOTALL
                if not self.m_case_checkbox.GetValue():
                    flags |= regex.IGNORECASE
                if self.m_unicode_checkbox.GetValue():
                    flags |= regex.UNICODE
                else:
                    flags |= regex.ASCII
                if self.m_bestmatch_checkbox.GetValue():
                    flags |= regex.BESTMATCH
                if self.m_enhancematch_checkbox.GetValue():
                    flags |= regex.ENHANCEMATCH
                if self.m_word_checkbox.GetValue():
                    flags |= regex.WORD
                if self.m_reverse_checkbox.GetValue():
                    flags |= regex.REVERSE
                if self.m_posix_checkbox.GetValue():
                    flags |= regex.POSIX
                if flags & regex.VERSION0 and self.m_fullcase_checkbox.GetValue():
                    flags |= regex.FULLCASE
            elif self.regex_mode == rumcore.BRE_MODE:
                flags = bre.MULTILINE
                if not self.m_case_checkbox.GetValue():
                    flags |= bre.IGNORECASE
                if self.m_dotmatch_checkbox.GetValue():
                    flags |= bre.DOTALL
                if self.m_unicode_checkbox.GetValue():
                    flags |= bre.UNICODE
            else:
                flags = re.MULTILINE
                if not self.m_case_checkbox.GetValue():
                    flags |= re.IGNORECASE
                if self.m_dotmatch_checkbox.GetValue():
                    flags |= re.DOTALL
                if self.m_unicode_checkbox.GetValue():
                    flags |= re.UNICODE

            try:
                if self.regex_mode == rumcore.BREGEX_MODE:
                    test = bregex.compile_search(self.m_regex_text.GetValue(), flags)
                elif self.regex_mode == rumcore.REGEX_MODE:
                    test = regex.compile(self.m_regex_text.GetValue(), flags)
                elif self.regex_mode == rumcore.BRE_MODE:
                    test = bre.compile_search(self.m_regex_text.GetValue(), flags)
                else:
                    test = re.compile(self.m_regex_text.GetValue(), flags)
            except Exception:
                self.reset_highlights()
                self.m_test_replace_text.SetValue(
                    self.m_test_text.GetValue() if self.m_replace_text.GetValue() else ''
                )
                self.testing = False
                return

            replace_test = None
            try:
                rpattern = self.m_replace_text.GetValue()
                if rpattern:
                    if self.regex_mode == rumcore.BREGEX_MODE:
                        if self.m_format_replace_checkbox.GetValue():
                            replace_test = functools.partial(replace_bregex_format, replace=rpattern)
                        else:
                            replace_test = bregex.compile_replace(test, self.m_replace_text.GetValue())
                    elif self.regex_mode == rumcore.REGEX_MODE:
                        replace_test = functools.partial(replace_regex, replace=rpattern)
                    elif self.regex_mode == rumcore.BRE_MODE:
                        replace_test = bre.compile_replace(test, self.m_replace_text.GetValue())
                    else:
                        replace_test = functools.partial(replace_re, replace=rpattern)
            except Exception:
                pass

            try:
                text = self.m_test_text.GetValue()

                # Reset Colors
                self.reset_highlights()

                new_text = []
                offset = 0
                for m in test.finditer(text):
                    try:
                        if replace_test:
                            new_text.append(text[offset:m.start(0)])
                            new_text.append(replace_test(m))
                            offset = m.end(0)
                    except Exception:
                        replace_test = None
                    self.m_test_text.SetStyle(
                        m.start(0),
                        m.end(0),
                        wx.TextAttr(wx.Colour(0, 0, 0), colBack=wx.Colour(0xFF, 0xCC, 0x00))
                    )
                if replace_test:
                    new_text.append(text[offset:])
                self.m_test_replace_text.SetValue(''.join(new_text))

            except Exception:
                print(str(traceback.format_exc()))
            self.testing = False

    def regex_start_event(self, event):
        """Regex start event."""

        self.regex_event_code += 1
        event.Skip()

    def on_test_changed(self, event):
        """On test change event."""

        if not self.testing:
            self.regex_start_event(event)
        else:
            event.Skip()

    on_replace_changed = regex_start_event

    on_regex_changed = regex_start_event

    on_case_toggle = regex_start_event

    on_dot_toggle = regex_start_event

    on_unicode_toggle = regex_start_event

    on_bestmatch_toggle = regex_start_event

    on_enhancematch_toggle = regex_start_event

    on_word_toggle = regex_start_event

    on_reverse_toggle = regex_start_event

    on_format_replace_toggle = regex_start_event

    on_fullcase_toggle = regex_start_event
