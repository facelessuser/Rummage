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
from wx.combo import ComboPopup, ComboCtrl

# wx.SystemOptions.SetOptionInt("mac.listctrl.always_use_generic", 0)

class AutoCompleteCombo(ComboCtrl):
    def __init__(self, parent, choices=[], load_last=False):
        ComboCtrl.__init__(self, parent, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, style=wx.TE_PROCESS_ENTER|wx.TAB_TRAVERSAL)
        self.update_semaphore = False
        self.choices = None
        self.UseAltPopupWindow(True)
        self.list = ListCtrlComboPopup(self, self.GetTextCtrl())
        self.SetPopupControl(self.list)
        self.Bind(wx.EVT_KEY_UP, self.on_key_up)
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.Bind(wx.EVT_CHAR, self.on_char)
        self.Bind(wx.EVT_COMBOBOX_DROPDOWN, self.on_popup)
        self.Bind(wx.EVT_COMBOBOX_CLOSEUP, self.on_dismiss)
        self.Bind(wx.EVT_TEXT, self.on_text_change)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_enter_key)
        self.update_choices(choices, load_last)

    def tab_forward(self):
        self.GetTextCtrl().Navigate(wx.NavigationKeyEvent.FromTab|wx.NavigationKeyEvent.IsForward)

    def tab_back(self):
        self.GetTextCtrl().Navigate(wx.NavigationKeyEvent.FromTab|wx.NavigationKeyEvent.IsBackward)

    def update_choices(self, items, load_last=False):
        self.choices = items
        value = self.list.get_selected_text()
        self.list.clear()
        self.list.append_items(items)
        if load_last:
            idx = self.list.GetItemCount() - 1
            if idx != -1:
                self.list.select_item(0)
        else:
            self.update_semaphore = True
            self.list.set_selected_text(value)

    def on_popup(self, event):
        self.popped = True
        event.Skip()

    def on_dismiss(self, event):
        value = self.list.is_value_waiting()
        if value >= 0:
            self.list.select_item(value)
        self.list.set_waiting_value(-1)
        event.Skip()

    def on_enter_key(self, event):
        if self.list.curitem != -1:
            self.list.select_item(self.list.curitem)
        self.tab_forward()
        event.Skip()

    def on_char(self, event):
        key = event.GetKeyCode()
        if key in [wx.WXK_DELETE, wx.WXK_BACK]:
            self.curitem = -1
            self.update_semaphore = True
        elif key == wx.WXK_TAB:
            if event.ShiftDown():
                self.tab_back()
            else:
                self.tab_forward()
        event.Skip()

    def on_key_up(self, event):
        key = event.GetKeyCode()
        if key == wx.WXK_DOWN:
            if self.IsPopupShown():
                self.list.next_item()
                return
            else:
                self.Popup()
                self.pick_item()
        elif key == wx.WXK_UP:
            if self.IsPopupShown():
                self.list.prev_item()
                return
            else:
                self.Popup()
                self.pick_item()
        event.Skip()

    def pick_item(self):
        value = self.GetTextCtrl().GetValue()
        if value in self.choices:
            self.list.set_item(self.choices.index(value))

    def on_key_down(self, event):
        key = event.GetKeyCode()
        if key == wx.WXK_DOWN or key == wx.WXK_UP:
            if self.IsPopupShown():
                return
        event.Skip()

    def on_text_change(self, event):
        found = False
        if not self.update_semaphore:
            tc = self.GetTextCtrl()
            value = tc.GetValue()
            found_items = []
            for choice in sorted(self.choices) :
                if choice.startswith(value):
                    found_items.append(choice)
                    found = True
            if len(found_items):
                smallest = -1
                best = None
                for f in found_items:
                    if smallest == -1 or len(f) < smallest:
                        smallest = len(f)
                        best = f
                    elif smallest == len(f):
                        best = None
                if best is not None:
                    for f in found_items:
                        print(best)
                        if f != best and not f.startswith(best):
                            best = None
                            break
                if best is not None:
                    self.update_semaphore = True
                    tc.SetValue(best)
                    tc.SetInsertionPoint(len(best))
                    tc.SetSelection(len(value), len(best))
            self.list.curitem = -1
        else:
            self.update_semaphore = False
        if not found:
            event.Skip()

class ListCtrlComboPopup(wx.ListCtrl, wx.combo.ComboPopup):
    def __init__(self, parent, txt_ctrl):
        self.txt_ctrl = txt_ctrl
        self.set_value = -1
        # Since we are using multiple inheritance, and don't know yet
        # which window is to be the parent, we'll do 2-phase create of
        # the ListCtrl instead, and call its Create method later in
        # our Create method.  (See Create below.)
        self.PostCreate(wx.PreListCtrl())

        # Also init the ComboPopup base class.
        wx.combo.ComboPopup.__init__(self)

    def select_item(self, idx):
        self.txt_ctrl.SetValue(self.GetItemText(0))

    def get_selected_text(self):
        return self.txt_ctrl.GetValue()

    def set_selected_text(self, text):
        self.txt_ctrl.SetValue(text)

    def set_waiting_value(self, value):
        self.set_value = value

    def is_value_waiting(self):
        return self.set_value

    def append_items(self, items):
        for x in items:
            self.AddItem(x)

    def AddItem(self, txt):
        self.InsertStringItem(self.GetItemCount(), txt)

    def on_motion(self, evt):
        item, _ = self.HitTest(evt.GetPosition())
        if item >= 0:
            self.Select(item)
            self.curitem = item

    def next_item(self):
        if self.curitem < self.GetItemCount() - 1:
            self.curitem += 1
            self.Select(self.curitem)

    def prev_item(self):
        if self.curitem > 0 and self.GetItemCount() > 0:
            self.curitem -= 1
            self.Select(self.curitem)

    def set_item(self, idx):
        self.curitem = idx
        self.Select(self.curitem)

    def OnLeftDown(self, evt):
        item, _ = self.HitTest(evt.GetPosition())
        if item >= 0:
            self.Select(item)
            self.curitem = item
            self.set_value = item
        self.Dismiss()

    def clear(self):
        self.ClearAll()

    # The following methods are those that are overridable from the
    # ComboPopup base class.

    def Init(self):
        """ This is called immediately after construction finishes.  You can
        use self.GetCombo if needed to get to the ComboCtrl instance. """

        self.curitem = -1

    def Create(self, parent):
        """ Create the popup child control. Return True for success. """

        wx.ListCtrl.Create(self, parent,
                           style=wx.LC_LIST|wx.LC_SINGLE_SEL|wx.SIMPLE_BORDER)
        self.Bind(wx.EVT_MOTION, self.on_motion)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)

        return True

    def GetControl(self):
        """ Return the widget that is to be used for the popup. """

        return self

    def GetAdjustedSize(self, minWidth, prefHeight, maxHeight):
        return wx.combo.ComboPopup.GetAdjustedSize(self, minWidth, 200, maxHeight)

    def OnPopup(self):
        """ Called immediately after the popup is shown. """
        wx.combo.ComboPopup.OnPopup(self)

    def OnDismiss(self):
        " Called when popup is dismissed. """
        wx.combo.ComboPopup.OnDismiss(self)
