"""
Notify

Licensed under MIT
Copyright (c) 2013 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
# import wx
import sys
import subprocess
from os.path import exists, join

if sys.platform.startswith('win'):
    _PLATFORM = "windows"
elif sys.platform == "darwin":
    _PLATFORM = "osx"
else:
    _PLATFORM = "linux"

if _PLATFORM == "windows":
    import winsound


###################################
# Platform Specific Audio Alert
###################################
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


###################################
# Ubuntu Notify OSD
###################################
NOTIFY_OSD_ICON = None
NOTIFY_OSD = None

def notify_osd_fallback(title, message, sound, fallback):
    """
    Ubuntu Notify OSD notifications fallback (just sound)
    """

    # Fallback to wxpython notification
    fallback(title, message, sound)


NOTIFY_OSD = notify_osd_fallback


try:
    import pynotify

    def notify_osd_call(title, message, sound, fallback):
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

            if sound:
                # Play sound if desired
                play_alert()
        except:
            # Fallback to wxpython notification
            fallback(title, description, sound)


except:
    notify_osd_call = None
    print("no notify osd")


def setup_notify_osd(app_name):
    """
    Setup Notify OSD
    """

    global NOTIFY_OSD
    global notify_osd_call
    if notify_osd_call is not None:
        try:
            pynotify.init(app_name)
        except:
            notify_osd_call = None
    if notify_osd_call is not None:
        NOTIFY_OSD = notify_osd_call


###################################
# Windows and OSX Growl Support
###################################
GROWL_ICON = None
GROWL_ENABLED = False
GROWL = None
NOTIFY_GROWL = None

def notify_growl_fallback(note_type, title, description, sound, fallback):
        """
        Growl failed to register so create a growl notify that simply
        calls the fallback
        """

        fallback(title, description, sound)

NOTIFY_GROWL = notify_growl_fallback

try:
    import gntp.notifier

    def notify_growl_call(note_type, title, description, sound, fallback):
        """
        Send growl notification
        """

        try:
            GROWL.notify(
                noteType = note_type,
                title = title,
                description = description,
                icon=GROWL_ICON,
                sticky = False,
                priority = 1
            )

            if sound:
                # Play sound if desired
                play_alert()
        except:
            # Fallback to wxpython notification
            fallback(title, description, sound)
except:
    notify_growl_call = None
    print("no growl")


def setup_notify_growl(app_name):
    """
    Setup growl
    """

    global GROWL
    global NOTIFY_GROWL
    global notify_growl_call
    try:
        # Init growl object
        GROWL = gntp.notifier.GrowlNotifier(
            applicationName = app_name,
            notifications = ["Info", "Warning", "Error"],
            defaultNotifications = ["Info", "Warning", "Error"]
        )

        GROWL.register()
    except:
        GROWL = None

    if GROWL is not None:
        NOTIFY_GROWL = notify_growl_call


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

    return GROWL is not None


###################################
# Windows Native Notifications
###################################
NOTIFY_WIN_ICON = None
NOTIFY_WIN = None

class WinNotifyLevel(object):
    ICON_INFORMATION = 0x01
    ICON_WARNING = 0x02
    ICON_ERROR = 0x04

def notify_win_fallback(title, message, sound, icon, fallback):
    """
    Notify win calls the fallback
    """

    fallback(title, message, sound)

NOTIFY_WIN = notify_win_fallback

if _PLATFORM == "windows":
    try:
        from win32api import *
        from win32gui import *
        import win32con
        import struct
        import time

        class NotifyWin(object):
            def __init__(self, app_name, icon, tooltip=None):
                """
                Create the taskbar for the application and register it.
                Show nothing by default until called.
                """

                message_map = {
                    win32con.WM_DESTROY: self.OnDestroy,
                    win32con.WM_USER + 20 : self.OnTaskbarNotify,
                }

                self.tooltip = tooltip
                self.visible = False

                # Register window class
                wc = WNDCLASS()
                self.hinst = wc.hInstance = GetModuleHandle(None)
                wc.lpszClassName = app_name
                wc.lpfnWndProc = message_map # could also specify a wndproc.
                self.class_atom = RegisterClass(wc)

                # Create the Window.
                style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
                self.hwnd = CreateWindow(
                    self.class_atom, "Taskbar", style,
                    0, 0, win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT,
                    0, 0, self.hinst, None
                )
                UpdateWindow(self.hwnd)

                self.hicon = self.get_icon(icon)

            def get_icon(self, icon):
                """
                Try to load the given icon from the path given,
                else default to generic application icon from the OS.
                """

                icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
                try:
                    hicon = LoadImage(
                        self.hinst, icon,
                        win32con.IMAGE_ICON,
                        0, 0, icon_flags
                    )
                except:
                    hicon = LoadIcon(0, win32con.IDI_APPLICATION)

                return hicon

            def show_notification(self, title, msg, sound, icon, fallback):
                """
                Attemp to show notifications.  Provide fallback for consistency
                with other notifyicatin methods.
                """

                try:
                    self._show_notification(title, msg, sound, icon)
                except:
                    fallback(title, msg, sound)

            def _show_notification(self, title, msg, sound, icon):
                """
                Call windows API to show notification
                """

                icon_level = 0
                if icon & WinNotifyLevel.ICON_INFORMATION:
                    icon_level |= NIIF_INFO
                elif icon & WinNotifyLevel.ICON_WARNING:
                    icon_level |= NIIF_WARNING
                elif icon & WinNotifyLevel.ICON_ERROR:
                    icon_level |= NIIF_ERROR
                flags = NIF_ICON | NIF_MESSAGE | NIF_TIP
                self.show_icon()
                Shell_NotifyIcon(
                    NIM_MODIFY,
                    (
                        self.hwnd, 0, NIF_INFO, win32con.WM_USER + 20,
                        self.hicon, "Balloon tooltip", msg, 200, title,
                        icon_level
                    )
                )

                if sound:
                    play_alert()

            def OnTaskbarNotify(self, hwnd, msg, wparam, lparam):
                """
                When recieving the dismiss code for the notification,
                hide the icon.
                """

                if lparam == 1028:
                    self.hide_icon()
                    # Noification dismissed

            def show_icon(self):
                """
                Display the taskbar icon
                """

                flags = NIF_ICON | NIF_MESSAGE
                if self.tooltip is not None:
                    flags |= NIF_TIP
                    nid = (self.hwnd, 0, flags, win32con.WM_USER + 20, self.hicon, self.tooltip)
                else:
                    nid = (self.hwnd, 0, flags, win32con.WM_USER + 20, self.hicon)
                if self.visible:
                    self.hide_icon()
                Shell_NotifyIcon(NIM_ADD, nid)
                self.visible = True

            def hide_icon(self):
                """
                Hide icon
                """

                if self.visible:
                    nid = (self.hwnd, 0)
                    Shell_NotifyIcon(NIM_DELETE, nid)
                self.visible = False

            def OnDestroy(self, hwnd, msg, wparam, lparam):
                """
                Remove icon and notification
                """

                self.hide_icon()
                PostQuitMessage(0)

    except:
        NotifyWin = None
        print("no win notify")
else:
    NotifyWin = None
    print("no win notify")


def setup_noitfy_win(app_name, icon):
    """
    Setup win notify
    """

    global NOTIFY_WIN

    if NotifyWin is not None:
        NOTIFY_WIN = NotifyWin(app_name + "Taskbar", icon, app_name).show_notification


###################################
# WxPython Notification
###################################
# try:
#     class WxNotify(wx.NotificationMessage):
#         def __init__(self, *args, **kwargs):
#             """
#             Setup Notify object
#             """

