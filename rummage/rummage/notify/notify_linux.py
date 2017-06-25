"""
Notify Linux.

Copyright (c) 2013 - 2016 Isaac Muse <isaacmuse@gmail.com>
License: MIT
"""
import subprocess
from os.path import exists
import traceback

__all__ = ("get_notify", "alert", "setup", "destroy")


class Options(object):
    """Notification options."""

    icon = None
    notify = None
    app_name = ""

    @classmethod
    def clear(cls):
        """Clear."""

        cls.icon = None
        cls.notify = None
        cls.app_name = ""


def alert(sound=None):
    """Play an alert sound for the OS."""

    if exists('/usr/share/sounds/gnome/default/alerts/glass.ogg'):
        subprocess.call(['/usr/bin/canberra-gtk-play', '-f', '/usr/share/sounds/gnome/default/alerts/glass.ogg'])
    else:
        subprocess.call(['/usr/bin/canberra-gtk-play', '--id', 'bell'])


@staticmethod
def notify_osd_fallback(title, message, sound, fallback):
    """Ubuntu Notify OSD notifications fallback (just sound)."""

    # Fallback to wxpython notification
    fallback(title, message, sound)


try:
    assert(subprocess.call(["notify-send", "--version"]) == 0)

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
            print(traceback.format_exc())
            # Fallback to wxpython notification
            fallback(title, message, sound)
except Exception:
    notify_osd_call = None
    print("no notify osd")


def setup_notify_osd(app_name):
    """Setup Notify OSD."""

    if notify_osd_call is not None:
        Options.app_name = app_name
        Options.notify = notify_osd_call


def setup(app_name, icon, *args):
    """Setup."""

    Options.icon = None

    try:
        assert(icon is not None and exists(icon))
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
