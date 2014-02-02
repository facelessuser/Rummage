"""
notify

Copyright (c) 2013 Isaac Muse <isaacmuse@gmail.com>
License: MIT
"""
from __future__ import absolute_import
import sys

__all__ = ["info", "warning", "error", "setup_notifications", "enable_growl", "has_growl"]

if sys.platform.startswith('win'):
    _PLATFORM = "windows"
elif sys.platform == "darwin":
    _PLATFORM = "osx"
else:
    _PLATFORM = "linux"

if _PLATFORM == "windows":
    from .notify_windows import *
if _PLATFORM == "osx":
    from .notify_osx import *
if _PLATFORM == "linux":
    from .notify_linux import *

from .notify_growl import *


###################################
# Fallback Notifications
###################################
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
            alert()


DEFAULT_NOTIFY = NotifyFallback


###################################
# Notification Calls
###################################
def info(title, message, sound=False):
    """
    Info notification
    """

    send_notify(title, message, sound, "Info")


def error(title, message, sound=False):
    """
    Error notification
    """
    send_notify(title, message, sound, "Error")


def warning(title, message, sound=False):
    """
    Warning notification
    """

    send_notify(title, message, sound, "Warning")


def send_notify(title, message, sound, level):
    """
    Send notification
    """

    default_notify = lambda title, message, sound: DEFAULT_NOTIFY(title, message, sound=sound).Show()
    notify = get_notify()
    growl = get_growl()
    if growl_enabled():
        growl(level, title, message, sound, default_notify)
    elif _PLATFORM in ["osx", "linux"]:
        notify(title, message, sound, default_notify)
    elif _PLATFORM == "windows":
        notify(title, message, sound, windows_icons[level], default_notify)
    else:
        default_notify(title, message, sound)


###################################
# Setup Notifications
###################################
def setup_notifications(app_name, png=None, icon=None, term_notify=(None, None)):
    """
    Setup notifications for all platforms
    """

    setup_growl(app_name, png, alert)
    setup(
        app_name,
        icon if _PLATFORM == "windows" else png,
        term_notify if _PLATFORM == "osx" else None
    )
