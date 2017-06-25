"""
Notify windows.

Copyright (c) 2013 - 2016 Isaac Muse <isaacmuse@gmail.com>
License: MIT
"""
from __future__ import unicode_literals
import traceback
import winsound
import ctypes
import ctypes.wintypes as wintypes
import os
import platform

__all__ = ("get_notify", "alert", "setup", "windows_icons", "destroy")

if ctypes.sizeof(ctypes.c_long) == ctypes.sizeof(ctypes.c_void_p):
    WPARAM = ctypes.c_ulong
    LPARAM = ctypes.c_long
    LRESULT = ctypes.c_long
elif ctypes.sizeof(ctypes.c_longlong) == ctypes.sizeof(ctypes.c_void_p):
    WPARAM = ctypes.c_ulonglong
    LPARAM = ctypes.c_longlong
    LRESULT = ctypes.c_longlong
HANDLE = ctypes.c_void_p
WNDPROCTYPE = WNDPROC = ctypes.CFUNCTYPE(LRESULT, HANDLE, ctypes.c_uint, WPARAM, LPARAM)

WM_DESTROY = 2
IMAGE_ICON = 1
LR_LOADFROMFILE = 16
LR_DEFAULTSIZE = 64
IDI_APPLICATION = 1
WS_OVERLAPPED = 0
WS_SYSMENU = 524288
CW_USEDEFAULT = -2147483648
WM_USER = 1024

NIM_ADD = 0
NIM_MODIFY = 1
NIM_DELETE = 2
NIF_ICON = 2
NIF_MESSAGE = 1
NIF_TIP = 4
NIIF_INFO = 1
NIIF_WARNING = 2
NIIF_ERROR = 3
NIF_INFO = 16
NIF_SHOWTIP = 0x80


class WndClassEx(ctypes.Structure):
    """WNDCLASSEX structure."""

    _fields_ = [
        ("cbSize", ctypes.c_uint),
        ("style", ctypes.c_uint),
        ("lpfnWndProc", WNDPROCTYPE),
        ("cbClsExtra", ctypes.c_int),
        ("cbWndExtra", ctypes.c_int),
        ("hInstance", HANDLE),
        ("hIcon", HANDLE),
        ("hCursor", HANDLE),
        ("hbrBackground", HANDLE),
        ("lpszMenuName", wintypes.LPCWSTR),
        ("lpszClassName", wintypes.LPCWSTR),
        ("hIconSm", HANDLE)
    ]


class NotifyIconData(ctypes.Structure):
    """NOTIFYICONDATA structure."""

    _fields_ = [
        ("cbSize", ctypes.c_uint),
        ("hWnd", HANDLE),
        ("uID", ctypes.c_uint),
        ("uFlags", ctypes.c_uint),
        ("uCallbackMessage", ctypes.c_uint),
        ("hIcon", HANDLE),
        ("szTip", ctypes.c_wchar * 128),
        ("dwState", ctypes.c_uint),
        ("dwStateMask", ctypes.c_uint),
        ("szInfo", ctypes.c_wchar * 256),
        ("uVersion", ctypes.c_uint),
        ("szInfoTitle", ctypes.c_wchar * 64),
        ("dwInfoFlags", ctypes.c_uint),
        ("guidItem", ctypes.c_char * 16),
        ("hBalloonIcon", HANDLE),
    ]


class NotifyIconDataV3(ctypes.Structure):
    """NOTIFYICONDATA_V3 structure."""

    _fields_ = NotifyIconData._fields_[:-1]  # noqa


class Options(object):
    """Notification options."""

    notify = None
    instance = None

    @classmethod
    def clear(cls):
        """Clear."""

        cls.notify = None
        cls.instance = None


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


