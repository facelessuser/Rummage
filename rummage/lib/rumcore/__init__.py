# -*- coding: utf-8 -*-
"""
RumCore.

Licensed under MIT
Copyright (c) 2013 - 2015 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.
"""
from __future__ import unicode_literals
import sys
import codecs
import mmap
import os
import re
import shutil
import sre_parse
import unicodedata
import backrefs
from collections import namedtuple
from time import ctime
from backrefs import bre
from collections import deque
from . import text_decode
from .file_times import getmtime, getctime
from .file_hidden import is_hidden
from .. import util
try:
    from backrefs import bregex
    import regex
    REGEX_SUPPORT = True
except ImportError:  # pragma: no cover
    REGEX_SUPPORT = False

# Common regex flags (re|regex)
IGNORECASE = 0x1  # (?i)
DOTALL = 0x2      # (?s)
MULTILINE = 0x4   # (?m)
UNICODE = 0x8     # (?u)

# Regex module flags
ASCII = 0x10            # (?a)
FULLCASE = 0x20         # (?f)
WORD = 0x40             # (?w)
BESTMATCH = 0x80        # (?b)
ENHANCEMATCH = 0x100    # (?e)
REVERSE = 0x200         # (?r)
VERSION0 = 0x400        # (?V0)
VERSION1 = 0x800        # (?V1)
FORMATREPLACE = 0x1000  # Use {1} for groups in replace
POSIX = 0x2000          # (?p)

# Rumcore search related flags
LITERAL = 0x10000           # Literal search

# Rumcore related flags
BUFFER_INPUT = 0x20000      # Input is a buffer
RECURSIVE = 0x40000         # Recursive directory search
FILE_REGEX_MATCH = 0x80000  # Regex pattern for files
DIR_REGEX_MATCH = 0x100000  # Regex pattern for directories
SHOW_HIDDEN = 0x200000      # Show hidden files and folders
COUNT_ONLY = 0x400000       # Only count the matches; no context
BOOLEAN = 0x800000          # Just check if file has one match and move on
PROCESS_BINARY = 0x1000000  # Process binary files
TRUNCATE_LINES = 0x2000000  # Truncate context lines to 120 chars
BACKUP = 0x4000000          # Backup files on replace
BACKUP_FOLDER = 0x8000000   # Backup to folder

RE_MODE = 0
BRE_MODE = 1
REGEX_MODE = 2
BREGEX_MODE = 3

SEARCH_MASK = 0x1FFFF
FILE_MASK = 0xFFE0000

RE_MODES = (RE_MODE, BRE_MODE)
REGEX_MODES = (REGEX_MODE, BREGEX_MODE)
FORMAT_MODES = (REGEX_MODE, BREGEX_MODE, BRE_MODE)

TRUNCATE_LENGTH = 120

DEFAULT_BAK = 'rum-bak'
DEFAULT_FOLDER_BAK = '.rum-bak'

_OCTAL = frozenset(('0', '1', '2', '3', '4', '5', '6', '7'))
_STANDARD_ESCAPES = frozenset(('a', 'b', 'f', 'n', 'r', 't', 'v', '\\'))
_CHAR_ESCAPES = frozenset(('u', 'U', 'x'))
_SET_OPERATORS = frozenset(('&', '~', '|'))
_WILDCARD_CHARS = frozenset(('-', '[', ']', '*', '?', '|'))

_U32 = frozenset(('u32', 'utf32', 'utf_32'))
_U32BE = frozenset(('utf-32be', 'utf_32_be'))
_U32LE = frozenset(('utf-32le', 'utf_32_le'))
_U16 = frozenset(('u16', 'utf16', 'utf_16'))
_U16BE = frozenset(('utf-16be', 'utf_16_be'))
_U16LE = frozenset(('utf-16le', 'utf_16_le'))
_U8 = frozenset(('u8', 'utf', 'utf8', 'utf_8', 'utf_8_sig', 'utf-8-sig'))

RE_LINE_ENDINGS = re.compile(r'(?:\r\n|\r|\n)')


def get_exception():
    """Capture exception and traceback separately."""

    import traceback

    # capture the exception before doing anything else
    exc_type, exc_value, exc_tb = sys.exc_info()

    try:
        exc = ''.join(traceback.format_exception_only(exc_type, exc_value))
        tb = ''.join(traceback.format_tb(exc_tb))
    finally:
        # Prevent circular reference.
        del exc_tb

    return (exc, tb)


def _re_pattern(pattern, rum_flags=0, binary=False):
    """Prepare regex search pattern flags."""

    flags = 0
    if rum_flags & MULTILINE:
        flags |= re.MULTILINE
    if rum_flags & IGNORECASE:
        flags |= re.IGNORECASE
    if rum_flags & DOTALL:
        flags |= re.DOTALL
    if not binary and rum_flags & UNICODE:
        flags |= re.UNICODE
    else:
        flags |= re.ASCII
    return re.compile(pattern, flags)


def _bre_pattern(pattern, rum_flags=0, binary=False):
    """Prepare regex search pattern flags."""

    flags = 0
    if rum_flags & MULTILINE:
        flags |= bre.MULTILINE
    if rum_flags & IGNORECASE:
        flags |= bre.IGNORECASE
    if rum_flags & DOTALL:
        flags |= bre.DOTALL
    if not binary and rum_flags & UNICODE:
        flags |= bre.UNICODE
    else:
        flags |= bre.ASCII
    return bre.compile(pattern, flags)


def _re_literal_pattern(pattern, rum_flags=0, binary=False):
    """Prepare literal search pattern flags."""

    flags = 0
    if rum_flags & IGNORECASE:
        flags |= re.IGNORECASE
    if not binary and rum_flags & UNICODE:
        flags |= re.UNICODE
    else:
        flags |= re.ASCII
    return re.compile(re.escape(pattern), flags)


