"""Compatibility module."""
import sys

if sys.platform.startswith('win'):
    _PLATFORM = "windows"
elif sys.platform == "darwin":
    _PLATFORM = "macos"
else:
    _PLATFORM = "linux"


def platform():
    """Get Platform."""

    return _PLATFORM