class WindowsNotify(object):
    """Windows notification class."""

    window_handle = None
    taskbar_icon = None
    wc = None

    def __init__(self, app_name, icon, tooltip=None):
        """
        Create the taskbar for the application and register it.

        Show nothing by default until called.
        """

        def winproc(hwnd, msg, wparam, lparam):
            """Winproc funciton to handle events."""

            if msg == WM_USER + 20:
                self.OnTaskbarNotify(hwnd, msg, wparam, lparam)
                return 0
            elif msg == WM_DESTROY:
                self.OnDestroy(hwnd, msg, wparam, lparam)
                return 0
            return hwnd

        self.tooltip = tooltip
        self.is_xp = platform.release().lower() == 'xp'
        self.visible = False
        self.app_name = app_name

        # Register window class
        wc = WndClassEx()
        self.hinst = wc.hInstance = ctypes.windll.kernel32.GetModuleHandleW(None)
        wc.cbSize = ctypes.sizeof(wc)
        wc.lpszClassName = ctypes.c_wchar_p(app_name + "Taskbar")
        wc.lpfnWndProc = WNDPROCTYPE(winproc)
        wc.style = 0
        wc.cbClsExtra = 0
        wc.cbWndExtra = 0
        wc.hIcon = 0
        wc.hCursor = 0
        wc.hbrBackground = 0

        if WindowsNotify.wc is not None:
            self._destroy_window()
            ctypes.windll.user32.UnregisterClassW(wc.lpszClassName, None)
            WindowsNotify.wc = wc
        ctypes.windll.user32.RegisterClassExW(ctypes.byref(wc))
        WindowsNotify.wc = wc

        self._create_window(wc.lpszClassName)

        self.hicon = self.get_icon(icon)

    def get_icon(self, icon):
        """
        Get icon.

        Try to load the given icon from the path given,
        else default to generic application icon from the OS.
        """

        if WindowsNotify.taskbar_icon is not None:
            ctypes.windll.user32.DestroyIcon(wintypes.HICON(WindowsNotify.taskbar_icon))
            WindowsNotify.taskbar_icon = None

        icon_flags = LR_LOADFROMFILE | LR_DEFAULTSIZE
        try:
            assert icon is not None
            hicon = ctypes.windll.user32.LoadImageW(
                self.hinst, icon,
                IMAGE_ICON,
                0, 0, icon_flags
            )
        except Exception:
            hicon = ctypes.windll.user32.LoadIconA(0, IDI_APPLICATION)
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

    def _create_window(self, classname):
        """Create the Window."""

        style = WS_OVERLAPPED | WS_SYSMENU
        self.hwnd = ctypes.windll.user32.CreateWindowExW(
            0, classname, classname, style,
            0, 0, CW_USEDEFAULT, CW_USEDEFAULT,
            0, 0, self.hinst, None
        )
        WindowsNotify.window_handle = self.hwnd
        ctypes.windll.user32.UpdateWindow(self.hwnd)

    def _destroy_window(self):
        """Destroy the window."""

        if WindowsNotify.window_handle:
            ctypes.windll.user32.DestroyWindow(WindowsNotify.window_handle)
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

        res = NotifyIconDataV3() if self.is_xp else NotifyIconData()
        res.cbSize = ctypes.sizeof(res)
        res.hWnd = self.hwnd
        res.uID = 0
        res.uFlags = NIF_INFO | NIF_ICON | NIF_MESSAGE | NIF_TIP | NIF_SHOWTIP
        res.uCallbackMessage = WM_USER + 20
        res.hIcon = self.hicon
        res.szTip = self.app_name[:128]
        res.uVersion = 3 if self.is_xp else 4
        res.szInfo = msg[:256]
        res.szInfoTitle = title[:64]
        res.dwInfoFlags = icon_level

        self.show_icon(res)

        if sound:
            alert()

    def OnTaskbarNotify(self, hwnd, msg, wparam, lparam):
        """When recieving the dismiss code for the notification, hide the icon."""

        if lparam == 1028:
            self.hide_icon()

    def show_icon(self, res):
        """Display the taskbar icon."""

        if not ctypes.windll.shell32.Shell_NotifyIconW(NIM_MODIFY, ctypes.byref(res)):
            tres = NotifyIconDataV3() if self.is_xp else NotifyIconData()
            tres.cbSize = ctypes.sizeof(res)
            tres.hWnd = self.hwnd
            tres.uID = 0
            tres.uFlags = NIF_ICON | NIF_MESSAGE | NIF_TIP
            tres.uCallbackMessage = WM_USER + 20
            tres.hIcon = self.hicon
            tres.szTip = self.app_name[:128]
            tres.uVersion = 3 if self.is_xp else 4
            ctypes.windll.shell32.Shell_NotifyIconW(NIM_ADD, ctypes.byref(tres))
            ctypes.windll.shell32.Shell_NotifyIconW(0x4, ctypes.byref(tres))
            ctypes.windll.shell32.Shell_NotifyIconW(NIM_MODIFY, ctypes.byref(res))

        self.visible = True

    def hide_icon(self):
        """Hide icon."""

        if self.visible:
            res = NotifyIconDataV3() if self.is_xp else NotifyIconData()
            res.cbSize = ctypes.sizeof(res)
            res.hWnd = self.hwnd
            res.uID = 0
            res.uFlags = 0
            res.uVersion = 3 if self.is_xp else 4

            ctypes.windll.shell32.Shell_NotifyIconW(NIM_DELETE, ctypes.byref(res))
        self.visible = False

    def OnDestroy(self, hwnd, msg, wparam, lparam):
        """Remove icon and notification."""

        self.hide_icon()

    def destroy(self):

        self.hide_icon()
        self._destroy_window()


@staticmethod
def NotifyWin(title, msg, sound, icon, fallback):
    """Notify for windows."""

    Options.instance.show_notification(title, msg, sound, icon, fallback)


def setup(app_name, icon, *args):
    """Setup."""

    try:
        assert(icon is not None and os.path.exists(icon))
    except Exception:
        icon = None

    Options.instance = WindowsNotify(app_name, icon, app_name)
    Options.notify = NotifyWin


def destroy():
    """Destroy."""

    if Options.instance is not None:
        Options.instance.destroy()

    Options.clear()
    Options.notify = notify_win_fallback


def get_notify():
    """Get the notification."""

    return Options.notify


Options.notify = notify_win_fallback
