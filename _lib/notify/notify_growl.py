"""
notify_growl

Copyright (c) 2013 Isaac Muse <isaacmuse@gmail.com>
License: MIT
"""
import traceback
from os.path import exists

__all__ = ["get_growl", "enable_growl", "growl_enabled", "setup_growl", "has_growl"]


class Options(object):
    icon = None
    enabled = False
    growl = None
    notify = None


def alert():
    pass


@staticmethod
def notify_growl_fallback(note_type, title, description, sound, fallback):
        """
        Growl failed to register so create a growl notify that simply
        calls the fallback
        """

        fallback(title, description, sound)


try:
    import gntp.notifier

    @staticmethod
    def notify_growl_call(note_type, title, description, sound, fallback):
        """
        Send growl notification
        """

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
        except:
            print(traceback.format_exc())
            # Fallback notification
            fallback(title, description, sound)
except:
    notify_growl_call = None
    print("no growl")


def enable_growl(enable):
    """
    Enable/Disable growl
    """

    Options.enabled = enable and has_growl()


def has_growl():
    """
    Return if growl is available
    """

    return Options.growl is not None


def growl_enabled():
    """
    Return if growl is enabled
    """

    return has_growl() and Options.enabled


def setup_growl(app_name, icon, alert_function):
    """
    Setup growl
    """

    global alert
    global notify_growl_call
    Options.icon = None

    alert = alert_function

    try:
        assert(icon is not None and exists(icon))
        with open(icon, "rb") as f:
            Options.icon = f.read()
    except:
        pass

    try:
        # Init growl object
        Options.growl = gntp.notifier.GrowlNotifier(
            applicationName=app_name,
            notifications=["Info", "Warning", "Error"],
            defaultNotifications=["Info", "Warning", "Error"]
        )

        Options.growl.register()
    except:
        print(traceback.format_exc())
        Options.growl = None

    if Options.growl is not None:
        Options.notify = notify_growl_call


def get_growl():
    return Options.notify


Options.notify = notify_growl_fallback