#             self.sound = kwargs.get("sound", False)
#             self.flags = kwargs.get("flags", 0)
#             if "sound" in kwargs:
#                 del kwargs["sound"]
#             if "flags" in kwargs:
#                 del kwargs["flags"]
#             super(Notify, self).__init__(*args, **kwargs)
#             self.SetFlags(self.flags)

#         def Show(self):
#             """
#             Show notification
#             """

#             super(Notify, self).Show()
#             if self.sound:
#                 play_alert()
# except:
#     WxNotify = None
WxNotify = None


class NotifyFallback(object):
    def __init__(self, *args, **kwargs):
        """
        Init class
        """

        self.sound = kwargs.get("sound", False)

    def Show(self):
        """
        Fallback just plays an alert
        """

        if self.sound:
            play_alert()

Notify = WxNotify if WxNotify is not None else NotifyFallback


###################################
# Setup Notifications
###################################
def set_app_icon(app_name, png, icon, pth):
    """
    Set app icon for growl
    """

    global GROWL_ICON
    global NOTIFY_OSD_ICON
    global NOTIFY_WIN_ICON
    GROWL_ICON = icon
    NOTIFY_OSD_ICON = join(pth, app_name + "-notify.png")
    NOTIFY_WIN_ICON = join(pth, app_name + "-notify.ico")
    try:
        if not exists(NOTIFY_OSD_ICON):
            with open(NOTIFY_OSD_ICON, "wb") as f:
                f.write(png)
    except:
        NOTIFY_OSD_ICON = None
        pass

    try:
        if not exists(NOTIFY_WIN_ICON):
            with open(NOTIFY_WIN_ICON, "wb") as f:
                f.write(icon)
    except:
        NOTIFY_WIN_ICON = None