if REGEX_SUPPORT:
    def _regex_pattern(pattern, rum_flags=0, binary=False):
        """Prepare regex search pattern flags for regex module."""

        flags = 0

        if rum_flags & VERSION1:
            flags |= regex.VERSION1
        else:
            flags |= regex.VERSION0
            if rum_flags & FULLCASE:
                flags |= regex.FULLCASE
        if rum_flags & WORD:
            flags |= regex.WORD
        if rum_flags & BESTMATCH:
            flags |= regex.BESTMATCH
        if rum_flags & ENHANCEMATCH:
            flags |= regex.ENHANCEMATCH
        if rum_flags & REVERSE:
            flags |= regex.REVERSE
        if rum_flags & MULTILINE:
            flags |= regex.MULTILINE
        if rum_flags & IGNORECASE:
            flags |= regex.IGNORECASE
        if rum_flags & DOTALL:
            flags |= regex.DOTALL
        if rum_flags & POSIX:
            flags |= regex.POSIX
        if not binary and rum_flags & UNICODE:
            flags |= regex.UNICODE
        else:
            flags |= regex.ASCII
        return regex.compile(pattern, flags)

    def _bregex_pattern(pattern, rum_flags=0, binary=False):
        """Prepare regex search pattern flags for regex module."""

        flags = 0

        if rum_flags & VERSION1:
            flags |= bregex.VERSION1
        else:
            flags |= bregex.VERSION0
            if rum_flags & FULLCASE:
                flags |= bregex.FULLCASE

        if rum_flags & WORD:
            flags |= bregex.WORD
        if rum_flags & BESTMATCH:
            flags |= bregex.BESTMATCH
        if rum_flags & ENHANCEMATCH:
            flags |= bregex.ENHANCEMATCH
        if rum_flags & REVERSE:
            flags |= bregex.REVERSE
        if rum_flags & MULTILINE:
            flags |= bregex.MULTILINE
        if rum_flags & IGNORECASE:
            flags |= bregex.IGNORECASE
        if rum_flags & DOTALL:
            flags |= bregex.DOTALL
        if rum_flags & POSIX:
            flags |= bregex.POSIX
        if not binary and rum_flags & UNICODE:
            flags |= bregex.UNICODE
        else:
            flags |= bregex.ASCII
        return bregex.compile(pattern, flags)

    def _regex_literal_pattern(pattern, rum_flags=0, binary=False):
        """Prepare literal search pattern flags."""

        flags = 0
        if rum_flags & VERSION1:
            flags |= regex.VERSION1
        else:
            flags |= regex.VERSION0
            if rum_flags & FULLCASE:
                flags |= regex.FULLCASE

        if not binary and rum_flags & UNICODE:
            flags |= regex.UNICODE
        else:
            flags |= regex.ASCII

        if rum_flags & IGNORECASE:
            flags |= regex.IGNORECASE
        return regex.compile(regex.escape(pattern), flags)


class RummageException(Exception):
    """Rummage exception."""


class RummageTestException(Exception):
    """Rummage exception."""


class FileAttrRecord(namedtuple('FileAttrRecord', ['name', 'ext', 'size', 'modified', 'created', 'skipped', 'error'])):
    """File Attributes."""


class FileInfoRecord(namedtuple('FileInfoRecord', ['id', 'name', 'ext', 'size', 'modified', 'created', 'encoding'])):
    """A record for tracking file info."""


class FileRecord(namedtuple('FileRecord', ['info', 'match', 'error'])):
    """A record that reports file info, matching status, and errors."""


class MatchRecord(namedtuple('MatchRecord', ['lineno', 'colno', 'match', 'lines', 'context'])):
    """A record that contains match info, lineno content, context, etc."""


class BufferRecord(namedtuple('BufferRecord', ['content', 'error'])):
    """A record with the string buffer replacements."""


class ErrorRecord(namedtuple('ErrorRecord', ['error'])):
    """A record for non-file related errors."""


class _StringIter(object):
    """Preprocess replace tokens."""

    def __init__(self, string):
        """Initialize."""

        self._string = string
        self._index = 0

    def __iter__(self):
        """Iterate."""

        return self

    def __next__(self):
        """Python 3 iterator compatible next."""

        return self.iternext()

    @property
    def index(self):
        """Get current index."""

        return self._index

    def previous(self):
        """Get previous char."""

        return self._string[self._index - 1]

    def rewind(self, count):
        """Rewind index."""

        if count > self._index:  # pragma: no cover
            raise ValueError("Can't rewind past beginning!")

        self._index -= count

    def iternext(self):
        """Iterate through characters of the string."""

        try:
            char = self._string[self._index]
            self._index += 1
        except IndexError:  # pragma: no cover
            raise StopIteration

        return char


