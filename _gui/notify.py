"""
Notify

Licensed under MIT
Copyright (c) 2013 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import wx
import sys
import gntp.notifier

if sys.platform.startswith('win'):
    _PLATFORM = "windows"
elif sys.platform == "darwin":
    _PLATFORM = "osx"
else:
    _PLATFORM = "linux"

if _PLATFORM == "windows":
    import winsound

GROWL_ICON = None


growl = gntp.notifier.GrowlNotifier(
    applicationName = "Rummage",
    notifications = ["Info","Warning", "Error"],
    defaultNotifications = ["Info"]
)


def set_growl_icon(icon):
    global GROWL_ICON
    GROWL_ICON = icon


try:
    growl.register()
    def growl_notify(note_type, title, description, sound, fallback):
        try:
            growl.notify(
                noteType = note_type,
                title = title,
                description = description,
                icon=GROWL_ICON,
                sticky = False,
                priority = 1
            )
        except:
            if _PLATFORM != "osx":
                fallback(title, description, sound)
        if sound:
            pass
except:
    print("no growl")
    def growl_notify(note_type, title, description, sound, fallback):
        fallback(title, description, sound)


class Notify(wx.NotificationMessage):
    def __init__(self, *args, **kwargs):
        self.sound = kwargs.get("sound", False)
        self.flags = kwargs.get("flags", 0)
        if "sound" in kwargs:
            del kwargs["sound"]
        if "flags" in kwargs:
            del kwargs["flags"]
        super(Notify, self).__init__(*args, **kwargs)
        self.SetFlags(self.flags)

    def Show(self):
        super(Notify, self).Show()
        if self.sound:
            if _PLATFORM == "windows":
                winsound.PlaySound("*", winsound.SND_ALIAS)


def info(title, message="", sound=False):
    default_notify = lambda title, message, sound: Notify(title, message, flags=wx.ICON_INFORMATION, sound=sound).Show()
    if growl is not None:
        growl_notify("Info", title, message, sound, default_notify)
    elif _PLATFORM != "osx":
        default_notify(title, message, sound)


def error(title, message, sound=False):
    default_notify = lambda title, message, sound: Notify(title, message, flags=wx.ICON_ERROR, sound=sound).Show()
    if growl is not None:
        growl_notify("Error", title, message, sound, default_notify)
    elif _PLATFORM != "osx":
        default_notify(title, message, sound)


def warning(title, message, sound=False):
    default_notify = lambda title, message, sound: Notify(title, message, flags=wx.ICON_WARNING, sound=sound).Show()
    if growl is not None:
        growl_notify("Warning", title, message, sound, default_notify)
    elif _PLATFORM != "osx":
        default_notify(title, message, sound)
