"""
notify_linux

Copyright (c) 2013 Isaac Muse <isaacmuse@gmail.com>
License: MIT
"""
import subprocess
from os.path import exists
import traceback

__all__ = ["get_notify", "alert", "setup"]


class Options(object):
    icon = None
    notify = None
    app_name = ""


def alert(sound=None):
    """
    Play an alert sound for the OS
    """

    if exists('/usr/share/sounds/gnome/default/alerts/glass.ogg'):
        subprocess.call(['/usr/bin/canberra-gtk-play', '-f', '/usr/share/sounds/gnome/default/alerts/glass.ogg'])
    else:
        subprocess.call(['/usr/bin/canberra-gtk-play', '--id', 'bell'])


@staticmethod
def notify_osd_fallback(title, message, sound, fallback):
    """
    Ubuntu Notify OSD notifications fallback (just sound)
    """

    # Fallback to wxpython notification
    fallback(title, message, sound)


try:
    assert(subprocess.call(["notify-send", "--version"]) == 0)

    @staticmethod
    def notify_osd_call(title, message, sound, fallback):
        """
        Ubuntu Notify OSD notifications
        """

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
        except:
            print(traceback.format_exc())
            # Fallback to wxpython notification
            fallback(title, message, sound)
except:
    notify_osd_call = None
    print("no notify osd")


def setup_notify_osd(app_name):
    """
    Setup Notify OSD
    """

    global notify_osd_call
    if notify_osd_call is not None:
        Options.app_name = app_name
        Options.notify = notify_osd_call


def setup(app_name, icon, *args):
    """
    Setup
    """

    global notify_osd_call
    Options.icon = None

    try:
        assert(icon is not None and exists(icon))
        Options.icon = icon
    except:
        pass

    if notify_osd_call is not None:
        Options.app_name = app_name
        Options.notify = notify_osd_call


def get_notify():
    return Options.notify


Options.notify = notify_osd_fallback
