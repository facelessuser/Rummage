"""
Notify Growl.

Copyright (c) 2013 - 2016 Isaac Muse <isaacmuse@gmail.com>
License: MIT
"""
import traceback
import sys
import os

IS_LINUX = False
if sys.platform.startswith('win'):
    from .notify_windows import _alert
elif sys.platform == "darwin":
    from .notify_osx import _alert
else:
    from .notify_linux import _alert
    IS_LINUX = True

__all__ = ("get_growl", "enable_growl", "growl_enabled", "setup_growl", "has_growl", "growl_destroy")


class Options:
    """Notification options."""

    icon = None
    enabled = False
    growl = None
    notify = None
    sound = None
    player = None

    @classmethod
    def clear(cls):
        """Clear variables."""

        cls.icon = None
        cls.enabled = False
        cls.growl = None
        cls.notify = None
        cls.sound = None
        cls.player = None


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


def alert():
    """Alert."""

    if IS_LINUX:
        _alert(Options.sound, player=Options.player)
    else:
        _alert(Options.sound)


def setup_growl(app_name, icon, **kwargs):
    """Setup growl."""

    Options.icon = None
    Options.player = None

    sound = kwargs.get('sound')
    if sound is not None and os.path.exists(sound):
        Options.sound = sound

    player = kwargs.get('sound_player')
    if IS_LINUX:
        Options.player = player

    try:
        if icon is None or not os.path.exists(icon):
            raise ValueError("Icon does not appear to be valid")
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
