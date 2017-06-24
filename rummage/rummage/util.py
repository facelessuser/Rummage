"""Compatibility module."""
from __future__ import unicode_literals
import sys
import functools

PY3 = (3, 0) <= sys.version_info

if sys.platform.startswith('win'):
    _PLATFORM = "windows"
elif sys.platform == "darwin":
    _PLATFORM = "osx"
else:
    _PLATFORM = "linux"

if PY3:
    string_type = str
    ustr = str
    bstr = bytes
    CommonBrokenPipeError = BrokenPipeError  # noqa
else:
    string_type = basestring
    ustr = unicode
    bstr = str

    class CommonBrokenPipeError(Exception):
        """
        Broken Pipe Error.

        Include this for consistency, but we won't actually
        capture this in PY2.
        """


def platform():
    """Get Platform."""

    return _PLATFORM


def sorted_callback(l, sorter):
    """Use a callback with sort in a PY2/PY3 way."""

    if PY3:
        l.sort(key=functools.cmp_to_key(sorter))
    else:
        l.sort(sorter)


def to_ascii_bytes(string):
    """Convert unicode to ascii byte string."""

    return bytes(string, 'ascii') if PY3 else bytes(string)