def setup_notifications(app_name, png, icon, config_path):
    """
    Setup notifications for all platforms
    """

    set_app_icon(app_name, png, icon, config_path)
    setup_notify_growl(app_name)
    setup_notify_osd(app_name)
    setup_noitfy_win(app_name, NOTIFY_WIN_ICON)


###################################
# Notification Calls
###################################
def info(title, message="", sound=False):
    """
    Info notification
    """

    default_notify = lambda title, message, sound: Notify(title, message, sound=sound).Show()  # flags=wx.ICON_INFORMATION,
    if has_growl() and GROWL_ENABLED:
        NOTIFY_GROWL("Info", title, message, sound, default_notify)
    elif _PLATFORM == "linux":
        NOTIFY_OSD(title, message, sound, default_notify)
    elif _PLATFORM == "windows":
        NOTIFY_WIN(title, message, sound, WinNotifyLevel.ICON_INFORMATION, default_notify)
    else:
        default_notify(title, message, sound)


def error(title, message, sound=False):
    """
    Error notification
    """

    default_notify = lambda title, message, sound: Notify(title, message, sound=sound).Show()  # flags=wx.ICON_ERROR,
    if has_growl() and GROWL_ENABLED:
        NOTIFY_GROWL("Error", title, message, sound, default_notify)
    elif _PLATFORM == "linux":
        NOTIFY_OSD(title, message, sound, default_notify)
    elif _PLATFORM == "windows":
        NOTIFY_WIN(title, message, sound, WinNotifyLevel.ICON_ERROR, default_notify)
    else:
        default_notify(title, message, sound)


def warning(title, message, sound=False):
    """
    Warning notification
    """

    default_notify = lambda title, message, sound: Notify(title, message, sound=sound).Show()  # flags=wx.ICON_WARNING,
    if has_growl() and GROWL_ENABLED:
        NOTIFY_GROWL("Warning", title, message, sound, default_notify)
    elif _PLATFORM == "linux":
        NOTIFY_OSD(title, message, sound, default_notify)
    elif _PLATFORM == "windows":
        NOTIFY_WIN(title, message, sound, WinNotifyLevel.ICON_WARNING, default_notify)
    else:
        default_notify(title, message, sound)
