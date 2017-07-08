"""Platform window focus."""
from __future__ import unicode_literals
import ctypes
import ctypes.util
from ... import util

if util.platform() == "osx":
    appkit = ctypes.cdll.LoadLibrary(ctypes.util.find_library('AppKit'))
    objc = ctypes.cdll.LoadLibrary(ctypes.util.find_library('objc'))

    objc.objc_getClass.restype = ctypes.c_void_p
    objc.sel_registerName.restype = ctypes.c_void_p
    objc.objc_msgSend.restype = ctypes.c_void_p
    objc.objc_msgSend.argtypes = [ctypes.c_void_p, ctypes.c_void_p]


def platform_window_focus(frame):
    """Set focus to the window frame."""

    # General window raising
    if frame.IsIconized():
        frame.Iconize(False)
    if not frame.IsShown():
        frame.Show(True)
    frame.Raise()

    # OSX specific extra to ensure raise
    if util.platform() == "osx":
        try:
            nsapplication = ctypes.c_void_p(objc.objc_getClass('NSApplication'))
            nsapp = ctypes.c_void_p(objc.objc_msgSend(nsapplication, objc.sel_registerName('sharedApplication')))
            objc.objc_msgSend(nsapp, objc.sel_registerName('activateIgnoringOtherApps:'), True)
        except Exception:
            # Failed to bring window to top in OSX
            pass
