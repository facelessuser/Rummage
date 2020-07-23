"""
Notify windows.

Copyright (c) 2013 - 2016 Isaac Muse <isaacmuse@gmail.com>
License: MIT
"""
import traceback
import winsound
import ctypes
import ctypes.wintypes as wintypes
import os

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

NIM_ADD = 0x00
NIM_MODIFY = 0x01
NIM_DELETE = 0x02
NIM_SETVERSION = 0x04
NIF_MESSAGE = 0x01
NIF_ICON = 0x02
NIF_TIP = 0x04
NIF_STATE = 0x08
NIF_INFO = 0x10
NIF_REALTIME = 0x40
NIF_SHOWTIP = 0x80
NIIF_INFO = 0x1
NIIF_WARNING = 0x2
NIIF_ERROR = 0x3
NIIF_NOSOUND = 0x10
NIFF_USER = 0x00000004

NIS_HIDDEN = 0x01

HWND_MESSAGE = -3

NIN_BALLOONSHOW = WM_USER + 2
NIN_BALLOONHIDE = WM_USER + 3
NIN_BALLOONTIMEOUT = WM_USER + 4
NIN_BALLOONUSERCLICK = WM_USER + 5


class WndClassEx(ctypes.Structure):
    """The `WNDCLASSEX` structure."""

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
    """The `NOTIFYICONDATA` structure."""

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


class Options:
    """Notification options."""

    notify = None
    instance = None
    sound = None

    @classmethod
    def clear(cls):
        """Clear."""

        cls.notify = None
        cls.instance = None
        cls.sound = None


def _alert(sound=None):
    """Play an alert sound for the OS."""

    if sound is None and Options.sound is not None:
        sound = Options.sound

    try:
        if sound:
            winsound.PlaySound(sound, winsound.SND_FILENAME)
    except Exception:
        pass


def alert():
    """Alert."""

    _alert()


class WinNotifyLevel:
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


class WindowsNotify:
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
            """Handle `winproc` events."""

            if msg == WM_USER + 20 and lparam in (NIN_BALLOONTIMEOUT, NIN_BALLOONUSERCLICK):
                pass
            return hwnd

        self.tooltip = tooltip
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

        self.hicon = self.get_icon(icon)

        self._show_notification('', '', False, 0)

    def get_icon(self, icon):
        """
        Get icon.

        Try to load the given icon from the path given,
        else default to generic application icon from the OS.
        """

        if WindowsNotify.taskbar_icon is not None:
            ctypes.windll.user32.DestroyIcon(wintypes.HICON(WindowsNotify.taskbar_icon))
            WindowsNotify.taskbar_icon = None

        hicon = wintypes.HICON()
        try:
            if icon is None:
                raise ValueError("Icon is not available")
            ctypes.windll.comctl32.LoadIconWithScaleDown(
                None, icon, 48, 48, ctypes.byref(hicon)
            )
        except Exception:
            hicon = ctypes.windll.user32.LoadIconA(0, IDI_APPLICATION)
        WindowsNotify.taskbar_icon = hicon

        return hicon

    def show_notification(self, title, msg, sound, icon, fallback):
        """
        Attempt to show notifications.

        Provide fallback for consistency with other notification methods.
        """

        try:
            self._show_notification(title, msg, sound, icon)
        except Exception:
            print(traceback.format_exc())
            fallback(title, msg, sound)

    def _get_window(self):
        """Create the Window."""

        if WindowsNotify.window_handle:
            hwnd = WindowsNotify.window_handle
        else:
            hwnd = ctypes.windll.user32.FindWindowExW(
                HWND_MESSAGE, None, WindowsNotify.wc.lpszClassName, None
            )
        if not hwnd:
            style = WS_OVERLAPPED | WS_SYSMENU
            hwnd = ctypes.windll.user32.CreateWindowExW(
                0, WindowsNotify.wc.lpszClassName, WindowsNotify.wc.lpszClassName, style,
                0, 0, CW_USEDEFAULT, CW_USEDEFAULT,
                HWND_MESSAGE, 0, self.hinst, None
            )
            if hwnd:
                WindowsNotify.window_handle = hwnd
                ctypes.windll.user32.UpdateWindow(hwnd)
        return hwnd

    def _destroy_window(self):
        """Destroy the window."""

        if WindowsNotify.window_handle:
            if self.visible:
                res = NotifyIconData()
                res.cbSize = ctypes.sizeof(res)
                res.hWnd = WindowsNotify.window_handle
                res.uID = 0
                res.uFlags = 0
                res.uVersion = 4

                ctypes.windll.shell32.Shell_NotifyIconW(NIM_DELETE, ctypes.byref(res))
                ctypes.windll.user32.UpdateWindow(WindowsNotify.window_handle)
            self.visible = False

            ctypes.windll.user32.DestroyWindow(WindowsNotify.window_handle)
            WindowsNotify.window_handle = None

    def _show_notification(self, title, msg, sound, icon):
        """Call windows API to show notification."""

        icon_level = 0
        if icon & WinNotifyLevel.ICON_INFORMATION:
            icon_level |= NIIF_INFO
        elif icon & WinNotifyLevel.ICON_WARNING:
            icon_level |= NIIF_WARNING
        elif icon & WinNotifyLevel.ICON_ERROR:
            icon_level |= NIIF_ERROR

        hwnd = self._get_window()

        if hwnd:
            res = NotifyIconData()
            res.cbSize = ctypes.sizeof(res)
            res.hWnd = hwnd
            res.uID = 0
            # `NIF_SHOWTIP` and `NIF_TIP` is probably not needed for Windows 8+, but maybe for 7?
            res.uFlags = NIF_INFO | NIF_ICON | NIF_STATE | NIF_SHOWTIP | NIF_TIP | NIF_MESSAGE
            res.uCallbackMessage = WM_USER + 20
            res.hIcon = self.hicon
            res.szTip = self.app_name[:128]
            res.uVersion = 4
            res.szInfo = msg[:256]
            res.szInfoTitle = title[:64]
            res.dwInfoFlags = icon_level | NIIF_NOSOUND | NIFF_USER

            if not ctypes.windll.shell32.Shell_NotifyIconW(NIM_MODIFY, ctypes.byref(res)):
                if not self.visible and WindowsNotify.window_handle:
                    ctypes.windll.shell32.Shell_NotifyIconW(NIM_ADD, ctypes.byref(res))
                    ctypes.windll.shell32.Shell_NotifyIconW(NIM_SETVERSION, ctypes.byref(res))
                self.visible = WindowsNotify.window_handle is not None

            if sound:
                alert()

    def destroy(self):
        """Destroy."""

        self._destroy_window()


@staticmethod
def NotifyWin(title, msg, sound, icon, fallback):
    """Notify for windows."""

    Options.instance.show_notification(title, msg, sound, icon, fallback)


def setup(app_name, icon, **kwargs):
    """Setup."""

    sound = kwargs.get('sound')
    if sound is not None and os.path.exists(sound):
        Options.sound = sound

    try:
        if icon is None or not os.path.exists(icon):
            raise ValueError("Icon does not appear to be valid")
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