class Wildcard2Regex(object):
    """Translate fnmatch pattern to regex."""

    def __init__(self, pattern, regex_mode=RE_MODE, case_sensitive=False):
        """Initialize."""

        self.pattern = pattern
        if (
            (regex_mode in REGEX_MODES and not REGEX_SUPPORT) or
            (RE_MODE > regex_mode > BREGEX_MODE)
        ):  # pragma: no cover
            regex_mode = RE_MODE
        self.is_regex = regex_mode in REGEX_MODES
        if self.is_regex:  # pragma: no cover
            self.engine = regex
        else:
            self.engine = re

        self.flags = 0
        if regex_mode:  # pragma: no cover
            self.flags |= self.engine.V0
        if not case_sensitive:
            self.flags |= self.engine.I

    def _sequence(self, i):
        """Handle fnmatch character group."""

        result = ['[']

        c = next(i)
        if c == '!':
            # Handle negate char
            result.append('^')
            c = next(i)
        if c == '^':
            # Escape regular expression negate character
            result.append('\\' + c)
            c = next(i)
        if c in ('-', '['):
            # Escape opening bracket or hyphen
            result.append('\\' + c)
            c = next(i)
        elif c == ']':
            # Handle closing as first character
            result.append(c)
            c = next(i)

        end_stored = False
        escape_hypen = -1
        while c != ']':
            if c == '-':
                if i.index - 1 > escape_hypen:
                    # Found a range delimiter.
                    # Mark the next two characters as needing to be escaped if hypens.
                    # The next character would be the end char range (s-e),
                    # and the one after that would be the potential start char range
                    # of a new range (s-es-e), so neither can be legitimate range delimiters.
                    result.append(c)
                    escape_hypen = i.index + 1
                else:
                    result.append('\\' + c)
            elif c == '\\':
                # Handle escapes
                subindex = i.index
                try:
                    result.append(self._references(i))
                    if i.previous() == ']':
                        end_stored = True
                        break
                except StopIteration:
                    i.rewind(i.index - subindex)
                    result.append('\\\\')
            elif c in _SET_OPERATORS:
                # Escape &, |, and ~ to avoid &&, ||, and ~~
                result.append('\\' + c)
            else:
                # Anything else
                result.append(c)
            c = next(i)

        if not end_stored:
            result.append(']')

        return ''.join(result)

    def _references(self, i):
        """Handle references."""

        index = i.index
        value = ''
        c = next(i)
        if c in 'N':
            # \N{name}
            try:
                c = next(i)
                if c != '{':
                    raise SyntaxError("Missing '{' in named Unicode character format at position %d!" % (i.index - 1))
                name = []
                c = next(i)
                while c != '}':
                    name.append(c)
                    c = next(i)
            except StopIteration:
                raise SyntaxError('Incomplete named Unicode character at position %d!' % (index - 1))
            nval = ord(unicodedata.lookup(''.join(name)))
            value = '\\%03o' % nval if nval <= 0xFF else backrefs.util.uchr(nval)
        elif c in _OCTAL:
            # \octal
            digit = [c]
            try:
                for x in range(2):
                    c = next(i)
                    if c in _OCTAL:
                        digit.append(c)
                    else:
                        i.rewind(1)
                        break
            except StopIteration:
                pass
            digit = int(''.join(digit), 8)
            if digit <= 0xFF:
                value = '\\%03o' % digit
            else:
                value = backrefs.util.uchr(digit)
        elif c in _STANDARD_ESCAPES or c in _CHAR_ESCAPES:
            # \n, \v, etc. and \u, \U, \x etc.
            value = '\\' + c
        elif c in _SET_OPERATORS or c in _WILDCARD_CHARS:
            value = '\\\\'
            i.rewind(1)
        else:
            # Anything else
            value = '\\\\' + c
        return value

    def translate(self):
        """Translate fnmatch pattern counting `|` as a separator and `-` as a negative pattern."""

        result = []
        exclude_result = []

        if self.pattern[0] == '-':
            current = exclude_result
            pattern = self.pattern[1:]
            current.append('')
        else:
            current = result
            pattern = self.pattern
            current.append('')

        i = _StringIter(pattern)
        iter(i)
        for c in i:
            if c == '*':
                current.append('.*')
            elif c == '?':
                current.append('.')
            elif c == '|':
                try:
                    c = next(i)
                    if c == '-':
                        current = exclude_result
                    else:
                        current = result
                        i.rewind(1)
                except StopIteration:
                    # No need to append | as we are at the end.
                    current = result
                # Only append if we've already started the pattern
                # This is to avoid adding a leading | to something
                # like the exclude pattern on transition from normal
                # to exclude pattern.
                if current:
                    current.append('|')
            elif c == '\\':
                index = i.index
                try:
                    current.append(self._references(i))
                except StopIteration:
                    i.rewind(i.index - index)
                    current.append('\\\\')
            elif c == '[':
                index = i.index
                try:
                    current.append(self._sequence(i))
                except StopIteration:
                    i.rewind(i.index - index)
                    current.append('\\[')
            else:
                current.append(self.engine.escape(c))
        if not result:
            result.append('.*')
        if util.PY36 or self.is_regex:
            pattern = r'(?s:%s)\Z' % ''.join(result)
            exclude_pattern = r'(?s:%s)\Z' % ''.join(exclude_result)
        else:
            pattern = r'(?ms)(?:%s)\Z' % ''.join(result)
            exclude_pattern = r'(?ms)(?:%s)\Z' % ''.join(exclude_result)

        return self.engine.compile(pattern, self.flags), self.engine.compile(exclude_pattern, self.flags)


class Search(object):
    """Search setup object."""

    def __init__(self, replace=False):
        """Setup search object as as a search only or search and replace object."""

        self._entry = []
        self._is_replace = replace

    def add(self, search, replace=None, flags=0):
        """Add search entry."""

        self._entry.append(
            (
                search,
                ("" if replace is None else replace),
                flags & SEARCH_MASK
            )
        )

    def __string__(self):
        """To string."""

        return str(self._entry)

    def is_replace(self):
        """Is this a replace object."""

        return self._is_replace

    def __getitem__(self, index):
        """Get entry item."""

        return self._entry[index]

    def __len__(self):
        """Get length."""

        return len(self._entry)


class ReplacePlugin(object):
    """Rummage replace plugin."""

    def __init__(self, file_info, flags):
        """Initialize."""

        self.file_info = file_info
        self.flags = flags
        self.on_init()

    def _test(self, m):  # pragma: no cover
        """
        Used for testing and capturing the exception.

        Needs to raise the RummageTestException.
        This should not be touched by the user.
        """

        try:
            return self.replace(m)
        except Exception:
            import traceback
            raise RummageTestException(str(traceback.format_exc()))

    def on_init(self):
        """Override this function to add initialization setup."""

    def get_flags(self):
        """Get flags."""

        return self.flags

    def get_file_name(self):
        """Get file name."""

        return self.file_info.name

    def is_binary(self):
        """Is a binary search."""

        return self.file_info.encoding.encode == 'bin'

    def is_literal(self):
        """Is a literal search."""

        return self.flags & LITERAL

    def replace(self, m):
        """Make replacement."""

        return m.group(0)


class _RummageFileContent(object):
    """Either return a string or memory map file object."""

    def __init__(self, name, size, encoding, file_content=None):
        """Initialize."""
        self.name = name
        self.size = size
        self.encoding = encoding
        self.file_obj = None
        self.string_buffer = file_content
        self.file_map = None

    def __enter__(self):
        """Return content of either a memory map file or string."""

        return self.string_buffer if self.string_buffer else self._read_file()

    def __exit__(self, *args):
        """Close file obj and memory map object if open."""

        if self.file_map is not None:
            self.file_map.close()
        if self.file_obj is not None:
            self.file_obj.close()

    def _get_encoding(self):
        """Get the encoding."""

        enc = self.encoding.encode
        if enc == 'utf-8':
            enc = 'utf-8-sig'
        elif enc.startswith('utf-16'):
            enc = 'utf-16'
        elif enc.startswith('utf-32'):
            enc = 'utf-32'
        return enc

    def _read_bin(self):
        """Setup binary file reading with mmap."""
        try:
            self.file_obj = open(self.name, "rb")
            if self.size != 0:
                self.file_map = mmap.mmap(self.file_obj.fileno(), 0, access=mmap.ACCESS_READ)
        except Exception:
            # _read_bin has no other fallbacks, so we issue this if it fails.
            raise RummageException("Could not access or read file.")

    def _read_file(self):
        """Read the file in."""

        try:
            if self.encoding.encode == "bin":
                self._read_bin()
            else:
                enc = self._get_encoding()
                self.file_obj = codecs.open(self.name, 'r', encoding=enc)
            return self.file_obj.read() if self.file_map is None else self.file_map
        except RummageException:
            # Bubble up RummageExceptions
            raise
        except Exception:
            if self.encoding.encode != "bin":
                if self.file_obj is not None:
                    self.file_obj.close()
                self.encoding = text_decode.Encoding("bin", None)
                self._read_bin()
                return self.file_map


