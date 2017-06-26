"""Compatibility module."""
from __future__ import unicode_literals
import sys
import functools
import os

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


def to_ustr(obj):
    """Convert to string."""

    if isinstance(obj, ustr):
        return obj
    elif isinstance(obj, bstr):
        return ustr(obj, 'utf-8')
    else:
        return ustr(obj)


def to_bstr(obj):
    """Convert to byte string."""

    assert isinstance(obj, string_type), TypeError
    return obj.encode('utf-8') if isinstance(obj, ustr) else obj


def getcwd():
    """Get the current working directory."""

    if PY3:
        return os.getcwd()
    else:
        return os.getcwdu()


def iternext(item):
    """Iterate to next."""

    if PY3:
        return item.__next__()
    else:
        return item.next()


def translate(lang, text):
    """Translate text."""

    return lang.gettext(text) if PY3 else lang.ugettext(text)
