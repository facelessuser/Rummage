"""Compatibility module."""
import wx
import re
import sys
import codecs
import platform as plat
from itertools import groupby
from encodings.aliases import aliases

_MAC_VER = (0, 0)

if sys.platform.startswith('win'):
    _PLATFORM = "windows"
elif sys.platform == "darwin":
    _PLATFORM = "macos"
    _MAC_VER = tuple([int(x) for x in plat.mac_ver()[0].split('.')[:2]])
else:
    _PLATFORM = "linux"


WX_420 = wx.__version__ >= '4.2.0'

if WX_420:
    MAC_LIGHT = 1.023
    MAC_DARK = 1.043
else:
    MAC_LIGHT = 0.99
    MAC_DARK = 1.085

# High Sierra and below
MAC_OLD = _MAC_VER < (10, 14)


def mac_ver():
    """Get macOS version."""

    return _MAC_VER


def platform():
    """Get Platform."""

    return _PLATFORM


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

RE_FMT = re.compile(
    r'''(\\[abfrtnv\\])|(\\U[\da-fA-F]{8}|\\u[\da-fA-F]{4}|\\x[\da-fA-F]{2})|(\\[0-7]{1,3})'''
)

RE_RE = re.compile(
    r'''(\\[\\])|(\\U[\da-fA-F]{8}|\\u[\da-fA-F]{4}|\\x[\da-fA-F]{2})|(\\[0-7]{3})'''
)


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
            else:
                # Octal
                value = int(m.group(3)[1:], 8)

            if fmt_repl or value >= 0xff:
                text = chr(value)
            else:
                text = '\\%03o' % value
        return text

    return (RE_FMT if format_replace else RE_RE).sub(replace, string)


def to_ustr(obj):
    """Convert to string."""

    if isinstance(obj, str):
        return obj
    elif isinstance(obj, bytes):
        return str(obj, 'utf-8')
    else:
        return str(obj)
