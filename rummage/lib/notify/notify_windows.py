"""
Notify windows.

Copyright (c) 2013 - 2015 Isaac Muse <isaacmuse@gmail.com>
License: MIT
"""
import traceback
import winsound
from os.path import exists

__all__ = ("get_notify", "alert", "setup", "windows_icons")


class Options(object):

    """Notification options."""

    notify = None
    instance = None


def alert(sound=None):
    """Play an alert sound for the OS."""

    snd = sound if sound is not None else "*"
    winsound.PlaySound(snd, winsound.SND_ALIAS)


class WinNotifyLevel(object):

    """Windows notification level."""

    ICON_INFORMATION = 0x01
    ICON_WARNING = 0x02
    ICON_ERROR = 0x04


windows_icons = {
    "Info": WinNotifyLevel.ICON_INFORMATION,
    "Warning": WinNotifyLevel.ICON_WARNING,
    "Error": WinNotifyLevel.ICON_ERROR
}


def notify_win_fallback(title, message, sound, icon, fallback):
    """Notify win calls the fallback."""

    fallback(title, message, sound)


try:
    from win32api import *
    from win32gui import *
    import win32con

    class WindowsNotify(object):

        """Windows notification class."""

        atom_name = None
        window_handle = None
        taskbar_icon = None

        def __init__(self, app_name, icon, tooltip=None):
            """
            Create the taskbar for the application and register it.

            Show nothing by default until called.
            """

            message_map = {
                win32con.WM_DESTROY: self.OnDestroy,
                win32con.WM_USER + 20: self.OnTaskbarNotify,
            }

            self.tooltip = tooltip
            self.visible = False

            # Register window class
            wc = WNDCLASS()
            self.hinst = wc.hInstance = GetModuleHandle(None)
            wc.lpszClassName = app_name
            wc.lpfnWndProc = message_map  # could also specify a wndproc.
            if WindowsNotify.atom_name is not None:
                self._destroy_window()
                UnregisterClass(WindowsNotify.atom_name, None)
                WindowsNotify.atom_name = None
            self.class_atom = RegisterClass(wc)
            WindowsNotify.atom_name = self.class_atom

            self._create_window()

            self.hicon = self.get_icon(icon)

        def get_icon(self, icon):
            """
            Get icon.

            Try to load the given icon from the path given,
            else default to generic application icon from the OS.
            """

            if WindowsNotify.taskbar_icon is not None:
                DestroyIcon(WindowsNotify.taskbar_icon)
                WindowsNotify.taskbar_icon = None

            icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
            try:
                hicon = LoadImage(
                    self.hinst, icon,
                    win32con.IMAGE_ICON,
                    0, 0, icon_flags
                )
            except Exception:
                hicon = LoadIcon(0, win32con.IDI_APPLICATION)
            WindowsNotify.taskbar_icon = hicon

            return hicon

        def show_notification(self, title, msg, sound, icon, fallback):
            """
            Attemp to show notifications.

            Provide fallback for consistency with other notifyicatin methods.
            """

            try:
                self._show_notification(title, msg, sound, icon)
            except Exception:
                print(traceback.format_exc())
                fallback(title, msg, sound)

        def _create_window(self):
            """Create the Window."""

            style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
            self.hwnd = CreateWindow(
                self.class_atom, "Taskbar", style,
                0, 0, win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT,
                0, 0, self.hinst, None
            )
            WindowsNotify.window_handle = self.hwnd
            UpdateWindow(self.hwnd)

        def _destroy_window(self):
            """Destroy the window."""

            if WindowsNotify.window_handle:
                DestroyWindow(WindowsNotify.window_handle)
                WindowsNotify.window_handle = None
                self.hwnd = None

        def _show_notification(self, title, msg, sound, icon):
            """Call windows API to show notification."""

            icon_level = 0
            if icon & WinNotifyLevel.ICON_INFORMATION:
                icon_level |= NIIF_INFO
            elif icon & WinNotifyLevel.ICON_WARNING:
                icon_level |= NIIF_WARNING
            elif icon & WinNotifyLevel.ICON_ERROR:
                icon_level |= NIIF_ERROR
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
                alert()

        def OnTaskbarNotify(self, hwnd, msg, wparam, lparam):
            """When recieving the dismiss code for the notification, hide the icon."""

            if lparam == 1028:
                self.hide_icon()
                # Noification dismissed

        def show_icon(self):
            """Display the taskbar icon."""

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
            """Hide icon."""

            if self.visible:
                nid = (self.hwnd, 0)
                Shell_NotifyIcon(NIM_DELETE, nid)
            self.visible = False

        def OnDestroy(self, hwnd, msg, wparam, lparam):
            """Remove icon and notification."""

            self.hide_icon()
            PostQuitMessage(0)

    @staticmethod
    def NotifyWin(title, msg, sound, icon, fallback):
        """Notify for windows."""

        Options.instance.show_notification(title, msg, sound, icon, fallback)

except Exception:
    NotifyWin = None
    print("no win notify")


def setup(app_name, icon, *args):
    """Setup."""

    try:
        assert(icon is not None and exists(icon))
    except Exception:
        icon = None

    if NotifyWin is not None:
        Options.instance = WindowsNotify(app_name + "Taskbar", icon, app_name)
        Options.notify = NotifyWin


def get_notify():
    """Get the notification."""

    return Options.notify


Options.notify = notify_win_fallback
