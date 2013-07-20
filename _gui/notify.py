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
import subprocess
from os.path import exists, join
from version import app as APP_NAME

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

NOTIFY_OSD_ICON = None
GROWL_ICON = None
GROWL_ENABLED = False


try:
    import pynotify
    pynotify.init(APP_NAME)


    def notify_osd(title, message, sound):
        """
        Ubuntu Notify OSD notifications
        """

        try:
            notice = pynotify.Notification(
                title,
                message,
                NOTIFY_OSD_ICON
            )
            notice.show()
        except:
            pass

        if sound:
            # Play sound if desired
            play_alert()

except:

    def notify_osd(title, message, sound):
        """
        Ubuntu Notify OSD notifications fallback (just sound)
        """

        if sound:
            # Play sound if desired
            play_alert()

    print("no notify osd")


# Init growl object
growl = gntp.notifier.GrowlNotifier(
    applicationName = APP_NAME,
    notifications = ["Info", "Warning", "Error"],
    defaultNotifications = ["Info", "Warning", "Error"]
)


def enable_growl(enable):
    """
    Enable/Disable growl
    """
    global GROWL_ENABLED
    GROWL_ENABLED = enable and has_growl()


def has_growl():
    """
    Return if growl is available
    """

    return growl is not None


def set_app_icon(icon, pth):
    """
    Set app icon for growl
    """

    global GROWL_ICON
    global NOTIFY_OSD_ICON
    GROWL_ICON = icon
    NOTIFY_OSD_ICON = join(pth, APP_NAME + "-notify.png")
    try:
        if not exists(NOTIFY_OSD_ICON):
            with open(NOTIFY_OSD_ICON, "w") as f:
                f.write(icon)
    except:
        NOTIFY_OSD_ICON = None
        pass


def _nsstring(string):
    """
    Return an NSString object
    """

    return c_void_p(cf.CFStringCreateWithCString(None, string.encode('utf8'), kCFStringEncodingUTF8))


def _callmethod(obj, method, *args, **kwargs):
    """
    ObjC method call
    """

    cast_return = kwargs.get("cast_return", c_void_p)
    return cast_return(objc.objc_msgSend(obj, objc.sel_registerName(method), *args))


def play_alert(sound=None):
    """
    Play an alert sound for the OS
    """

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
    else:
        if exists('/usr/share/sounds/gnome/default/alerts/glass.ogg'):
            subprocess.call(['/usr/bin/canberra-gtk-play', '-f', '/usr/share/sounds/gnome/default/alerts/glass.ogg'])
        else:
            subprocess.call(['/usr/bin/canberra-gtk-play','--id','bell'])


try:
    # Attempt to register growl
    growl.register()


    def growl_notify(note_type, title, description, sound, fallback):
        """
        Send growl notification
        """

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
            # Fallback to wxpython notification
            if _PLATFORM != "osx":
                fallback(title, description, sound)
        if sound:
            # Play sound if desired
            play_alert()
except:
    print("no growl")


    def growl_notify(note_type, title, description, sound, fallback):
        """
        Growl failed to register so create a growl notify that simply
        calls the fallback
        """

        if _PLATFORM != "osx":
            # Fallback to wxpython notification
            fallback(title, description, sound)
        elif sound:
            # Play sound if desired
            play_alert()


class Notify(wx.NotificationMessage):
    def __init__(self, *args, **kwargs):
        """
        Setup Notify object
        """

        self.sound = kwargs.get("sound", False)
        self.flags = kwargs.get("flags", 0)
        if "sound" in kwargs:
            del kwargs["sound"]
        if "flags" in kwargs:
            del kwargs["flags"]
        super(Notify, self).__init__(*args, **kwargs)
        self.SetFlags(self.flags)

    def Show(self):
        """
        Show notification
        """

        super(Notify, self).Show()
        if self.sound:
            play_alert()


def info(title, message="", sound=False):
    """
    Info notification
    """

    default_notify = lambda title, message, sound: Notify(title, message, flags=wx.ICON_INFORMATION, sound=sound).Show()
    if has_growl() and GROWL_ENABLED:
        growl_notify("Info", title, message, sound, default_notify)
    elif _PLATFORM == "linux":
        notify_osd(title, message, sound)
    elif _PLATFORM != "osx" or _PLATFORM != "linux":
        default_notify(title, message, sound)


def error(title, message, sound=False):
    """
    Error notification
    """

    default_notify = lambda title, message, sound: Notify(title, message, flags=wx.ICON_ERROR, sound=sound).Show()
    if has_growl() and GROWL_ENABLED:
        growl_notify("Error", title, message, sound, default_notify)
    elif _PLATFORM == "linux":
        notify_osd(title, message, sound)
    elif _PLATFORM != "osx" or _PLATFORM != "linux":
        default_notify(title, message, sound)


def warning(title, message, sound=False):
    """
    Warning notification
    """

    default_notify = lambda title, message, sound: Notify(title, message, flags=wx.ICON_WARNING, sound=sound).Show()
    if has_growl() and GROWL_ENABLED:
        growl_notify("Warning", title, message, sound, default_notify)
    elif _PLATFORM == "linux":
        notify_osd(title, message, sound)
    elif _PLATFORM != "osx" or _PLATFORM != "linux":
        default_notify(title, message, sound)
