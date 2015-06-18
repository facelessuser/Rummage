"""
AutoCompleteCombo.

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
from wx.combo import ComboCtrl


class AutoCompleteCombo(ComboCtrl):

    """AutoCompleteCombo box."""

    def __init__(self, parent, choices=[], load_last=False, changed_callback=None):
        """Init the AutoCompleteCombo object."""

        ComboCtrl.__init__(
            self, parent, wx.ID_ANY,
            wx.EmptyString, wx.DefaultPosition, wx.DefaultSize,
            style=wx.TAB_TRAVERSAL | wx.TE_PROCESS_ENTER
        )
        self.update_semaphore = False
        self.choices = None
        self.changed_callback = changed_callback
        self.UseAltPopupWindow(True)

        # Create list ctrl popup
        self.list = ListCtrlComboPopup(self, self.GetTextCtrl())
        self.SetPopupControl(self.list)

        # Key bindings and events for the object
        self.Bind(wx.EVT_CHAR, self.on_char)
        self.Bind(wx.EVT_KEY_UP, self.on_key_up)
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.Bind(wx.EVT_SET_FOCUS, self.on_focus)
        self.Bind(wx.EVT_TEXT, self.on_text_change)
        try:
            self.Bind(wx.EVT_COMBOBOX_CLOSEUP, self.on_dismiss)
        except Exception:
            pass

        # Add choices
        self.update_choices(choices, load_last)

    def on_focus(self, event):
        """Ensure the TextCtrl object takes the focus."""

        self.GetTextCtrl().SetFocus()
        event.Skip()

    def tab_forward(self):
        """Tab forward to the next object."""

        self.Navigate(wx.NavigationKeyEvent.FromTab | wx.NavigationKeyEvent.IsForward)

    def tab_back(self):
        """Tab backwards to the previous object."""

        self.Navigate(wx.NavigationKeyEvent.FromTab | wx.NavigationKeyEvent.IsBackward)

    def update_choices(self, items, load_last=False):
        """
        Update the choices in the popup.

        Load the first entry if desired
        (really need to rename load_last to
        load_first since this changed).
        """

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
        self.list.resize_dropdown()

    def on_dismiss(self, event):
        """Load a previously selected choice to the TextCtrl on dismiss."""

        value = self.list.is_value_waiting()
        if value >= 0:
            self.GetTextCtrl().SetSelection(0, 0)
            self.list.select_item(value)
            self.GetTextCtrl().SetSelection(0, len(self.GetTextCtrl().GetValue()))
            self.list.set_waiting_value(-1)
            return
        event.Skip()

    def on_char(self, event):
        """
        Prevent delete and backspace from triggering autocomplete.

        Allow tab and shift+tab to tab forward and back to other objects.
        """

        key = event.GetKeyCode()
        if key == wx.WXK_TAB:
            if event.ShiftDown():
                self.tab_back()
            else:
                self.tab_forward()
        event.Skip()

    def on_key_up(self, event):
        """
        Popup combo dropdown on arrow up and down.

        If already open select next and previous choices.
        """

        key = event.GetKeyCode()
        if key == wx.WXK_DOWN:
            self.Popup()
            self.pick_item()
        elif key == wx.WXK_UP:
            self.Popup()
            self.pick_item()
        event.Skip()

    def pick_item(self):
        """Set the choice based on the TextCtrl value."""

        value = self.GetTextCtrl().GetValue()
        if value in self.choices:
            self.list.set_item(self.choices.index(value))

    def on_key_down(self, event):
        """Swallow up and down arrow event if popup shown."""

        key = event.GetKeyCode()
        if key in [wx.WXK_DELETE, wx.WXK_BACK]:
            self.update_semaphore = True
        event.Skip()

    def safe_set_value(self, text):
        """Update TextCtrl without triggering autocomplete."""

        self.update_semaphore = True
        self.GetTextCtrl().SetValue(text)
        self.update_semaphore = False

    def on_text_change(self, event):
        """Autocomplete on text change event."""

        found = False
        if not self.update_semaphore:
            tc = self.GetTextCtrl()
            value = tc.GetValue()
            found_items = []
            for choice in sorted(self.choices):
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
                        if f != best and not f.startswith(best):
                            best = None
                            break
                if best is not None:
                    self.update_semaphore = True
                    tc.SetValue(best)
                    tc.SetInsertionPoint(len(best))
                    tc.SetSelection(len(value), len(best))
        else:
            self.update_semaphore = False
        if self.changed_callback is not None:
            self.changed_callback()
        if not found:
            event.Skip()


class ListCtrlComboPopup(wx.ListCtrl, wx.combo.ComboPopup):

    """ListCtrlComboPopup."""

    def __init__(self, parent, txt_ctrl):
        """Init the ListCtrlComboPopup object."""

        self.txt_ctrl = txt_ctrl
        self.waiting_value = -1
        self.parent = parent
        self.popup_shown = False
        # Since we are using multiple inheritance, and don't know yet
        # which window is to be the parent, we'll do 2-phase create of
        # the ListCtrl instead, and call its Create method later in
        # our Create method.  (See Create below.)
        self.PostCreate(wx.PreListCtrl())

        # Also init the ComboPopup base class.
        wx.combo.ComboPopup.__init__(self)

    def select_item(self, idx=None):
        """Select the first item or by index if one is given."""

        self.txt_ctrl.SetValue(self.GetItemText(idx if idx is not None else 0))

    def get_selected_text(self):
        """Get the TextCtrl value."""

        return self.txt_ctrl.GetValue()

    def set_selected_text(self, text):
        """Set the TextCtrl value."""

        self.txt_ctrl.SetValue(text)

    def set_waiting_value(self, value):
        """Set a value that is to be written to the TextCtrl later."""

        self.waiting_value = value

    def is_value_waiting(self):
        """Return if a selected value is waiting to be set to TextCtrl."""

        return self.waiting_value

    def append_items(self, items):
        """Add items to combo popup."""

        for x in items:
            self.add_item(x)

    def add_item(self, text):
        """Add item to combo popup."""

        if self.GetColumnCount() == 0:
            self.InsertColumn(0, 'Col 0')
        self.InsertStringItem(self.GetItemCount(), text)
        self.SetColumnWidth(0, wx.LIST_AUTOSIZE)

    def on_motion(self, event):
        """Select item on hover."""

        item, flags = self.HitTest(event.GetPosition())
        if item >= 0:
            self.Select(item)

    def next_item(self):
        """Select next item."""

        curitem = self.GetFirstSelected()
        if curitem < self.GetItemCount() - 1:
            self.Select(curitem + 1)

    def prev_item(self):
        """Select previous item."""

        curitem = self.GetFirstSelected()
        if curitem > 0 and self.GetItemCount() > 0:
            self.Select(curitem - 1)

    def set_item(self, idx):
        """Set item by index."""

        self.Select(idx)

    def on_left_down(self, event):
        """Select item and dismiss popup on left mouse click."""

        item, flags = self.HitTest(event.GetPosition())
        if item >= 0:
            self.waiting_value = item
        wx.CallAfter(self.Dismiss)
        event.Skip()

    def clear(self):
        """Clear choices."""

        self.ClearAll()

    def on_key_down(self, event):
        """Select item and dismiss popup on return key."""

        key = event.GetKeyCode()
        if key == wx.WXK_RETURN:
            curitem = self.GetFirstSelected()
            if curitem != -1:
                self.waiting_value = curitem
            wx.CallAfter(self.Dismiss)
        elif key == wx.WXK_DOWN:
            if self.popup_shown:
                self.next_item()
                return
        elif key == wx.WXK_UP:
            if self.popup_shown:
                self.prev_item()
                return
        event.Skip()

    def resize_dropdown(self):
        """Resize the list box column for the dropdown."""

        if self.GetColumnCount():
            if self.GetColumnWidth(0) < self.GetSize()[0] - 20:
                self.SetColumnWidth(0, self.GetSize()[0] - 20)

    def on_resize_dropdown(self, event):
        """ListCtrl resize event."""

        self.resize_dropdown()
        event.Skip()

    # The following methods are those that are overridable from the
    # ComboPopup base class.

    def Init(self):
        """
        This is called immediately after construction finishes.

        You can use self.GetCombo if needed to get to the ComboCtrl instance.
        """

    def Create(self, parent):
        """
        Create the popup child control.

        Return True for success.
        """

        wx.ListCtrl.Create(
            self, parent,
            style=wx.LC_REPORT | wx.LC_NO_HEADER | wx.LC_SINGLE_SEL | wx.SIMPLE_BORDER
        )
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.Bind(wx.EVT_MOTION, self.on_motion)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
        self.Bind(wx.EVT_SIZE, self.on_resize_dropdown)

        return True

    def GetControl(self):
        """Return the widget that is to be used for the popup."""

        return self

    def GetAdjustedSize(self, minWidth, prefHeight, maxHeight):
        """Get adjusted size."""

        return wx.combo.ComboPopup.GetAdjustedSize(self, minWidth, 200, maxHeight)

    def OnPopup(self):
        """Called immediately after the popup is shown."""
        self.popup_shown = True
        wx.combo.ComboPopup.OnPopup(self)

    def OnDismiss(self):
        """Called when popup is dismissed."""
        self.popup_shown = False
        wx.combo.ComboPopup.OnDismiss(self)
