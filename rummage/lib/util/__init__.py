"""Compatibility module."""
from __future__ import unicode_literals
import re
import sys
import locale
import functools
import os
import copy
import struct
import codecs
import json
from itertools import groupby
from encodings.aliases import aliases
from .file_strip.json import sanitize_json

MAXUNICODE = sys.maxunicode
NARROW = sys.maxunicode == 0xFFFF

PY3 = (3, 0) <= sys.version_info
PY2 = (2, 0) <= sys.version_info < (3, 0)

if sys.platform.startswith('win'):
    _PLATFORM = "windows"
elif sys.platform == "darwin":
    _PLATFORM = "osx"
else:
    _PLATFORM = "linux"

if PY3:
    from urllib.request import urlopen # noqa F401
    string_type = str
    ustr = str
    bstr = bytes
    unichar = chr

    CommonBrokenPipeError = BrokenPipeError  # noqa F821
else:
    from urllib2 import urlopen # noqa F401
    string_type = basestring  # noqa F821
    ustr = unicode  # noqa F821
    bstr = str  # noqa F821
    unichar = unichr  # noqa F821

    class CommonBrokenPipeError(Exception):
        """
        Broken Pipe Error.

        Include this for consistency, but we won't actually
        capture this in PY2.
        """


BACK_SLASH_TRANSLATION = {
    "\\a": '\a',
    "\\b": '\b',
    "\\f": '\f',
    "\\r": '\r',
    "\\t": '\t',
    "\\n": '\n',
    "\\v": '\v',
    "\\\\": '\\'
}

FMT_BRACKETS = ('{', '}')

if NARROW:
    RE_FMT = re.compile(
        r'''(\\[abfrtnv\\])|(\\u[\da-fA-F]{4}|\\x[\da-fA-F]{2})|(\\[0-7]{1,3})'''
    )
    RE_RE = re.compile(
        r'''(\\[\\])|(\\u[\da-fA-F]{4}|\\x[\da-fA-F]{2})|(\\[0-7]{3})|(\\x[\da-fA-F]{2})'''
    )
else:
    RE_FMT = re.compile(
        r'''(\\[abfrtnv\\])|(\\U[\da-fA-F]{8}|\\u[\da-fA-F]{4}|\\x[\da-fA-F]{2})|(\\[0-7]{1,3})'''
    )
    RE_RE = re.compile(
        r'''(\\[\\])|(\\U[\da-fA-F]{8}|\\u[\da-fA-F]{4}|\\x[\da-fA-F]{2})|(\\[0-7]{3})|(\\x[\da-fA-F]{2})'''
    )


def platform():
    """Get Platform."""

    return _PLATFORM


def uchr(i):
    """Allow getting unicode character on narrow python builds."""

    try:
        return unichar(i)
    except ValueError:  # pragma: no cover
        return struct.pack('i', i).decode('utf-32')


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


def read_json(filename):
    """Read JSON."""

    try:
        with codecs.open(filename, "r", encoding='utf-8') as f:
            content = sanitize_json(f.read(), True)
        obj = json.loads(content)
    except Exception:
        obj = None
    return obj


def write_json(filename, obj):
    """Write JSON."""

    fail = False

    try:
        j = json.dumps(obj, sort_keys=True, indent=4, separators=(',', ': '))
        with codecs.open(filename, 'w', encoding='utf-8') as f:
            f.write(j + "\n")
    except Exception:
        fail = True

    return fail


def numeric_sort(text):
    """Sort numbers in strings as actual numbers."""

    final_text = []
    for digit, g in groupby(text, lambda x: x.isdigit()):
        val = "".join(g)
        if digit:
            final_text.append(int(val))
        else:
            final_text.append(val)

    return final_text


def normalize_encoding_name(original_name):
    """Normalize the encoding names."""

    name = None
    try:
        name = codecs.lookup(original_name).name.upper().replace('_', '-')
    except LookupError:
        if original_name.upper() == 'BIN':
            name = 'BIN'
    return name


def get_encodings():
    """Get list of all encodings."""

    exclude = ('BASE64', 'BZ2', 'HEX', 'QUOPRI', 'ROT-13', 'UU', 'ZLIB')
    elist = set()
    elist.add('BIN')
    for k in aliases.keys():
        value = normalize_encoding_name(k)
        if value is not None and value not in exclude:
            elist.add(value)
    elist = list(elist)
    elist = sorted(elist, key=numeric_sort)
    return elist


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


def preprocess_replace(string, format_replace=False):
    """Process the format string."""

    def replace(m, fmt_repl=format_replace):
        """Replace."""
        if m.group(1):
            if fmt_repl:
                text = BACK_SLASH_TRANSLATION[m.group(1)]
            else:
                text = '\\134'
        else:
            if m.group(2):
                # Unicode (wide and narrow) and bytes
                value = int(m.group(2)[2:], 16)
            elif not format_replace and m.group(4):
                value = int(m.group(4)[2:], 16)
            elif m.group(3):
                # Octal
                value = int(m.group(3)[1:], 8)

            if fmt_repl:
                text = uchr(value)
                if text in FMT_BRACKETS:
                    text = text * 2
            elif value <= 0xff:
                text = '\\%03o' % value
            else:
                text = uchr(value)
        return text

    return (RE_FMT if format_replace else RE_RE).sub(replace, string)


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
