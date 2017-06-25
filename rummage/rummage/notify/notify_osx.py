"""
Notify OSX.

Copyright (c) 2013 - 2016 Isaac Muse <isaacmuse@gmail.com>
License: MIT
"""
from __future__ import unicode_literals
import subprocess
import traceback
from os.path import exists
import ctypes
import ctypes.util
import sys
import platform

__all__ = ("get_notify", "alert", "setup", "destroy")

PY3 = (3, 0) <= sys.version_info < (4, 0)

if PY3:
    binary_type = bytes  # noqa
else:
    binary_type = str

appkit = ctypes.cdll.LoadLibrary(ctypes.util.find_library('AppKit'))
cf = ctypes.cdll.LoadLibrary(ctypes.util.find_library('CoreFoundation'))
objc = ctypes.cdll.LoadLibrary(ctypes.util.find_library('objc'))

kCFStringEncodingUTF8 = 0x08000100

cf.CFStringCreateWithCString.restype = ctypes.c_void_p
cf.CFStringCreateWithCString.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_uint32]

objc.objc_getClass.restype = ctypes.c_void_p
objc.sel_registerName.restype = ctypes.c_void_p
objc.objc_msgSend.restype = ctypes.c_void_p
objc.objc_msgSend.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

NSSound = ctypes.c_void_p(objc.objc_getClass('NSSound'))
NSAutoreleasePool = ctypes.c_void_p(objc.objc_getClass('NSAutoreleasePool'))


def _nsstring(string):
    """Return an NSString object."""

    return ctypes.c_void_p(cf.CFStringCreateWithCString(None, string.encode('utf8'), kCFStringEncodingUTF8))


def _callmethod(obj, method, *args, **kwargs):
    """Call the ObjC method."""

    cast_return = kwargs.get("cast_return", ctypes.c_void_p)
    return cast_return(objc.objc_msgSend(obj, objc.sel_registerName(method), *args))


def _is_ver_okay():
    """See if version is > 10.8."""

    try:
        return float(platform.mac_ver()[0].split('.')[:2]) >= 10.9
    except Exception:
        return False


class Options(object):
    """Notification options."""

    notify = None
    sender = "com.apple.Terminal"
    terminal_notifier = None
    app_name = ""
    icon = None

    @classmethod
    def clear(cls):
        """Clear."""

        cls.notify = None
        cls.sender = "com.apple.Terminal"
        cls.terminal_notifier = None
        cls.app_name = ""
        cls.icon = None


def alert(sound=None):
    """Play an alert sound for the OS."""

    pool = _callmethod(_callmethod(NSAutoreleasePool, "alloc"), "init")
    snd = _nsstring(sound if sound is not None else "Glass")
    soundobj = _callmethod(NSSound, "soundNamed:", snd)
    _callmethod(soundobj, "play")
    _callmethod(pool, "drain")
    del pool


@staticmethod
def notify_osx_fallback(title, message, sound, fallback):
    """OSX notifications fallback (just sound)."""

    # Fallback to wxpython notification
    fallback(title, message, sound)


@staticmethod
def notify_osx_call(title, message, sound, fallback):
    """OSX notifications."""

    try:
        assert(Options.terminal_notifier is not None and exists(Options.terminal_notifier))
        # Show Notification here
        params = [Options.terminal_notifier, "-title", Options.app_name, "-timeout", "5"]
        if message is not None:
            params += ["-message", message]
        if title is not None:
            params += ["-subtitle", title]
        if Options.sender is not None:
            params += ["-sender", Options.sender]
        if Options.icon is not None:
            params += ["-appIcon", Options.icon]
        if sound:
            params += ["-sound", "Glass"]
        subprocess.Popen(params)

        # if sound:
        #     # Play sound if desired
        #     alert()
    except Exception:
        print(traceback.format_exc())
        # Fallback notification
        fallback(title, message, sound)


def setup(app_name, icon, *args):
    """Setup."""

    term_notify = None
    sender = None

    if len(args) and len(args[0]) == 3:
        term_notify = args[0][0]
        sender = args[0][1]
        notify_icon = args[0][2]

        if term_notify is not None and isinstance(term_notify, binary_type):
            term_notify = term_notify.decode('utf-8')

        if sender is not None and isinstance(sender, binary_type):
            sender = sender.decode('utf-8')

        if _is_ver_okay():
            notify_icon = None
        elif notify_icon is not None and isinstance(notify_icon, binary_type):
            notify_icon = notify_icon.decode('utf-8')

    Options.app_name = app_name

    try:
        assert(term_notify is not None and exists(term_notify))
        Options.terminal_notifier = term_notify
        if sender is not None:
            Options.sender = sender
        if notify_icon is not None and exists(notify_icon):
            Options.icon = notify_icon
        Options.notify = notify_osx_call
    except Exception:
        print(traceback.format_exc())


def destroy():
    """Destroy."""

    Options.clear()
    Options.notify = notify_osx_fallback


def get_notify():
    """Get notification."""

    return Options.notify


Options.notify = notify_osx_fallback