class _FileSearch(object):
    """Search for files."""

    hex_tx_table = ("\ufffd" * 32) + "".join(chr(c) for c in range(32, 127)) + ("\ufffd" * 129)

    def __init__(
        self, search_obj, file_obj, file_id, flags, context, encoding,
        backup_location, max_count, file_content=None, regex_mode=RE_MODE,
        encoding_options=None
    ):
        """Init the file search object."""

        self.abort = False
        self.encoding_options = encoding_options
        self.search_obj = search_obj
        if (regex_mode in REGEX_MODES and not REGEX_SUPPORT) or (RE_MODE > regex_mode > BREGEX_MODE):
            regex_mode = RE_MODE
        self.regex_mode = regex_mode
        self.flags = flags
        self.boolean = bool(self.flags & BOOLEAN)
        self.count_only = bool(self.flags & COUNT_ONLY)
        self.truncate_lines = bool(self.flags & TRUNCATE_LINES)
        self.process_binary = bool(self.flags & PROCESS_BINARY)
        self.reverse = False
        self.backup = bool(self.flags & BACKUP)
        self.backup2folder = bool(self.flags & BACKUP_FOLDER)
        self.backup_ext = ('.%s' % backup_location) if not self.backup2folder else DEFAULT_BAK
        self.backup_folder = backup_location if self.backup2folder else DEFAULT_FOLDER_BAK
        self.bom = None
        self.context = (0, 0) if self.truncate_lines else context

        # Prepare search
        self.expand = None
        self.literal = False
        self.idx = file_id
        self.file_obj = file_obj
        self.max_count = max_count
        self.encoding = encoding if encoding is not None else None
        self.file_content = file_content
        self.is_binary = False
        self.current_encoding = None
        self.is_unicode_buffer = self.file_content is not None and isinstance(self.file_content, str)

    def _get_binary_context(self, content, m):
        """Get context info for binary file."""

        row = 1
        col = 1
        before = 0
        after = 0
        start = m.start()
        end = m.end()
        eof = len(content) - 1

        match_len = m.end() - m.start()
        overage = (TRUNCATE_LENGTH - match_len) / 2
        if overage > 0:
            start = m.start() - overage
            end = m.end() + overage
        if start < 0:
            start = 0
        if end > eof:
            end = eof

        match_start = m.start() - start
        match_end = match_start + m.end() - m.start()

        if self.truncate_lines:
            length = end - start
            if length > TRUNCATE_LENGTH:
                end = start + TRUNCATE_LENGTH
                length = TRUNCATE_LENGTH

            # Recalculate relative match start and end
            if match_start > length:
                match_start = length
            if match_end > length:
                match_end = TRUNCATE_LENGTH

        return (
            content[int(start):int(end)].decode('ascii', errors='replace').translate(self.hex_tx_table),
            (match_start, match_end),
            (before, after),
            row,
            col
        )

    def _get_line_endings_to_point(self, point):
        """Get line ending up to the given point."""
        try:
            while point > self.last_line:
                lend = next(self.line_iter)
                self.line_map.append(lend.end() - 1)
                self.last_line = lend.end()
        except StopIteration:
            self.last_line = point
            pass

    def _get_line_endings_count(self, count):
        """Get line ending up to the given point."""
        try:
            found = 0
            for x in range(count):
                lend = next(self.line_iter)
                self.line_map.append(lend.end() - 1)
                self.last_line = lend.end()
                found += 1
        except StopIteration:
            pass
        return found

    def _get_line_context(self, content, m):
        """Get context info about the line."""

        win_end = '\r\n'

        before, after = self.context
        self._get_line_endings_to_point(m.start())
        row = self._get_row(m.start())
        col = m.start() + 1
        idx = row - 1
        lines = len(self.line_map) - 1
        start = 0
        end = len(content)

        # 1 index back gives us the start of this line
        # 2 gives us the start of the next
        start_idx = idx - before - 1
        end_idx = idx + after

        # On buffer boundary we may not be able to get
        # all of a files requested lines, as we will be beyond
        # map's index.  Set index to None, as it is invalid,
        # and recalculate actual before.
        if start_idx < 0:
            before -= start_idx + 1
            start_idx = None

        # Extended beyond map's end
        if lines < end_idx:
            lines += self._get_line_endings_count(end_idx - lines)
            if lines < end_idx:
                after -= end_idx - lines
                end_idx = None

        # Calculate column of cursor and actual start and end of context
        if lines != -1:
            col_start = idx - 1
            col = m.start() - self.line_map[col_start] if col_start >= 0 else m.start() + 1
            # \r\n combinations usually show up as one char in editors and displays.
            # Decrement the column if we are at a line's end with one of these.
            # We will verify any line to account for mixed line endings.
            if (
                self.line_map and idx < len(self.line_map) and m.start() == self.line_map[idx] and
                m.start() != 0 and content[m.start() - 1: m.start() + 1] == win_end
            ):
                col -= 1

            if start_idx is not None:
                start = self.line_map[start_idx] + 1
            if end_idx is not None:
                end = self.line_map[end_idx]

        # Make the match start and match end relative to the context snippet
        match_start = m.start() - start
        match_end = match_start + m.end() - m.start()

        # Truncate long lines if desired
        if self.truncate_lines:
            length = end - start
            if length > TRUNCATE_LENGTH:
                end = start + TRUNCATE_LENGTH
                length = TRUNCATE_LENGTH

            # Recalculate relative match start and end
            if match_start > length:
                match_start = length
            if match_end > length:
                match_end = TRUNCATE_LENGTH

        # Return the context snippet, where the match occurs,
        # and how many lines of context before and after,
        # and the row and colum of match start.
        return (
            content[start:end],
            (match_start, match_end),
            (before, after),
            row,
            col
        )

    def _get_row(self, start):
        """Get line number where result is found in file."""

        # Binary Search
        mn = 0
        mx = len(self.line_map) - 1
        if mx == -1 or start <= self.line_map[mn]:
            return mn + 1

        if start > self.line_map[-1]:
            return mx + 2

        while mx - mn != 1:
            idx = mn + ((mx - mn) >> 1)
            if start > self.line_map[idx]:
                mn = idx
            else:
                mx = idx

        return mx + 1

    def expand_match(self, m):
        """Expand the match."""

        if self.is_plugin_replace:
            return self.current_replace.replace(m)
        elif self.literal:
            return self.current_replace
        elif self.expand:
            return self.expand(m)
        elif self.regex_format_replace:
            return m.expandf(self.current_replace)
        else:
            return m.expand(self.current_replace)

    def _findall(self, file_content, search_pattern, replace_pattern, flags, file_info):
        """Find all occurences of search pattern in file."""

        replace = None
        pattern = None

        if (
            replace_pattern is not None and
            not isinstance(replace_pattern, (str, bytes))
        ):
            replace_pattern = replace_pattern(file_info, flags)
            self.is_plugin_replace = True
        else:
            self.is_plugin_replace = False

        self.regex_format_replace = self.regex_mode in FORMAT_MODES and bool(flags & FORMATREPLACE)

        if self.is_binary:
            try:
                pattern = bytes(search_pattern, 'ascii')
            except UnicodeEncodeError:
                raise RummageException('Unicode chars in binary search pattern')
            if replace_pattern is not None and not self.is_plugin_replace:
                try:
                    replace = bytes(replace_pattern, 'ascii')
                except UnicodeEncodeError:
                    raise RummageException('Unicode chars in binary replace pattern')
        else:
            pattern = search_pattern
            replace = replace_pattern

        self.current_replace = replace

        if pattern is not None:
            if bool(flags & LITERAL):
                self.literal = True
                if self.regex_mode in REGEX_MODES:
                    pattern = _regex_literal_pattern(pattern, flags, self.is_binary)
                else:
                    pattern = _re_literal_pattern(pattern, flags, self.is_binary)
            else:
                if self.regex_mode == BREGEX_MODE:
                    pattern = _bregex_pattern(pattern, flags, self.is_binary)
                    if replace is not None and not self.is_plugin_replace:
                        self.expand = pattern.compile(replace, (bregex.FORMAT if bool(flags & FORMATREPLACE) else 0))
                elif self.regex_mode == REGEX_MODE:
                    pattern = _regex_pattern(pattern, flags, self.is_binary)
                elif self.regex_mode == BRE_MODE:
                    pattern = _bre_pattern(pattern, flags, self.is_binary)
                    if replace is not None and not self.is_plugin_replace:
                        self.expand = pattern.compile(replace, (bre.FORMAT if bool(flags & FORMATREPLACE) else 0))
                else:
                    pattern = _re_pattern(pattern, flags, self.is_binary)
                    if replace is not None and not self.is_plugin_replace:
                        template = sre_parse.parse_template(replace, pattern)
                        self.expand = lambda m, t=template: sre_parse.expand_template(t, m)

            if REGEX_SUPPORT and isinstance(pattern, (bregex._REGEX_TYPE, bregex.Bregex)):
                self.reverse = bool(pattern.flags & regex.REVERSE)
            else:
                self.reverse = False

            self.text_offset = len(file_content) if self.reverse else 0

            for m in pattern.finditer(file_content):
                yield m

    def _update_buffer(self, content):
        """Update the buffer content."""

        return BufferRecord((b'' if self.is_binary else '').join(content), None)

    def _update_file(self, file_name, content):
        """Update the file content."""

        encoding = self.current_encoding
        if self.backup:
            if self.backup2folder:
                dirname = os.path.join(os.path.dirname(file_name), self.backup_folder)
                basename = os.path.basename(file_name)
                backup = os.path.join(dirname, basename)
                if not os.path.exists(dirname):
                    os.makedirs(dirname)
                shutil.copy2(file_name, backup + '.bak')
            else:
                backup = file_name + self.backup_ext
                shutil.copy2(file_name, backup)

        if encoding.bom:
            # Write the bom first, then write in utf format out in the specified order.
            with open(file_name, 'wb') as f:
                f.write(encoding.bom)
            with codecs.open(file_name, 'a', encoding=encoding.encode) as f:
                while content:
                    f.write(content.popleft())
        elif encoding.encode == 'bin':
            # Write bin file.
            with open(file_name, 'wb') as f:
                while content:
                    f.write(content.popleft())
        else:
            # If a user is adding unicode to ascii,
            # we write ascii files out as utf-8 to keep it from failing.
            # We choose utf-8 because it is compatible with ASCII,
            # but we could just as easily have choosen Latin-1 or CP1252.
            enc = encoding.encode
            with codecs.open(file_name, 'w', encoding=('utf-8' if enc == 'ascii' else enc)) as f:
                while content:
                    f.write(content.popleft())

    def _get_file_info(self, file_obj):
        """Create file info record."""

        error = None
        file_info = None
        string_buffer = self.file_content is not None

        try:
            self.current_encoding = text_decode.Encoding('bin', None)
            self.is_binary = False
            if string_buffer:
                self.current_encoding = text_decode.Encoding('unicode' if self.is_unicode_buffer else 'bin', None)
                self.is_binary = not self.is_unicode_buffer
            elif self.encoding is not None:
                if self.encoding == 'bin':
                    self.current_encoding = text_decode.Encoding('bin', None)
                    self.is_binary = True
                elif self.encoding.startswith(('utf-8', 'utf-16', 'utf-32')):
                    bom = text_decode.inspect_bom(file_obj.name)
                    if bom and bom.encode.startswith(self.encoding):
                        self.current_encoding = bom
                    else:
                        self.current_encoding = text_decode.Encoding(self.encoding, None)
                else:
                    self.current_encoding = text_decode.Encoding(self.encoding, None)
            else:
                # Guess encoding and decode file
                encoding = text_decode.guess(
                    file_obj.name, verify=False, encoding_options=self.encoding_options
                )
                if encoding is not None:
                    if encoding.encode == "bin":
                        self.is_binary = True
                    self.current_encoding = encoding
        except Exception:
            error = get_exception()

        file_info = FileInfoRecord(
            self.idx,
            file_obj.name,
            os.path.splitext(file_obj.name)[1].lower().lstrip('.'),
            file_obj.size,
            file_obj.modified,
            file_obj.created,
            self.current_encoding.encode.upper()
        )

        return file_info, error

    def kill(self):
        """Kill process."""

        self.abort = True

    def search_and_replace(self):
        """Search and replace."""

        text = deque()
        is_buffer = True if self.file_content else False

        file_info, error = self._get_file_info(self.file_obj)

        if error is not None:
            if is_buffer:
                yield BufferRecord(None, error)
            else:
                yield FileRecord(file_info, None, error)
        elif not self.is_binary or self.process_binary:

            try:
                file_record_sent = False

                rum_content = _RummageFileContent(
                    file_info.name, file_info.size, self.current_encoding, self.file_content
                )
                self.file_content = None

                with rum_content as rum_buff:
                    skip = False
                    if self.is_binary is False and rum_content.encoding.encode == "bin":
                        self.is_binary = True
                        self.current_encoding = rum_content.encoding
                        if not self.process_binary:
                            skip = True
                        file_info = file_info._replace(encoding=self.current_encoding.encode.upper())

                    if not skip:

                        pattern, replace, flags = self.search_obj[0]
                        if REGEX_SUPPORT and isinstance(pattern, bregex._REGEX_TYPE):
                            self.reverse = bool(pattern.flags & regex.REVERSE)
                        else:
                            self.reverse = False

                        for m in self._findall(rum_buff, pattern, replace, flags, file_info):
                            if self.reverse:
                                text.appendleft(rum_buff[m.end(0):self.text_offset])
                                text.appendleft(self.expand_match(m))
                                self.text_offset = m.start(0)
                            else:
                                text.append(rum_buff[self.text_offset:m.start(0)])
                                text.append(self.expand_match(m))
                                self.text_offset = m.end(0)

                            yield FileRecord(
                                file_info,
                                MatchRecord(
                                    0,                     # lineno
                                    0,                     # colno
                                    (m.start(), m.end()),  # Postion of match
                                    None,                  # Line(s) in which match is found
                                    (0, 0)                 # Number of lines shown before and after matched line(s)
                                ),
                                None
                            )

                            file_record_sent = True

                            if self.abort:
                                break

                        # Grab the rest of the file if we found things to replace.
                        if not self.abort and (text or len(self.search_obj) > 1):
                            if self.reverse:
                                text.appendleft(rum_buff[:self.text_offset])
                            else:
                                text.append(rum_buff[self.text_offset:])

                # Additional chained replaces
                count = 1
                if not skip and not self.abort and len(self.search_obj) > 1:

                    for pattern, replace, flags in self.search_obj[1:]:

                        text2 = (b'' if self.is_binary else '').join(text)
                        text = deque()

                        for m in self._findall(text2, pattern, replace, flags, file_info):
                            if self.reverse:
                                text.appendleft(text2[m.end(0):self.text_offset])
                                text.appendleft(self.expand_match(m))
                                self.text_offset = m.start(0)
                            else:
                                text.append(text2[self.text_offset:m.start(0)])
                                text.append(self.expand_match(m))
                                self.text_offset = m.end(0)

                            yield FileRecord(
                                file_info,
                                MatchRecord(
                                    0,                     # lineno
                                    0,                     # colno
                                    (m.start(), m.end()),  # Postion of match
                                    None,                  # Line(s) in which match is found
                                    (0, 0)                 # Number of lines shown before and after matched line(s)
                                ),
                                None
                            )

                            file_record_sent = True

                            if self.abort:
                                break

                        count += 1

                        # Grab the rest of the file if we found things to replace.
                        if not self.abort and (text or count < len(self.search_obj)):
                            if self.reverse:
                                text.appendleft(text2[:self.text_offset])
                            else:
                                text.append(text2[self.text_offset:])

                        if self.abort:
                            break

                if not self.abort and text:
                    # Update the file or buffer depending on what is being used.
                    # For a buffer, we will actually return the the content via a BufferRecord.
                    if is_buffer:
                        yield self._update_buffer(text)
                        file_record_sent = True
                    else:
                        self._update_file(
                            file_info.name, text
                        )
                elif is_buffer:
                    # Buffers always return a Buffer record at the end
                    yield BufferRecord(None, None)
                    file_record_sent = True

                if not file_record_sent:
                    # Always return at least one record
                    yield FileRecord(file_info, None, None)

            except Exception:
                # Return a record with the failure attached
                if is_buffer:
                    yield BufferRecord(None, get_exception())
                else:
                    yield FileRecord(file_info, None, get_exception())

    def search(self):
        """Search target file or buffer returning a generator of results."""

        file_info, error = self._get_file_info(self.file_obj)
        if error is not None:
            yield FileRecord(file_info, None, error)
        elif not self.is_binary or self.process_binary:

            try:
                file_record_sent = False
                rum_content = _RummageFileContent(
                    file_info.name, file_info.size, self.current_encoding, self.file_content
                )
                self.file_content = None
                with rum_content as rum_buff:

                    skip = False
                    if self.is_binary is False and rum_content.encoding.encode == "bin":
                        self.is_binary = True
                        self.current_encoding = rum_content.encoding
                        if not self.process_binary:
                            skip = True
                        file_info = file_info._replace(encoding=self.current_encoding.encode.upper())

                    if not skip:
                        self.line_map = []
                        self.last_line = False
                        self.line_iter = None
                        get_context = self._get_binary_context if self.is_binary else self._get_line_context

                        for pattern, replace, flags in self.search_obj:
                            if hasattr(rum_buff, 'seek'):
                                rum_buff.seek(0)

                            if (
                                self.line_iter is None and not self.boolean and
                                not self.count_only and not self.is_binary
                            ):
                                self.line_iter = RE_LINE_ENDINGS.finditer(rum_buff)

                            for m in self._findall(rum_buff, pattern, replace, flags, file_info):

                                if not self.boolean and not self.count_only:
                                    # Get line related context.
                                    lines, match, context, row, col = get_context(rum_buff, m)
                                else:
                                    row = 1
                                    col = 1
                                    match = (m.start(), m.end())
                                    lines = None
                                    context = (0, 0)

                                file_record_sent = True

                                yield FileRecord(
                                    file_info,
                                    MatchRecord(
                                        row,          # lineno
                                        col,          # colno
                                        match,        # Postion of match
                                        lines,        # Line(s) in which match is found
                                        context       # Number of lines shown before and after matched line(s)
                                    ),
                                    None
                                )

                                if self.boolean:
                                    break

                                # Have we exceeded the maximum desired matches?
                                if self.max_count is not None:
                                    self.max_count -= 1

                                    if self.max_count == 0:
                                        break

                                if self.abort:
                                    break

                            if self.abort:
                                break

                if not file_record_sent:
                    yield FileRecord(file_info, None, None)
            except Exception:
                yield FileRecord(
                    file_info, None,
                    get_exception()
                )

    def run(self):
        """Start the file search."""

        try:
            if self.search_obj.is_replace():
                for rec in self.search_and_replace():
                    yield rec
            else:
                for rec in self.search():
                    yield rec
        except Exception:
            yield FileRecord(
                FileInfoRecord(
                    self.idx,
                    self.file_obj.name,
                    None,
                    None,
                    None,
                    None,
                    None
                ),
                None,
                get_exception()
            )


