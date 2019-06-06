"""
Notify Linux.

Copyright (c) 2013 - 2016 Isaac Muse <isaacmuse@gmail.com>
License: MIT
"""
import subprocess
from os.path import exists
from . import util

__all__ = ("get_notify", "alert", "setup", "destroy")

PLAYERS = ('paplay', 'aplay', 'play')


class Options:
    """Notification options."""

    icon = None
    notify = None
    app_name = ""
    sound = None

    @classmethod
    def clear(cls):
        """Clear."""

        cls.icon = None
        cls.notify = None
        cls.app_name = ""
        cls.sound = None


def alert(sound=None):
    """Play an alert sound for the OS."""

    if Options.sound is not None:
        for player in PLAYERS:
            executable = util.which(player)
            if executable is not None:
                try:
                    if player == 'play':
                        subprocess.call([executable, '-q', Options.sound])
                    else:
                        subprocess.call([executable, Options.sound])
                except Exception:
                    pass
                break


@staticmethod
def notify_osd_fallback(title, message, sound, fallback):
    """Ubuntu Notify OSD notifications fallback (just sound)."""

    # Fallback to wxPython notification
    fallback(title, message, sound)


try:
    if subprocess.call(["notify-send", "--version"]) != 0:
        raise ValueError("Notification support does not appear to be available")

    @staticmethod
    def notify_osd_call(title, message, sound, fallback):
        """Ubuntu Notify OSD notifications."""

        try:
            params = ["notify-send", "-a", Options.app_name, "-t", "3000"]
            if Options.icon is not None:
                params += ["-i", Options.icon]
            if message is not None:
                params += [title, message]
            subprocess.call(params)

            if sound:
                # Play sound if desired
                alert()
        except Exception:
            # Fallback to wxPython notification
            fallback(title, message, sound)
except Exception:
    notify_osd_call = None
    print("no notify osd")


def setup_notify_osd(app_name):
    """Setup Notify OSD."""

    if notify_osd_call is not None:
        Options.app_name = app_name
        Options.notify = notify_osd_call


def setup(app_name, icon, **kwargs):
    """Setup."""

    Options.icon = None
    sound = kwargs.get('sound')
    if sound is not None and os.path.exists(sound):
        Options.sound = sound

    try:
        if icon is None or not os.path.exists(icon):
            raise ValueError("Icon does not appear to be valid")
        Options.icon = icon
    except Exception:
        pass

    if notify_osd_call is not None:
        Options.app_name = app_name
        Options.notify = notify_osd_call


def destroy():
    """Destroy."""

    Options.clear()
    Options.notify = notify_osd_fallback


def get_notify():
    """Get notification."""

    return Options.notify


Options.notify = notify_osd_fallback
