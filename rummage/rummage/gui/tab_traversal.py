"""
Custom tab traversal.

Tab traversal is kind of garbage on macOS and Linux, so provide a way
to perform a basic tab traversal for those systems.

Licensed under MIT
Copyright (c) 2017 Isaac Muse <isaacmuse@gmail.com>

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
from .. import util

TAB_FWD = 0
TAB_BACK = 1


class CustomTabTraversal(object):
    """Custom tab traversal."""

    def _set_tab_keybindings(self):
        """Get tab keybindings."""

        keybindings = [
            (wx.ACCEL_NORMAL, wx.WXK_TAB, lambda event, direction=TAB_FWD: self.on_tab_traversal(event, direction)),
            (wx.ACCEL_SHIFT, wx.WXK_TAB, lambda event, direction=TAB_BACK: self.on_tab_traversal(event, direction))
        ]

        # Setup tab keybindings
        tbl = []
        for binding in keybindings:
            keyid = wx.NewId()
            self.Bind(wx.EVT_MENU, binding[2], id=keyid)
            tbl.append((binding[0], binding[1], keyid))

        if len(keybindings):
            self.SetAcceleratorTable(wx.AcceleratorTable(tbl))

    def init_tab_traversal(self, tab_stop, no_tab=None):
        """
        Initialize custom tab traversal.

        tab_stop is the objects to tab from and to.
        no_tab is the objects you can't tab out of (for instance,
        an object that allows tab as an input).
        """

        if no_tab is None:
            no_tab = []

        if False:  # util.platform() != "windows":
            self._set_tab_keybindings()

            self.tab_stop = tab_stop
            self.no_tab = set()

            idx = 0
            self.id_to_tab_idx = {}
            for ts in self.tab_stop:
                self.id_to_tab_idx[ts.GetId()] = idx
                idx += 1
            self._min_tab = 0
            self._max_tab = idx - 1

            for ts in no_tab:
                self.no_tab.add(ts.GetId())

    def on_tab_traversal(self, event, direction):
        """Handle tab traversal."""

        obj = self.FindFocus()
        obj_id = obj.GetId()
        idx = self.id_to_tab_idx.get(obj_id)
        if idx is not None and (obj_id not in self.no_tab or direction):
            max_tab = self.get_max_tab()
            min_tab = self.get_min_tab()
            if direction == TAB_BACK:
                # Tab backwards
                idx = max_tab if idx == min_tab else idx - 1
            elif direction == TAB_FWD:
                # Tab forward
                idx = min_tab if idx == max_tab else idx + 1
            else:
                event.Skip()
                return
            self.tab_stop[idx].SetFocus()
            return
        elif (obj_id not in self.no_tab):
            self.tab_stop[0].SetFocus()
        event.Skip()

    def get_max_tab(self):
        """Get max limit."""

        return self._max_tab

    def get_min_tab(self):
        """Get min limit."""

        return self._min_tab