class _DirWalker(object):
    """Walk the directory."""

    def __init__(
        self, directory, file_pattern, file_regex_match,
        folder_exclude, dir_regex_match, recursive,
        show_hidden, size, modified, created, backup_location,
        backup_to_folder=False, regex_mode=RE_MODE
    ):
        """Init the directory walker object."""

        self.abort = False
        if (regex_mode in REGEX_MODES and not REGEX_SUPPORT) or (RE_MODE > regex_mode or regex_mode > BREGEX_MODE):
            regex_mode = RE_MODE
        self.regex_mode = regex_mode
        self.dir = directory
        self.size = (size[0], size[1]) if size is not None else size
        self.modified = modified
        self.created = created
        self.file_pattern = file_pattern
        self.file_regex_match = file_regex_match
        self.folder_exclude = folder_exclude
        self.dir_regex_match = dir_regex_match
        self.recursive = recursive
        self.show_hidden = show_hidden
        self.backup2folder = backup_to_folder
        if backup_location:
            self.backup_ext = ('.%s' % backup_location.lower()) if not self.backup2folder else DEFAULT_BAK
            self.backup_folder = backup_location if self.backup2folder else DEFAULT_FOLDER_BAK
        else:
            self.backup_ext = None
            self.backup_folder = None

    def _parse_pattern(self, string, regex_match, force_default=False):
        r"""Compile or format the inclusion\exclusion pattern."""

        pattern = None
        exclude_pattern = None
        if regex_match:
            if not string and force_default:
                string = r'.*'
            if string:
                if self.regex_mode == BREGEX_MODE:
                    pattern = bregex.compile(string, bregex.IGNORECASE)
                elif self.regex_mode == REGEX_MODE:
                    pattern = regex.compile(string, regex.IGNORECASE | regex.ASCII)
                elif self.regex_mode == BRE_MODE:
                    pattern = bre.compile(string, bre.IGNORECASE | bre.ASCII)
                else:
                    pattern = re.compile(string, re.IGNORECASE | re.ASCII)
        else:
            if not string and force_default:
                string = '*'
            if string:
                pattern, exclude_pattern = Wildcard2Regex(string).translate()
        return pattern, exclude_pattern

    def _is_hidden(self, path):
        """Check if file is hidden."""

        if not self.show_hidden:
            return is_hidden(path)
        return False

    def _compare_value(self, limit_check, current):
        """Compare file attribute against limits."""

        value_okay = False
        qualifier = limit_check[0]
        limit = limit_check[1]
        if qualifier == "eq":
            if current == limit:
                value_okay = True
        elif qualifier == "lt":
            if current < limit:
                value_okay = True
        elif qualifier == "gt":
            if current > limit:
                value_okay = True
        return value_okay

    def _is_times_okay(self, pth):
        """Verify file times meet requirements."""

        times_okay = False
        mod_okay = False
        cre_okay = False
        self.modified_time = getmtime(pth)
        self.created_time = getctime(pth)
        if self.modified is None:
            mod_okay = True
        else:
            mod_okay = self._compare_value(self.modified, self.modified_time)
        if self.created is None:
            cre_okay = True
        else:
            cre_okay = self._compare_value(self.created, self.created_time)
        if mod_okay and cre_okay:
            times_okay = True
        return times_okay

    def _is_size_okay(self, pth):
        """Verify file size meets requirements."""

        size_okay = False
        self.current_size = os.path.getsize(pth)
        if self.size is None:
            size_okay = True
        else:
            size_okay = self._compare_value(self.size, self.current_size)
        return size_okay

    def _is_backup(self, name, directory=False):
        """Check if file or directory is a rumcore backup."""

        is_backup = False

        if directory:
            if self.backup_folder and self.backup2folder:
                if util.platform() == "windows":  # pragma: no cover
                    name = name.lower()
                if name == self.backup_folder:
                    is_backup = True
        else:
            if self.backup_ext and not self.backup2folder:
                if util.platform() == "windows":  # pragma: no cover
                    name = name.lower()
                if name.endswith(self.backup_ext):
                    is_backup = True

        return is_backup

    def _valid_file(self, base, name):
        """Return whether a file can be searched."""

        valid = False
        if (
            self.re_file_pattern is not None and
            not self._is_hidden(os.path.join(base, name)) and
            not self._is_backup(name)
        ):
            valid = self.re_file_pattern.fullmatch(name) is not None
            if self.re_exclude_file_pattern and self.re_exclude_file_pattern.fullmatch(name) is not None:
                valid = False
            if valid:
                valid = self._is_size_okay(os.path.join(base, name))
            if valid:
                valid = self._is_times_okay(os.path.join(base, name))
        return valid

    def _valid_folder(self, base, name):
        """Return whether a folder can be searched."""

        valid = True
        if not self.recursive:
            valid = False
        elif self._is_hidden(os.path.join(base, name)) or self._is_backup(name, True):
            valid = False
        elif self.re_folder_exclude is not None:
            valid = self.re_folder_exclude.fullmatch(name) is None
            if (
                self.re_negated_folder_exclude is not None and
                self.re_negated_folder_exclude.fullmatch(name) is not None
            ):
                valid = True
        return valid

    def kill(self):
        """Abort process."""

        self.abort = True

    def walk(self):
        """Start search for valid files."""

        for base, dirs, files in os.walk(self.dir):
            # Remove child folders based on exclude rules
            for name in dirs[:]:
                try:
                    if not self._valid_folder(base, name):
                        dirs.remove(name)
                except Exception:  # pragma: no cover
                    dirs.remove(name)
                    yield FileAttrRecord(
                        os.path.join(base, name),
                        None,
                        None,
                        None,
                        None,
                        False,
                        get_exception()
                    )
                if self.abort:
                    break

            # Seach files if they were found
            if len(files):
                # Only search files that are in the inlcude rules
                for name in files:
                    try:
                        valid = self._valid_file(base, name)
                    except Exception:  # pragma: no cover
                        valid = False
                        yield FileAttrRecord(
                            os.path.join(base, name),
                            None,
                            None,
                            None,
                            None,
                            False,
                            get_exception()
                        )

                    if valid:
                        filename = os.path.join(base, name)
                        yield FileAttrRecord(
                            filename,
                            os.path.splitext(filename)[1].lower().lstrip('.'),
                            self.current_size,
                            self.modified_time,
                            self.created_time,
                            False,
                            None
                        )
                    else:
                        yield FileAttrRecord(os.path.join(base, name), None, None, None, None, True, None)

                    if self.abort:
                        break
            if self.abort:
                break

    def compile_search_patterns(self):
        """Compile search patterns."""

        self.re_file_pattern, self.re_exclude_file_pattern = self._parse_pattern(
            self.file_pattern, self.file_regex_match, force_default=True
        )
        self.re_folder_exclude, self.re_negated_folder_exclude = self._parse_pattern(
            self.folder_exclude, self.dir_regex_match
        )

    def run(self):
        """Run the directory walker."""

        try:
            self.compile_search_patterns()
            for f in self.walk():
                yield f
        except Exception:  # pragma: no cover
            yield ErrorRecord(get_exception())


