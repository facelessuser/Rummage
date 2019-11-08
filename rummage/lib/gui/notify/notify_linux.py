"""
Notify Linux.

Copyright (c) 2013 - 2016 Isaac Muse <isaacmuse@gmail.com>
License: MIT
"""
import subprocess
import os
from . import util

__all__ = ("get_notify", "alert", "setup", "destroy")

PLAYERS = ('paplay', 'aplay', 'play')


class Options:
    """Notification options."""

    icon = None
    notify = None
    app_name = ""
    sound = None
    player = None

    @classmethod
    def clear(cls):
        """Clear."""

        cls.icon = None
        cls.notify = None
        cls.app_name = ""
        cls.sound = None
        cls.player = None


def _alert(sound=None, player=None):
    """Play an alert sound for the OS."""

    if sound is None and Options.sound is not None:
        sound = Options.sound

    if player is None and Options.player is not None:
        player = Options.player

    if player is not None and sound is not None:
        try:
            if player == 'play':
                subprocess.call([player, '-q', sound])
            else:
                subprocess.call([player, sound])
        except Exception:
            pass


def alert():
    """Alert."""

    _alert()


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

    player = kwargs.get('sound_player')
    if player is not None and player in PLAYERS and util.which(player):
        Options.player = player

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
