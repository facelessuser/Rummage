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
import subprocess
from itertools import groupby
from encodings.aliases import aliases
from .file_strip.json import sanitize_json

PY36 = (3, 6) <= sys.version_info
NARROW = sys.maxunicode == 0xFFFF

if sys.platform.startswith('win'):
    _PLATFORM = "windows"
elif sys.platform == "darwin":
    _PLATFORM = "osx"
else:
    _PLATFORM = "linux"

from urllib.request import urlopen # noqa F401
string_type = str
ustr = str
bstr = bytes
unichar = chr


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

RE_SURROGATES = re.compile(r'([\ud800-\udbff])([\udc00-\udfff])')

FMT_BRACKETS = ('{', '}')

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


def char_size(c):
    """Get UTF8 char size."""

    value = ord(c)
    if value <= 0xffff:
        return 1
    elif value <= 0x10ffff:
        return 2
    raise ValueError('Invalid code point')


def ulen(string):
    """Get length of string in bytes."""

    return sum(char_size(c) for c in string)


def sorted_callback(l, sorter):
    """Use a callback with sort in a PY3 way."""

    l.sort(key=functools.cmp_to_key(sorter))


def to_ascii_bytes(string):
    """Convert unicode to ascii byte string."""

    return bytes(string, 'ascii')


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

    if not isinstance(obj, string_type):
        raise TypeError('Must be a string!')
    return obj.encode('utf-8') if isinstance(obj, ustr) else obj


def getcwd():
    """Get the current working directory."""

    return os.getcwd()


def iternext(item):
    """Iterate to next."""

    return item.__next__()


def translate(lang, text):
    """Translate text."""

    return lang.gettext(text)


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

    fail = False

    is_string = isinstance(cmd, string_type)

    try:
        if _PLATFORM == "windows":
            startupinfo = subprocess.STARTUPINFO()
            subprocess.Popen(
                cmd,
                startupinfo=startupinfo,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE,
                shell=is_string
            )
        else:
            subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE,
                shell=is_string
            )
    except Exception:
        fail = True

    return fail
