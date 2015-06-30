# -*- coding: utf-8 -*-
"""
Pygrep.

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
import codecs
import mmap
import re
import shutil
import sys
import traceback
from collections import namedtuple
from fnmatch import fnmatch
from os import walk
from os.path import isdir, isfile, join, abspath, getsize
from time import ctime
from . import text_decode
from . import backrefs
from .file_times import getmtime, getctime
from .file_hidden import is_hidden
from collections import deque

PY3 = (3, 0) <= sys.version_info < (4, 0)

if PY3:
    binary_type = bytes  # noqa
    string_type = str  # noqa

    def to_ascii_bytes(string):
        """Convert unicode to ascii byte string."""

        return bytes(string, 'ascii')
else:
    binary_type = str  # noqa
    string_type = basestring  # noqa

    def to_ascii_bytes(string):
        """Convert unicode to ascii byte string."""

        return bytes(string)

LITERAL = 1
IGNORECASE = 2
DOTALL = 4
RECURSIVE = 8
FILE_REGEX_MATCH = 16
DIR_REGEX_MATCH = 32
BUFFER_INPUT = 64

TRUNCATE_LENGTH = 120

ABORT = False
_PROCESS = False

if sys.platform.startswith('win'):
    _PLATFORM = "windows"
elif sys.platform == "darwin":
    _PLATFORM = "osx"
else:
    _PLATFORM = "linux"

U32 = (
    'u32', 'utf32', 'utf_32'
)

U32BE = (
    'utf-32be', 'utf_32_be'
)

U32LE = (
    'utf-32le', 'utf_32_le'
)

U16 = (
    'u16', 'utf16', 'utf_16'
)

U16BE = (
    'utf-16be', 'utf_16_be'
)

U16LE = (
    'utf-16le', 'utf_16_le'
)

U8 = (
    'u8', 'utf', 'utf8', 'utf_8', 'utf_8_sig', 'utf-8-sig'
)


def _re_pattern(pattern, ignorecase=False, dotall=False, multiline=True, binary=False):
    """Prepare regex search pattern flags."""

    flags = 0
    if multiline:
        flags |= re.MULTILINE if binary else re.MULTILINE
    if ignorecase:
        flags |= re.IGNORECASE if binary else re.IGNORECASE
    if dotall:
        flags |= re.DOTALL if binary else re.DOTALL
    if not binary:
        flags |= re.UNICODE
    return backrefs.compile_search(pattern, flags)


def _literal_pattern(pattern, ignorecase=False, dotall=False, multiline=True, binary=False):
    """Prepare literal search pattern flags."""

    flags = 0
    if multiline:
        flags |= re.MULTILINE if binary else re.MULTILINE
    if ignorecase:
        flags |= re.IGNORECASE if binary else re.IGNORECASE
    if dotall:
        flags |= re.DOTALL if binary else re.DOTALL
    if not binary:
        flags |= re.UNICODE
    return re.compile(re.escape(pattern), flags)


class GrepException(Exception):

    """Grep exception."""


class FileAttr(namedtuple('FileAttr', ['name', 'size', 'modified', 'created'])):

    """File Attributes."""


class FileInfo(namedtuple('FileInfo', ['id', 'name', 'size', 'modified', 'created', 'encoding'])):

    """Class for tracking file info."""


class FileRecord(namedtuple('FileRecord', ['info', 'match', 'error'])):

    """A record that reports file info, matching status, and errors."""


class MatchRecord(namedtuple('MatchRecord', ['lineno', 'colno', 'match', 'lines', 'ending', 'context'])):

    """A record that contains match info, lineno content, context, etc."""


class BufferReplaceRecord(namedtuple('BufferReplaceRecord', ['content', 'error'])):

    """A record with the string buffer replacements."""


class RummageFileContent(object):

    """Either return a string or memory map file object."""

    def __init__(self, name, size, encoding, file_content=None):
        """Initialize."""
        self.name = name
        self.size = size
        self.encoding = encoding
        self.file_obj = None
        self.file_content = file_content
        self.string_buffer = file_content is not None
        self.file_map = None

    def __enter__(self):
        """Return content of either a memory map file or string."""

        return self.file_content if self.string_buffer else self._read_file()

    def __exit__(self, *args):
        """Close file obj and memory map object if open."""

        if self.file_map is not None:
            self.file_map.close()
        if self.file_obj is not None:
            self.file_obj.close()

    def _read_file(self):
        """Read the file in."""

        if self.encoding is not None:
            if self.encoding.encode == "bin":
                self.file_obj = open(self.name, "rb")
            else:
                enc = self.encoding.encode
                if enc == 'utf-8':
                    enc = 'utf-8-sig'
                elif enc.startswith('utf-16'):
                    enc = 'utf-16'
                elif enc.startswith('utf-32'):
                    enc = 'utf-32'
                self.file_obj = codecs.open(self.name, 'r', encoding=enc)
            if self.size != '0.00KB':
                self.file_map = mmap.mmap(self.file_obj.fileno(), 0, access=mmap.ACCESS_READ)
            else:
                self.file_content = self.file_obj.read()
        return self.file_content if self.file_content is not None else self.file_map


class _FileSearch(object):

    """Search for files."""

    hex_tx_table = ("�" * 32) + "".join(chr(c) for c in range(32, 127)) + ("�" * 129)

    def __init__(self, args, file_obj, file_id, max_count, file_content):
        """Init the file search object."""

        self.literal = bool(args.flags & LITERAL)
        self.ignorecase = bool(args.flags & IGNORECASE)
        self.dotall = bool(args.flags & DOTALL)
        self.boolean = bool(args.boolean)
        self.count_only = bool(args.count_only)
        self.truncate_lines = args.truncate_lines
        self.backup = args.backup
        self.backup_ext = '.%s' % args.backup_ext
        self.bom = None
        if self.truncate_lines:
            self.context = (0, 0)
        else:
            self.context = args.context

        # Prepare search
        self.pattern = args.pattern
        self.replace = args.replace
        self.expand = None
        self.idx = file_id
        self.file_obj = file_obj
        self.max_count = max_count
        self.encoding = args.encoding if args.encoding is not None else None
        self.process_binary = args.process_binary
        self.file_content = file_content
        self.is_binary = False
        self.current_encoding = None

    def _get_binary_context(self, content, m):
        """Get context info for binary file."""

        row = 0
        col = 0
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
            content[start:end].translate(self.hex_tx_table),
            (match_start, match_end),
            (before, after),
            row,
            col
        )

    def _get_line_context(self, content, m, line_map):
        """Get context info about the line."""

        before, after = self.context
        row = self._get_row(m.start(), line_map)
        col = m.start() + 1
        idx = row - 1
        lines = len(line_map) - 1
        start = 0
        end = len(content) - 1

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
            after -= end_idx - lines
            end_idx = None

        # Calculate column of cursor and actual start and end of context
        if lines != -1:
            col_start = idx - 1
            col = m.start() - line_map[col_start] if col_start >= 0 else m.start() + 1
            if start_idx is not None:
                start = line_map[start_idx] + 1
            if end_idx is not None:
                end = line_map[end_idx]

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

    def _get_row(self, start, line_map):
        """Get line number where result is found in file."""

        # Binary Search
        mn = 0
        mx = len(line_map) - 1
        if mx == -1 or start <= line_map[mn]:
            return mn + 1

        if start > line_map[-1]:
            return mx + 2

        while mx - mn != 1:
            idx = mn + ((mx - mn) >> 1)
            if start > line_map[idx]:
                mn = idx
            else:
                mx = idx

        return mx + 1

    def _get_line_ending(self, file_content):
        """Get the line ending for the file content by scanning for and evaluating the first new line occurance."""

        if self.is_binary:
            nl = b'\n'
            cr = b'\r'
        else:
            nl = '\n'
            cr = '\r'
        line_map = []
        ending = None
        offset = 0
        last_offset = None
        for c in file_content:
            if last_offset is not None and (c == nl or c == cr):
                if last_offset + 1 == offset and c == nl:
                    ending = c
                    line_map.append(offset)
                else:
                    line_map.append(last_offset)
                    if c == ending:
                        line_map.append(offset)
                last_offset = None
            elif ending is None and (c == nl or c == cr):
                ending = c
                if ending == cr:
                    last_offset = offset
                else:
                    line_map.append(offset)
            elif c == ending:
                line_map.append(offset)
            offset += 1
        if last_offset is not None:
            line_map.append(last_offset)
        return nl if ending is None else ending, line_map

    def _findall(self, file_content):
        """Find all occurences of search pattern in file."""

        replace = None
        pattern = None

        if self.is_binary:
            pattern = to_ascii_bytes(self.pattern)
            if self.replace is not None:
                replace = to_ascii_bytes(self.replace)
        else:
            pattern = self.pattern
            replace = self.replace

        if pattern is not None:
            if self.literal:
                pattern = _literal_pattern(pattern, self.ignorecase, binary=self.is_binary)
            else:
                pattern = _re_pattern(pattern, self.ignorecase, self.dotall, binary=self.is_binary)
            if replace is not None and not self.literal:
                self.expand = backrefs.compile_replace(pattern, self.replace)
            else:
                self.expand = None

            for m in pattern.finditer(file_content):
                yield m
                if self.kill:
                    break

    def _update_file(self, file_name, content, encoding):
        """Update the file content."""

        if self.backup:
            backup = file_name + self.backup_ext
            shutil.copy2(file_name, backup)

        if encoding.bom:
            # Write the bomb first, then write in utf format out in the specified order.
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

        if not string_buffer:
            try:
                self.current_encoding = text_decode.Encoding('bin', None)
                self.is_binary = False
                if self.encoding is not None:
                    if self.encoding == 'bin':
                        self.current_encoding = text_decode.Encoding(self.encoding, None)
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
                    encoding = text_decode.guess(file_obj.name, verify=True, verify_block_size=1024)
                    if encoding is not None:
                        if encoding.encode == "bin":
                            self.is_binary = True
                        self.current_encoding = encoding
            except Exception:
                error = str(traceback.format_exc())
        elif isinstance(self.file_content, binary_type):
            self.is_binary = True

        file_info = FileInfo(
            self.idx,
            file_obj.name,
            "%.2fKB" % (float(file_obj.size) / 1024.0),
            file_obj.modified,
            file_obj.created,
            self.current_encoding.encode.upper() if not string_buffer else "--"
        )

        return file_info, error

    @property
    def kill(self):
        """Kill process."""

        return ABORT

    def search_and_replace(self):
        """Search and replace."""

        text = deque()

        file_info, error = self._get_file_info(self.file_obj)
        if error is not None:
            if self.file_content:
                yield BufferReplaceRecord(None, error)
            else:
                yield FileRecord(file_info, None, error)
        if not self.is_binary or self.process_binary:

            try:
                with RummageFileContent(
                    file_info.name, file_info.size, self.current_encoding, self.file_content
                ) as rum_file:
                    offset = 0

                    for m in self._findall(rum_file):
                        text.append(rum_file[offset:m.start(0)])
                        text.append(
                            self.expand(m) if self.expand is not None else m.expand(self.replace)
                        )
                        offset = m.end(0)

                        yield FileRecord(
                            file_info,
                            MatchRecord(
                                0,                     # lineno
                                0,                     # colno
                                (m.start(), m.end()),  # Postion of match
                                None,                  # Line(s) in which match is found
                                None,                  # Line ending for file
                                (0, 0)                 # Number of lines shown before and after matched line(s)
                            ),
                            None
                        )

                        if self.kill:
                            break

                    # Grab the rest of the file if we found things to replace.
                    if not self.kill and text:
                        text.append(rum_file[offset:])

                if not self.kill and text:
                    if self.file_content:
                        yield BufferReplaceRecord((b'' if self.is_binary else '').join(text), None)
                    else:
                        self._update_file(
                            file_info.name, text, self.current_encoding
                        )
                else:
                    if self.file_content:
                        yield BufferReplaceRecord(None, None)
                    else:
                        yield FileRecord(file_info, None, None)

            except Exception:
                if self.file_content:
                    yield BufferReplaceRecord(None, str(traceback.format_exc()))
                else:
                    yield FileRecord(file_info, None, str(traceback.format_exc()))

    def search(self):
        """Search target file or buffer returning a generator of results."""

        file_info, error = self._get_file_info(self.file_obj)
        if error is not None:
            yield FileRecord(file_info, None, error)
        if not self.is_binary or self.process_binary:

            try:
                with RummageFileContent(
                    file_info.name, file_info.size, self.current_encoding, self.file_content
                ) as rum_file:
                    line_ending = None
                    line_map = []
                    file_record_sent = False

                    for m in self._findall(rum_file):
                        if line_ending is None and not self.boolean and not self.count_only and not self.is_binary:
                            line_ending, line_map = self._get_line_ending(rum_file)

                        if not self.boolean and not self.count_only:
                            # Get line related context.
                            if self.is_binary:
                                lines, match, context, row, col = self._get_binary_context(
                                    rum_file, m
                                )
                            else:
                                lines, match, context, row, col = self._get_line_context(
                                    rum_file, m, line_map
                                )
                        else:
                            row = 0
                            col = 0
                            match = (m.start(), m.end())
                            lines = None
                            line_ending = None
                            context = (0, 0)

                        file_record_sent = True

                        yield FileRecord(
                            file_info,
                            MatchRecord(
                                row,                     # lineno
                                col,                     # colno
                                match,                   # Postion of match
                                lines,                   # Line(s) in which match is found
                                line_ending,             # Line ending for file
                                context                  # Number of lines shown before and after matched line(s)
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

                        if self.kill:
                            break

                if not file_record_sent:
                    yield FileRecord(file_info, None, None)
            except Exception:
                yield FileRecord(file_info, None, str(traceback.format_exc()))

    def run(self):
        """Start the file search thread."""

        try:
            if self.replace is not None:
                for rec in self.search_and_replace():
                    yield rec
            else:
                for rec in self.search():
                    yield rec
        except Exception:
            print(str(traceback.format_exc()))


class SearchParams(object):

    """Search parameter object."""

    def __init__(self):
        """Search parameters."""

        self.pattern = None
        self.flags = 0
        self.context = 0
        self.truncate_lines = False
        self.boolean = False
        self.count_only = False
        self.replace = None
        self.backup = True
        self.encoding = None
        self.process_binary = False
        self.backup_ext = 'bak'


class _DirWalker(object):

    """Walk the directory."""

    def __init__(
        self, directory, file_pattern, file_regex_match,
        folder_exclude, dir_regex_match, recursive,
        show_hidden, size, modified, created, backup_ext
    ):
        """Init the directory walker object."""

        self.dir = directory
        self.size = (size[0], size[1] * 1024) if size is not None else size
        self.modified = modified
        self.created = created
        self.file_pattern = file_pattern
        self.file_regex_match = file_regex_match
        self.dir_regex_match = dir_regex_match
        self.folder_exclude = folder_exclude
        self.recursive = recursive
        self.show_hidden = show_hidden
        self.backup_ext = None
        ext = '.%s' % backup_ext if backup_ext else None
        if ext is not None:
            self.backup_ext = ext.lower() if _PLATFORM == "windows" else ext

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
        self.current_size = getsize(pth)
        if self.size is None:
            size_okay = True
        else:
            size_okay = self._compare_value(self.size, self.current_size)
        return size_okay

    def _is_backup(self, name):
        """Check if file is a pygrep backup."""

        is_backup = False
        if self.backup_ext is not None:
            if _PLATFORM == "windows":
                if name.lower().endswith(self.backup_ext):
                    is_backup = True
            elif name.endswith(self.backup_ext):
                is_backup = True
        return is_backup


    def _valid_file(self, base, name):
        """Return whether a file can be searched."""

        try:
            valid = False
            if self.file_pattern is not None and not self._is_hidden(join(base, name)) and not self._is_backup(name):
                if self.file_regex_match:
                    valid = True if self.file_pattern.match(name) is not None else False
                else:
                    matched = False
                    exclude = False
                    for p in self.file_pattern:
                        if len(p) > 1 and p[0] == "-":
                            if fnmatch(name.lower(), p[1:]):
                                exclude = True
                                break
                        elif fnmatch(name.lower(), p):
                            matched = True
                    if exclude:
                        valid = False
                    elif matched:
                        valid = True
                if valid:
                    valid = self._is_size_okay(join(base, name))
                if valid:
                    valid = self._is_times_okay(join(base, name))
        except Exception:
            valid = False
        return valid

    def _valid_folder(self, base, name):
        """Return whether a folder can be searched."""

        valid = True
        try:
            if not self.recursive:
                valid = False
            elif self._is_hidden(join(base, name)):
                valid = False
            elif self.folder_exclude is not None:
                if self.dir_regex_match:
                    valid = False if self.folder_exclude.match(name) is not None else True
                else:
                    matched = False
                    exclude = False
                    for p in self.folder_exclude:
                        if len(p) > 1 and p[0] == "-":
                            if fnmatch(name.lower(), p[1:]):
                                matched = True
                                break
                        elif fnmatch(name.lower(), p):
                            exclude = True
                    if matched:
                        valid = True
                    elif exclude:
                        valid = False
        except Exception:
            valid = False
        return valid

    @property
    def kill(self):
        """Abort process."""

        return ABORT

    def walk(self):
        """Start search for valid files."""

        for base, dirs, files in walk(self.dir):
            # Remove child folders based on exclude rules
            for name in dirs[:]:
                if not self._valid_folder(base, name):
                    dirs.remove(name)
                if self.kill:
                    break

            # Seach files if they were found
            if len(files):
                # Only search files that are in the inlcude rules
                for name in files:
                    if self._valid_file(base, name):
                        yield FileAttr(
                            join(base, name),
                            self.current_size,
                            self.modified_time,
                            self.created_time
                        )

                    if self.kill:
                        break
            if self.kill:
                break

    def run(self):
        """Run the directory walker."""

        try:
            for f in self.walk():
                yield f
        except Exception:
            print(str(traceback.format_exc()))


class Grep(object):

    """Perform the grepping."""

    def __init__(
        self, target, pattern, file_pattern=None, folder_exclude=None,
        flags=0, context=(0, 0), max_count=None,
        show_hidden=False, encoding=None, size=None,
        modified=None, created=None, text=False, truncate_lines=False,
        boolean=False, count_only=False, replace=None,
        backup=False, backup_ext='bak'
    ):
        """Initialize Grep object."""

        global _PROCESS
        global ABORT
        if _PROCESS and _PROCESS.alive:
            ABORT = True
            raise GrepException("Grep process already running!")
        else:
            ABORT = False
            _PROCESS = self

        self.alive = False
        self.search_params = SearchParams()
        self.search_params.pattern = pattern
        self.search_params.flags = flags
        self.search_params.context = context
        self.search_params.truncate_lines = truncate_lines
        self.search_params.boolean = boolean
        self.search_params.count_only = count_only
        self.search_params.replace = replace
        self.search_params.backup = backup
        self.search_params.encoding = self._verify_encoding(encoding) if encoding is not None else None
        self.search_params.process_binary = text
        self.search_params.backup_ext = backup_ext if backup_ext and isinstance(backup_ext, string_type) else 'bak'

        self.buffer_input = bool(flags & BUFFER_INPUT)
        self.current_encoding = None
        self.idx = -1
        self.records = -1
        self.max = int(max_count) if max_count is not None else None
        self.target = abspath(target) if not self.buffer_input else target
        self.process_binary = text
        file_regex_match = bool(flags & FILE_REGEX_MATCH)
        dir_regex_match = bool(flags & DIR_REGEX_MATCH)
        self.path_walker = None
        self.is_binary = False
        self.files = deque()
        self.queue = deque()
        if not self.buffer_input and isdir(self.target):
            self.path_walker = _DirWalker(
                self.target,
                self._get_file_pattern(file_pattern, file_regex_match),
                file_regex_match,
                self._get_dir_pattern(folder_exclude, dir_regex_match),
                dir_regex_match,
                bool(flags & RECURSIVE),
                show_hidden,
                size,
                modified,
                created,
                self.search_params.backup_ext if backup else None
            )
        elif not self.buffer_input and isfile(self.target):
            self.files.append(
                FileAttr(
                    self.target,
                    getsize(self.target),
                    getmtime(self.target),
                    getctime(self.target)
                )
            )
        elif self.buffer_input:
            self.files.append(
                FileAttr(
                    "buffer input",
                    len(self.target),
                    ctime(),
                    ctime()
                )
            )

    def _verify_encoding(self, encoding):
        """Verify the encoding is okay."""

        enc = encoding.lower()
        # Normalize UTFx encodings as we detect order and boms later.
        if encoding in U8:
            enc = 'utf-8'
        elif encoding in U16:
            enc = 'utf-16'
        elif encoding in U16BE:
            enc = 'utf-16-be'
        elif encoding in U16LE:
            enc = 'utf-16-le'
        elif encoding in U32:
            enc = 'utf-32'
        elif encoding in U32BE:
            enc = 'utf-32-be'
        elif encoding in U32LE:
            enc = 'utf-32-le'

        if enc != 'bin':
            codecs.lookup(enc)

        return enc

    def _get_dir_pattern(self, folder_exclude, dir_regex_match):
        """Compile or format the directory exclusion pattern."""

        pattern = None
        if folder_exclude is not None:
            pattern = backrefs.compile_search(
                folder_exclude, re.IGNORECASE
            ) if dir_regex_match else [f.lower() for f in folder_exclude.split("|")]
        return pattern

    def _get_file_pattern(self, file_pattern, file_regex_match):
        """Compile or format the file pattern."""

        pattern = None
        if file_pattern is not None:
            pattern = backrefs.compile_search(
                file_pattern, re.IGNORECASE
            ) if file_regex_match else [f.lower() for f in file_pattern.split("|")]
        return pattern

    def get_status(self):
        """Return number of files searched out of current number of files crawled."""
        return self.idx + 1, self.idx + 1 + len(self.files), self.records + 1

    @property
    def kill(self):
        """Kill process."""

        return ABORT

    def _get_next_file(self):
        """Get the next file from the file crawler results."""

        file_info = self.files.popleft() if self.path_walker is None else None
        if file_info is None:
            if not self.kill:
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

        global ABORT

        file_info = self._get_next_file()
        if file_info is not None:

            self.searcher = _FileSearch(
                self.search_params,
                file_info,
                self.idx,
                self.max,
                content_buffer
            )
            for rec in self.searcher.run():
                if rec.error is None:
                    self.records += 1
                    if self.max is not None and rec.match is not None:
                        self.max -= 1
                yield rec

                if self.max is not None and self.max == 0:
                    ABORT = True

    def walk_files(self):
        """Single threaded run."""

        folder_limit = 100

        for f in self.path_walker.run():
            self.files.append(f)

            if self.kill:
                self.files.clear()

            # Search 50 for every 100
            if len(self.files) >= folder_limit:

                for x in range(0, 50):

                    for rec in self.search_file():
                        yield rec

        # Clear files if kill was signalled.
        if self.kill:
            self.files.clear()

        # Finish searching the rest
        while self.files and not self.kill:
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

        if len(self.files):
            for result in self.search_file(self.target if self.buffer_input else None):
                yield result
        else:
            for result in self.walk_files():
                yield result
        self.alive = False
