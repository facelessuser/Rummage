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

if _PLATFORM == "osx":
    from ctypes import *
    import ctypes.util as util

    appkit = cdll.LoadLibrary(util.find_library('AppKit'))
    cf = cdll.LoadLibrary(util.find_library('CoreFoundation'))
    objc = cdll.LoadLibrary(util.find_library('objc'))

    kCFStringEncodingUTF8 = 0x08000100

    cf.CFStringCreateWithCString.restype = c_void_p
    cf.CFStringCreateWithCString.argtypes = [c_void_p, c_char_p, c_uint32]

    objc.objc_getClass.restype = c_void_p
    objc.sel_registerName.restype = c_void_p
    objc.objc_msgSend.restype = c_void_p
    objc.objc_msgSend.argtypes = [c_void_p, c_void_p]

    NSSound = c_void_p(objc.objc_getClass('NSSound'))
    NSAutoreleasePool = c_void_p(objc.objc_getClass('NSAutoreleasePool'))


GROWL_ICON = None
GROWL_ENABLED = False


growl = gntp.notifier.GrowlNotifier(
    applicationName = "Rummage",
    notifications = ["Info","Warning", "Error"],
    defaultNotifications = ["Info"]
)


def enable_growl(enable):
    global GROWL_ENABLED
    GROWL_ENABLED = enable and has_growl()


def has_growl():
    return growl is not None


def set_growl_icon(icon):
    global GROWL_ICON
    GROWL_ICON = icon


def _nsstring(string):
    return c_void_p(cf.CFStringCreateWithCString(None, string.encode('utf8'), kCFStringEncodingUTF8))


def _callmethod(obj, method, *args, **kwargs):
    cast_return = kwargs.get("cast_return", c_void_p)
    return cast_return(objc.objc_msgSend(obj, objc.sel_registerName(method), *args))


def play_alert(sound=None):
    if _PLATFORM == "osx":
        pool = _callmethod(_callmethod(NSAutoreleasePool, "alloc"), "init")
        snd = _nsstring(sound if sound is not None else "Glass")
        soundobj = _callmethod(NSSound, "soundNamed:", snd)
        _callmethod(soundobj, "play")
        _callmethod(pool, "drain")
        del pool
    elif _PLATFORM == "windows":
        snd = sound if sound is not None else "*"
        winsound.PlaySound(snd, winsound.SND_ALIAS)


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
            play_alert()
except:
    print("no growl")
    def growl_notify(note_type, title, description, sound, fallback):
        if _PLATFORM != "osx":
            fallback(title, description, sound)
        elif sound:
            play_alert()


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
            play_alert()


def info(title, message="", sound=False):
    default_notify = lambda title, message, sound: Notify(title, message, flags=wx.ICON_INFORMATION, sound=sound).Show()
    if has_growl() and GROWL_ENABLED:
        growl_notify("Info", title, message, sound, default_notify)
    elif _PLATFORM != "osx":
        default_notify(title, message, sound)


def error(title, message, sound=False):
    default_notify = lambda title, message, sound: Notify(title, message, flags=wx.ICON_ERROR, sound=sound).Show()
    if has_growl() and GROWL_ENABLED:
        growl_notify("Error", title, message, sound, default_notify)
    elif _PLATFORM != "osx":
        default_notify(title, message, sound)


def warning(title, message, sound=False):
    default_notify = lambda title, message, sound: Notify(title, message, flags=wx.ICON_WARNING, sound=sound).Show()
    if has_growl() and GROWL_ENABLED:
        growl_notify("Warning", title, message, sound, default_notify)
    elif _PLATFORM != "osx":
        default_notify(title, message, sound)
