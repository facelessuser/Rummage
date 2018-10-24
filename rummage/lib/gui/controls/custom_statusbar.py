"""
Custom Status Bar.

https://gist.github.com/facelessuser/5750045

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
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
from __future__ import unicode_literals
from collections import OrderedDict
import wx
import wx.lib.agw.supertooltip
from ... import util


class ContextMenu(wx.Menu):
    """Context Menu."""

    def __init__(self, menu):
        """Attach the context menu to to the parent with the defined items."""

        wx.Menu.__init__(self)
        self._callbacks = {}

        for i in menu:
            menuid = wx.NewId()
            item = wx.MenuItem(self, menuid, i[0])
            self._callbacks[menuid] = i[1]
            self.Append(item)
            self.Bind(wx.EVT_MENU, self.on_callback, item)

    def on_callback(self, event):
        """Execute the menu item callback."""

        menuid = event.GetId()
        self._callbacks[menuid](event)
        event.Skip()


class ToolTip(wx.lib.agw.supertooltip.SuperToolTip):
    """Tooltip."""

    def __init__(self, target, message, header="", style="Office 2007 Blue", start_delay=.1):
        """Attach the defined tooltip to the target."""

        super(ToolTip, self).__init__(message, header=header)
        self.SetTarget(target)
        self.ApplyStyle(style)
        self.SetStartDelay(start_delay)
        target.tooltip = self

    def hide(self):
        """Hide the tooltip."""

        if self._superToolTip:
            self._superToolTip.Destroy()


class TimedStatusExtension(object):
    """Timed status in status bar."""

    kill = False

    def set_timed_status(self, text, index=0):
        """
        Set the status for a short time.

        Save the previous status for restore
        when the timed status completes.
        """

        if self.kill:
            return

        if self.text_timer[index].IsRunning():
            self.text_timer[index].Stop()
        else:
            self.saved_text = self.GetStatusText(index)
        self.SetStatusText(text, index)
        self.text_timer[index].Start(5000, oneShot=True)

    def sb_time_setup(self, field_count):
        """Setup timer for timed status."""

        if self.kill:
            return

        self.field_count = field_count
        self.saved_text = [""] * field_count
        self.text_timer = [wx.Timer(self)] * field_count
        count = 0
        for x in self.text_timer:
            self.Bind(wx.EVT_TIMER, lambda event, index=count: self.clear_text(event, index), self.text_timer[count])
            count += 1

    def clear_text(self, event, index):
        """Clear the status."""

        if self.kill:
            return

        self.SetStatusText(self.saved_text, index)

    def set_status(self, text, index=0):
        """Set the status."""

        if self.kill:
            return

        if self.text_timer[index].IsRunning():
            self.text_timer[index].Stop()
        self.SetStatusText(text, index)

    def kill_timers(self):
        """Kill timer event."""

        self.kill = True
        count = 0
        for x in self.text_timer[:]:
            if x.IsRunning():
                x.Stop()
            x.Destroy()
            del self.text_timer[count]
            count += 1


class IconTrayExtension(object):
    """Add icon tray extension."""

    fields = [-1]

    def sb_tray_setup(self):
        """Setup the status bar with icon tray."""

        self.SetFieldsCount(len(self.fields) + 1)
        self.SetStatusText('', 0)
        self.SetStatusWidths(self.fields + [1])
        self.sb_icons = OrderedDict()
        self.Bind(wx.EVT_SIZE, self.on_sb_size)

    def remove_icon(self, name):
        """Remove an icon from the tray."""

        if name in self.sb_icons:
            self.hide_tooltip(name)
            self.sb_icons[name].Destroy()
            del self.sb_icons[name]
            self.place_icons(resize=True)

    def hide_tooltip(self, name):
        """Hide the tooltip."""

        if self.sb_icons[name].tooltip:
            self.sb_icons[name].tooltip.hide()

    def set_icon(
        self, name, icon, msg=None, context=None,
        click_right=None, click_left=None,
        dclick_right=None, dclick_left=None
    ):
        """
        Set the given icon in the tray.

        Attach a menu and/or tooltip if provided.
        """

        if name in self.sb_icons:
            self.hide_tooltip(name)
            self.sb_icons[name].Destroy()
        bmp = wx.StaticBitmap(self)
        bmp.SetBitmap(label=icon)
        self.sb_icons[name] = bmp
        if msg is not None:
            ToolTip(self.sb_icons[name], msg)
        if click_left is not None:
            self.sb_icons[name].Bind(wx.EVT_LEFT_DOWN, click_left)
        if context is not None:
            self.sb_icons[name].Bind(wx.EVT_RIGHT_DOWN, lambda e: self.show_menu(name, context))
        elif click_right is not None:
            self.sb_icons[name].Bind(wx.EVT_RIGHT_DOWN, click_right)
        if dclick_left is not None:
            self.sb_icons[name].Bind(wx.EVT_LEFT_DCLICK, dclick_left)
        if dclick_right is not None:
            self.sb_icons[name].Bind(wx.EVT_RIGHT_DCLICK, dclick_right)
        self.place_icons(resize=True)

    def show_menu(self, name, context):
        """Show context menu on icon in tray."""

        self.hide_tooltip(name)
        pos = self.sb_icons[name].GetPosition()
        menu = ContextMenu(context)
        self.PopupMenu(menu, pos)
        menu.Destroy()

    def place_icons(self, resize=False):
        """Calculate new icon position and icon tray size."""

        x_offset = 0
        if resize:
            platform = util.platform()
            if platform in "osx":
                # macOS must increment by 10
                self.SetStatusWidths([-1, len(self.sb_icons) * 20 + 10])
            elif platform == "windows":
                # In at least wxPython 2.9+, the first icon inserted changes the size, additional icons don't.
                # I've only tested >= 2.9.
                if len(self.sb_icons):
                    self.SetStatusWidths([-1, (len(self.sb_icons) - 1) * 20 + 1])
                else:
                    self.SetStatusWidths([-1, len(self.sb_icons) * 20 + 1])
            else:
                # Linux? Should be fine with 1, but haven't tested yet.
                self.SetStatusWidths([-1, len(self.sb_icons) * 20 + 1])
        rect = self.GetFieldRect(len(self.fields))
        for v in self.sb_icons.values():
            v.SetPosition((rect.x + x_offset, rect.y))
            v.Hide()
            v.Show()
            x_offset += 20

    def on_sb_size(self, event):
        """Ensure icons are properly placed on resize."""

        event.Skip()
        self.place_icons()

    def destroy_icons(self):
        """Destroy Icons."""

        icons = []
        for name in self.sb_icons.keys():
            icons.append(name)
        for name in icons:
            self.remove_icon(name)


class CustomStatusExtension(IconTrayExtension, TimedStatusExtension):
    """Custom status extension."""

    def sb_setup(self, fields):
        """Setup the extension variant of the `CustomStatusBar` object."""

        if util.platform() == "windows":
            self.SetDoubleBuffered(True)

        self.fields = fields
        self.sb_tray_setup()
        self.sb_time_setup(len(self.fields))

    def tear_down(self):
        """Tear down dynamic stuff."""

        self.kill_timers()
        self.destroy_icons()


class CustomStatusBar(wx.StatusBar, CustomStatusExtension):
    """Custom status bar."""

    def __init__(self, parent, name, fields=None):
        """Initialize the `CustomStatusBar` object."""

        field_array = [-1] if not fields else fields[:]
        super(CustomStatusBar, self).__init__(
            parent,
            id=wx.ID_ANY,
            style=wx.STB_DEFAULT_STYLE,
            name=name
        )
        self.sb_setup(field_array)


def extend(instance, extension):
    """Extend instance with extension class."""

    instance.__class__ = type(
        '%s_extended_with_%s' % (
            instance.__class__.__name__, extension.__name__
        ),
        (instance.__class__, extension),
        {}
    )


def extend_sb(sb, fields=None):
    """Extend the status bar."""

    field_array = [-1] if not fields else fields[:]
    extend(sb, CustomStatusExtension)
    sb.sb_setup(field_array)
