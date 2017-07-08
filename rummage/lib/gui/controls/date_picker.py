"""
Date picker workaround.

Aims to solve an issue where you can't tab out of a date picker control on Linux.

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
import wx
import wx.adv
from ... import util


class DatePicker(wx.adv.GenericDatePickerCtrl):
    """DatePickerCtrl."""

    def __init__(self, parent, wx_id):
        """Initialize."""

        wx.adv.GenericDatePickerCtrl.__init__(
            self, parent, wx_id, style=wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY | wx.adv.DP_ALLOWNONE
        )

        if util.platform() == "linux":
            self.Children[0].Bind(wx.EVT_KEY_DOWN, self.on_key_down)

    def tab_first(self):
        """Get first tab stop of parent."""

        for child in self.GetParent().GetChildren():
            if child.AcceptsFocusFromKeyboard():
                child.SetFocus()
                break

    def tab_last(self):
        """Get last tab stop of parent."""

        for child in reversed(self.GetParent().GetChildren()):
            if child.AcceptsFocusFromKeyboard():
                child.SetFocus()
                break

    def tab_forward(self):
        """Tab forward to the next object."""

        current = self
        while True:
            sib = current.GetNextSibling()
            if sib is None:
                self.tab_first()
                break
            if sib.AcceptsFocusFromKeyboard():
                sib.SetFocus()
                break
            current = sib

    def tab_back(self):
        """Tab backwards to the previous object."""

        current = self
        while True:
            sib = current.GetPrevSibling()
            if sib is None:
                self.tab_last()
                break
            if sib.AcceptsFocusFromKeyboard():
                sib.SetFocus()
                break
            current = sib

    def on_key_down(self, event):
        """Handle tabs."""

        key = event.GetKeyCode()
        if key == wx.WXK_TAB:
            if event.ShiftDown():
                self.tab_back()
            else:
                self.tab_forward()
            return
        event.Skip()