class Rummage(object):
    """Perform the rummaging."""

    def __init__(
        self, target, searches, file_pattern=None, folder_exclude=None,
        flags=0, context=(0, 0), max_count=None, encoding=None, size=None,
        modified=None, created=None, backup_location=None, regex_mode=RE_MODE,
        encoding_options=None
    ):
        """Initialize Rummage object."""

        self.abort = False
        self.searcher = None
        self.path_walker = None
        if (regex_mode in REGEX_MODES and not REGEX_SUPPORT) or (RE_MODE > regex_mode > BREGEX_MODE):
            regex_mode = RE_MODE
        self.regex_mode = regex_mode

        if encoding_options is None:
            encoding_options = text_decode.DEFAULT_ENCODING_OPTIONS
        self.encoding_options = encoding_options

        self.search_params = searches
        self.file_flags = flags & FILE_MASK
        self.context = context
        self.encoding = self._verify_encoding(encoding) if encoding is not None else None
        self.skipped = 0

        self.backup_location = backup_location
        if not self.backup_location or not isinstance(self.backup_location, str):
            self.backup_location = DEFAULT_FOLDER_BAK if bool(self.file_flags & BACKUP_FOLDER) else DEFAULT_BAK

        self.buffer_input = bool(self.file_flags & BUFFER_INPUT)
        self.current_encoding = None
        self.idx = -1
        self.records = -1
        self.max = int(max_count) if max_count is not None else None
        self.target = os.path.abspath(target) if not self.buffer_input else target
        file_regex_match = bool(self.file_flags & FILE_REGEX_MATCH)
        dir_regex_match = bool(self.file_flags & DIR_REGEX_MATCH)
        self.path_walker = None
        self.is_binary = False
        self.files = deque()
        self.queue = deque()
        self.file_error = None

        # Initialize search objects:
        # - _DirWalker for if target is a folder
        # - Append FileAttrRecord if target is a file or buffer
        if not self.buffer_input and os.path.isdir(self.target):
            self.path_walker = _DirWalker(
                self.target,
                file_pattern,
                file_regex_match,
                folder_exclude,
                dir_regex_match,
                bool(self.file_flags & RECURSIVE),
                bool(self.file_flags & SHOW_HIDDEN),
                size,
                modified,
                created,
                self.backup_location if bool(self.file_flags & BACKUP) else None,
                bool(self.file_flags & BACKUP_FOLDER),
                self.regex_mode
            )
        elif not self.buffer_input and os.path.isfile(self.target):
            try:
                self.files.append(
                    FileAttrRecord(
                        self.target,
                        os.path.splitext(self.target)[1].lower().lstrip('.'),
                        os.path.getsize(self.target),
                        getmtime(self.target),
                        getctime(self.target),
                        False,
                        None
                    )
                )
            except Exception:
                self.file_error = FileAttrRecord(
                    self.target,
                    None,
                    None,
                    None,
                    None,
                    False,
                    get_exception()
                )
        elif self.buffer_input:
            self.files.append(
                FileAttrRecord(
                    None,
                    None,
                    len(self.target),
                    ctime(),
                    ctime(),
                    False,
                    None
                )
            )

    def _verify_encoding(self, encoding):
        """Verify the encoding is okay."""

        enc = encoding.lower()
        # Normalize UTFx encodings as we detect order and boms later.
        if encoding in _U8:
            enc = 'utf-8'
        elif encoding in _U16:
            enc = 'utf-16'
        elif encoding in _U16BE:
            enc = 'utf-16-be'
        elif encoding in _U16LE:
            enc = 'utf-16-le'
        elif encoding in _U32:
            enc = 'utf-32'
        elif encoding in _U32BE:
            enc = 'utf-32-be'
        elif encoding in _U32LE:
            enc = 'utf-32-le'

        if enc != 'bin':
            codecs.lookup(enc)

        return enc

    def get_status(self):
        """Return number of files searched out of current number of files crawled."""
        return self.idx + 1, self.idx + 1 + len(self.files), self.skipped, self.records + 1

    def kill(self):
        """Kill process."""

        self.abort = True
        if self.searcher:
            self.searcher.kill()
        if self.path_walker:
            self.path_walker.kill()

    def _get_next_file(self):
        """Get the next file from the file crawler results."""

        file_info = self.files.popleft() if self.path_walker is None else None
        if file_info is None:
            if not self.abort:
                self.idx += 1
                file_info = self.files.popleft()
        else:
            self.idx += 1

        return file_info

    def _drain_records(self):
        """Grab all current records."""

        while len(self.queue) and (self.max is None or self.max != 0):
            record = self.queue.popleft()
            if record.error is None:
                self.records += 1
                if self.max is not None and record.match is not None:
                    self.max -= 1
            yield record

    def search_file(self, content_buffer=None):
        """Search file."""

        file_info = self._get_next_file()
        if file_info is not None:

            self.searcher = _FileSearch(
                self.search_params,
                file_info,
                self.idx,
                self.file_flags,
                self.context,
                self.encoding,
                self.backup_location,
                self.max,
                content_buffer,
                self.regex_mode,
                self.encoding_options
            )
            for rec in self.searcher.run():
                if rec.error is None:
                    self.records += 1
                    if self.max is not None and rec.match is not None:
                        self.max -= 1
                yield rec

                if self.max is not None and self.max == 0:
                    self.kill()

    def walk_files(self):
        """Crawl the directory."""

        folder_limit = 100

        for f in self.path_walker.run():
            if hasattr(f, 'skipped') and f.skipped:
                self.idx += 1
                self.records += 1
                self.skipped += 1
                yield f
            elif f.error:
                self.idx += 1
                self.records += 1
                yield f
            else:
                self.files.append(f)

            if self.abort:
                self.files.clear()

            # Search 50 for every 100
            if len(self.files) >= folder_limit:

                for x in range(0, 50):

                    for rec in self.search_file():
                        yield rec

        # Clear files if kill was signalled.
        if self.abort:
            self.files.clear()

        # Finish searching the rest
        while self.files and not self.abort:
            for rec in self.search_file():
                yield rec

    def find(self):
        """
        Walk through a given directory searching files via the provided pattern.

        If given a file directly, it will search the file only.
        Return the results of each file via a generator.
        """

        self.alive = True
        self.idx = -1
        self.skipped = 0

        if len(self.search_params):
            if self.file_error is not None:
                # Single target wasn't set up right; just return error.
                yield self.file_error
            elif len(self.files):
                # Single target search (already set up); just search the file.
                for result in self.search_file(self.target if self.buffer_input else None):
                    yield result
            else:
                # Crawl directory and search files.
                for result in self.walk_files():
                    yield result
        else:
            # No search pattern, so just return files that *would* be searched.
            for f in self.path_walker.run():
                self.idx += 1
                self.records += 1
                if hasattr(f, 'skipped') and f.skipped:
                    self.skipped += 1
                yield f

                if self.abort:
                    self.files.clear()
