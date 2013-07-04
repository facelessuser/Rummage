"""
AutoCompleteCombo

Licensed under MIT
Copyright (c) 2013 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import wx
import sys


class AutoCompleteCombo(object):
    def setup(self, choices, load_last=False):
        self.update_semaphore = False
        self.popped = False
        self.choices = None
        if sys.platform != "darwin":
            self.Bind(wx.EVT_KEY_UP, self.on_combo_key)
            self.Bind(wx.EVT_CHAR, self.on_char)
            self.Bind(wx.EVT_COMBOBOX, self.on_selected)
            self.Bind(wx.EVT_COMBOBOX_DROPDOWN, self.on_popup)
            self.Bind(wx.EVT_COMBOBOX_CLOSEUP, self.on_dismiss)
        self.Bind(wx.EVT_TEXT, self.on_text_change)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_enter_key)
        self.update_choices(choices, load_last)

    def tab_forward(self):
        self.Navigate(wx.NavigationKeyEvent.FromTab|wx.NavigationKeyEvent.IsForward)

    def tab_back(self):
        self.Navigate(wx.NavigationKeyEvent.FromTab|wx.NavigationKeyEvent.IsBackward)

    def update_choices(self, items, load_last=False):
        self.choices = items
        value = self.GetValue()
        self.Clear()
        self.AppendItems(items)
        if load_last:
            idx = self.GetCount() - 1
            if idx != -1:
                self.SetSelection(0)
        else:
            self.update_semaphore = True
            self.SetValue(value)

    def on_popup(self, event):
        self.popped = True
        event.Skip()

    def on_dismiss(self, event):
        self.popped = False
        event.Skip()

    def on_selected(self, event):
        self.update_semaphore = True
        event.Skip()

    def on_enter_key(self, event):
        self.tab_forward()
        event.Skip()

    def on_char(self, event):
        key = event.GetKeyCode()
        if key in [wx.WXK_DELETE, wx.WXK_BACK]:
            self.update_semaphore = True
        elif key == wx.WXK_TAB:
            if event.ShiftDown():
                self.tab_back()
            else:
                self.tab_forward()
        event.Skip()

    def on_combo_key(self, event):
        key = event.GetKeyCode()
        if key == wx.WXK_DOWN and not self.popped:
            self.Popup()
        event.Skip()

    def on_text_change(self, event):
        found = False
        if sys.platform != "darwin":
            if not self.update_semaphore:
                value = event.GetString()
                for choice in sorted(self.choices) :
                    if choice.startswith(value):
                        self.update_semaphore = True
                        self.SetValue(choice)
                        self.SetInsertionPoint(len(value))
                        self.SetMark(len(value), len(choice))
                        found = True
                        break
            else:
                self.update_semaphore = False
        if not found:
            event.Skip()
