"""
Custom Status Bar
https://gist.github.com/facelessuser/5750045

Licensed under MIT
Copyright (c) 2013 Isaac Muse <isaacmuse@gmail.com>
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import wx
import wx.lib.agw.supertooltip as STT
from collections import OrderedDict
import sys

if sys.platform.startswith('win'):
    _PLATFORM = "windows"
elif sys.platform == "darwin":
    _PLATFORM = "osx"
else:
    _PLATFORM = "linux"


class ContextMenu(wx.Menu):
    def __init__(self, parent, menu, pos):
        """
        Attach the context menu to to the parent
        at the location given and with the items
        defined
        """

        wx.Menu.__init__(self)
        self._callbacks = {}

        for i in menu:
            menuid = wx.NewId()
            item = wx.MenuItem(self, menuid, i[0])
            self._callbacks[menuid] = i[1]
            self.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.on_callback, item)

        parent.PopupMenu(self, pos)

    def on_callback(self, event):
        """
        Execute the menu item callback
        """

        menuid = event.GetId()
        self._callbacks[menuid](event)
        event.Skip()


class ToolTip(STT.SuperToolTip):
    def __init__(self, target, message, header="", style="Office 2007 Blue", start_delay=.1):
        """
        Attach the defined tooltip to the target
        """

        super(ToolTip, self).__init__(message, header=header)
        self.SetTarget(target)
        self.ApplyStyle(style)
        self.SetStartDelay(start_delay)
        target.tooltip = self

    def hide(self):
        """
        Hide the tooltip
        """

        if self._superToolTip:
            self._superToolTip.Destroy()


class TimedStatusExtension(object):
    def set_timed_status(self, text):
        """
        Set the status for a short time.
        Save the previous status for restore
        when the timed status completes.
        """

        if self.text_timer.IsRunning():
            self.text_timer.Stop()
        else:
            self.saved_text = self.GetStatusText(0)
        self.SetStatusText(text, 0)
        self.text_timer.Start(5000, oneShot=True)

    def sb_time_setup(self):
        """
        Setup timer for timed status
        """

        self.saved_text = ""
        self.text_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.clear_text, self.text_timer)

    def clear_text(self, event):
        """
        Clear the status
        """

        self.SetStatusText(self.saved_text, 0)

    def set_status(self, text):
        """
        Set the status
        """

        if self.text_timer.IsRunning():
            self.text_timer.Stop()
        self.SetStatusText(text, 0)


class IconTrayExtension(object):
    def remove_icon(self, name):
        """
        Remove an icon from the tray
        """

        if name in self.sb_icons:
            self.hide_tooltip(name)
            self.sb_icons[name].Destroy()
            del self.sb_icons[name]
            self.place_icons(resize=True)

    def hide_tooltip(self, name):
        """
        Hide the tooltip
        """

        if self.sb_icons[name].tooltip:
            self.sb_icons[name].tooltip.hide()

    def set_icon(self, name, icon, msg=None, context=None):
        """
        Set the given icon in the tray.
        Attach a menu and/or tooltip if provided.
        """

        if name in self.sb_icons:
            self.hide_tooltip(name)
            self.sb_icons[name].Destroy()
        self.sb_icons[name] = wx.StaticBitmap(self, bitmap=icon)
        if msg is not None:
            ToolTip(self.sb_icons[name], msg)
        if context is not None:
            self.sb_icons[name].Bind(wx.EVT_RIGHT_DOWN, lambda e: self.show_menu(name, context))
        self.place_icons(resize=True)

    def show_menu(self, name, context):
        """
        Show context menu on icon in tray
        """

        self.hide_tooltip(name)
        ContextMenu(self, context, self.sb_icons[name].GetPosition())

    def place_icons(self, resize=False):
        """
        Calculate new icon position and icon tray size
        """

        x_offset = 0
        if resize:
            if _PLATFORM == "osx":
                self.SetStatusWidths([-1, len(self.sb_icons) * 20 + 10])
            elif _PLATFORM == "windows":
                # In wxPython 2.9, the first icon inserted changes the size, additional icons don't
                self.SetStatusWidths([-1, (len(self.sb_icons) - 1) * 20 + 1])
            else:
                # Linux? Haven't tested yet.
                self.SetStatusWidths([-1, len(self.sb_icons) * 20 + 1])
        rect = self.GetFieldRect(1)
        for v in self.sb_icons.values():
            v.SetPosition((rect.x + x_offset, rect.y))
            v.Hide()
            v.Show()
            x_offset += 20

    def on_sb_size(self, event):
        """
        Ensure icons are properly placed on resize
        """

        event.Skip()
        self.place_icons()

    def sb_tray_setup(self):
        """
        Setup the status bar with icon tray
        """

        self.SetFieldsCount(2)
        self.SetStatusText('', 0)
        self.SetStatusWidths([-1, 1])
        self.sb_icons = OrderedDict()
        self.Bind(wx.EVT_SIZE, self.on_sb_size)


class CustomStatusExtension(IconTrayExtension, TimedStatusExtension):
    def sb_setup(self):
        """
        Setup the extention variant of the CustomStatusBar object
        """

        self.sb_tray_setup()
        self.sb_time_setup()


class CustomStatusBar(wx.StatusBar, CustomStatusExtension):
    def __init__(self, parent):
        """
        Init the CustomStatusBar object
        """

        super(CustomStatusBar, self).__init__(parent)
        self.sb_setup()


def extend(instance, extension):
    """
    Extend instance with extension class
    """

    instance.__class__ = type(
        '%s_extended_with_%s' % (instance.__class__.__name__, extension.__name__),
        (instance.__class__, extension),
        {}
    )


def extend_sb(sb):
    """
    Extend the statusbar
    """

    extend(sb, CustomStatusExtension)
    sb.sb_setup()
