"""Compatibility module."""
from __future__ import unicode_literals
import sys
import locale
import functools
import os
import copy

PY3 = (3, 0) <= sys.version_info
PY2 = (2, 0) <= sys.version_info < (3, 0)

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
    CommonBrokenPipeError = BrokenPipeError  # noqa F821
else:
    string_type = basestring  # noqa F821
    ustr = unicode  # noqa F821
    bstr = str  # noqa F821

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


def to_unicode_argv():
    """Convert inputs to Unicode."""

    args = copy.copy(sys.argv)

    if PY2:
        if _PLATFORM == "windows":
            # Solution copied from http://stackoverflow.com/a/846931/145400

            from ctypes import POINTER, byref, cdll, c_int, windll
            from ctypes.wintypes import LPCWSTR, LPWSTR

            GetCommandLineW = cdll.kernel32.GetCommandLineW
            GetCommandLineW.argtypes = []
            GetCommandLineW.restype = LPCWSTR

            CommandLineToArgvW = windll.shell32.CommandLineToArgvW
            CommandLineToArgvW.argtypes = [LPCWSTR, POINTER(c_int)]
            CommandLineToArgvW.restype = POINTER(LPWSTR)

            cmd = GetCommandLineW()
            argc = c_int(0)
            argv = CommandLineToArgvW(cmd, byref(argc))
            if argc.value > 0:
                # Remove Python executable and commands if present
                start = argc.value - len(sys.argv)
                args = [argv[i] for i in xrange(start, argc.value)]  # noqa F821
        else:
            cli_encoding = sys.stdin.encoding or locale.getpreferredencoding()
            args = [arg.decode(cli_encoding) for arg in sys.argv if isinstance(arg, bstr)]
    return args


def call(cmd):
    """Call command."""

    # Handle Unicode subprocess paths in Python 2.7 on Windows in shell.
    if _PLATFORM == "windows" and PY2:
        from .win_subprocess import Popen, CreateProcess
        import _subprocess

        # We're going to manually patch this for this instance
        # and then restore afterwards.  I want to limit side effects
        # when using with other modules.
        pre_patched = _subprocess.CreateProcess
        _subprocess.CreateProcess = CreateProcess
    else:
        from subprocess import Popen
    import subprocess

    fail = False

    is_string = isinstance(cmd, string_type)

    try:
        if _PLATFORM == "windows":
            startupinfo = subprocess.STARTUPINFO()
            Popen(
                cmd,
                startupinfo=startupinfo,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE,
                shell=is_string
            )
        else:
            Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE,
                shell=is_string
            )
    except Exception:
        fail = True

    if _PLATFORM == "windows" and PY2:
        # Restore CreateProcess from before our monkey patch
        _subprocess.CreateProcess = pre_patched

    return fail
