"""
Notify Growl.

Copyright (c) 2013 - 2016 Isaac Muse <isaacmuse@gmail.com>
License: MIT
"""
from __future__ import unicode_literals
import traceback
import sys
from os.path import exists

if sys.platform.startswith('win'):
    from .notify_windows import alert
elif sys.platform == "darwin":
    from .notify_osx import alert
else:
    from .notify_linux import alert

__all__ = ("get_growl", "enable_growl", "growl_enabled", "setup_growl", "has_growl", "growl_destroy")


class Options(object):
    """Notification options."""

    icon = None
    enabled = False
    growl = None
    notify = None

    @classmethod
    def clear(cls):
        """Clear variables."""

        cls.icon = None
        cls.enabled = False
        cls.growl = None
        cls.notify = None


@staticmethod
def notify_growl_fallback(note_type, title, description, sound, fallback):
    """Growl failed to register so create a growl notify that simply calls the fallback."""

    fallback(title, description, sound)


try:
    import gntp.notifier

    @staticmethod
    def notify_growl_call(note_type, title, description, sound, fallback):
        """Send growl notification."""

        try:
            Options.growl.notify(
                noteType=note_type,
                title=title,
                description=description,
                icon=Options.icon,
                sticky=False,
                priority=1
            )

            if sound:
                # Play sound if desired
                alert()
        except Exception:
            print(traceback.format_exc())
            # Fallback notification
            fallback(title, description, sound)
except Exception:
    notify_growl_call = None
    print("no growl")


def enable_growl(enable):
    """Enable/Disable growl."""

    Options.enabled = enable and has_growl()


def has_growl():
    """Return if growl is available."""

    return Options.growl is not None


def growl_enabled():
    """Return if growl is enabled."""

    return has_growl() and Options.enabled


def setup_growl(app_name, icon):
    """Setup growl."""

    Options.icon = None

    try:
        assert(icon is not None and exists(icon))
        with open(icon, "rb") as f:
            Options.icon = f.read()
    except Exception:
        pass

    try:
        # Initialize growl object
        Options.growl = gntp.notifier.GrowlNotifier(
            applicationName=app_name,
            notifications=["Info", "Warning", "Error"],
            defaultNotifications=["Info", "Warning", "Error"]
        )

        Options.growl.register()
    except Exception:
        Options.growl = None

    if Options.growl is not None:
        Options.notify = notify_growl_call


def growl_destroy():
    """Clear the setup."""

    Options.clear()
    Options.notify = notify_growl_fallback


def get_growl():
    """Get growl."""

    return Options.notify


Options.notify = notify_growl_fallback
