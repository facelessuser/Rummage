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

if sys.platform.startswith('win'):
    _PLATFORM = "windows"
elif sys.platform == "darwin":
    _PLATFORM = "osx"
else:
    _PLATFORM = "linux"

if _PLATFORM == "windows":
    import winsound


class Notify(wx.NotificationMessage):
    def __init__(self, *args, **kwargs):
        super(Notify, self).__init__(*args, **kwargs)

    def Show(self, sound=False):
        super(Notify, self).Show()
        if sound:
            if _PLATFORM == "windows":
                winsound.PlaySound("*", winsound.SND_ALIAS)

    def notify(self, title, message, icon=0, sound=False):
        flags = icon
        self.SetFlags(icon)
        self.SetTitle(title)
        self.SetMessage(message)
        self.Show(sound)

    def info(self, title, message, sound=False):
        self.notify(title, message, icon=wx.ICON_INFORMATION, sound=sound)

    def error(self, title, message, sound=False):
        self.notify(title, message, icon=wx.ICON_ERROR, sound=sound)

    def warning(self, title, message, sound=False):
        self.notify(title, message, icon=wx.ICON_WARNING, sound=sound)
