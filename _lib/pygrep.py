"""
pygrep

Licensed under MIT
Copyright (c) 2011 Isaac Muse <isaacmuse@gmail.com>
https://gist.github.com/facelessuser/5757669

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import threading
import sys
from os import walk
from fnmatch import fnmatch
from os.path import isdir, join, abspath, getsize
from time import sleep, ctime
from collections import namedtuple
import traceback
import codecs

import _lib.ure as ure
import _lib.text_decode as text_decode
from _lib.file_times import getmtime, getctime
from _lib.file_hidden import is_hidden


LITERAL = 1
IGNORECASE = 2
DOTALL = 4
RECURSIVE = 8
FILE_REGEX_MATCH = 16
DIR_REGEX_MATCH = 32
BUFFER_INPUT = 64

_LOCK = threading.Lock()
_FILES = []
_RUNNING = False
_STARTED = False
_ABORT = False

if sys.platform.startswith('win'):
    _PLATFORM = "windows"
elif sys.platform == "darwin":
    _PLATFORM = "osx"
else:
    _PLATFORM = "linux"

LINE_ENDINGS = ure.compile(r"(?:(\r\n)|(\r)|(\n))")
HEX_TX_TABLE = ("." * 32) + "".join(chr(c) for c in xrange(32, 127)) + ("." * 129)


def threaded_walker(
    directory, file_pattern, file_regex_match,
    folder_exclude, dir_regex_match, recursive,
    show_hidden, size, modified, created
):
    """
    Peform threaded search
    """

    global _RUNNING
    global _STARTED
    with _LOCK:
        _RUNNING = True
        _STARTED = True
    try:
        walker = _DirWalker(
            directory, file_pattern, file_regex_match,
            folder_exclude, dir_regex_match, recursive,
            show_hidden, size, modified, created
        )
        walker.run()
    except:
        print(str(traceback.format_exc()))
        pass
    with _LOCK:
        _RUNNING = False


def _re_pattern(pattern, ignorecase=False, dotall=False, multiline=True):
    """
    Prepare regex search pattern flags
    """

    flags = ure.UNICODE
    if multiline:
        flags |= ure.MULTILINE
    if ignorecase:
        flags |= ure.IGNORECASE
    if dotall:
        flags |= ure.DOTALL
    return ure.compile(pattern, flags)


def _literal_pattern(pattern, ignorecase=False, dotall=False, multiline=True):
    """
    Prepare literal search pattern flags
    """

    flags = ure.UNICODE
    if multiline:
        flags |= ure.MULTILINE
    if ignorecase:
        flags |= ure.IGNORECASE
    if dotall:
        flags |= ure.DOTALL
    return ure.compile(ure.escape(pattern), flags)


class GrepException(Exception):
    pass


class FileInfo(namedtuple('FileInfo', ['id', 'name', 'size', 'modified', 'created', 'encoding'], verbose=False)):
    """
    Class for tracking file info
    """
    pass


class FileRecord(namedtuple('FileRecord', ['info', 'match', 'error'], verbose=False)):
    """
    A record that reports file info, matching status, and errors
    """

    pass


class MatchRecord(namedtuple('MatchRecord', ['lineno', 'colno', 'match', 'lines', 'ending', 'context'], verbose=False)):
    """
    A record that contains match info, lineno content, context, etc.
    """

    pass


class _FileSearch(object):
    def __init__(self, pattern, flags, context, truncate_lines, boolean, count_only):
        """
        Init the file search object
        """

        self.literal = bool(flags & LITERAL)
        self.ignorecase = bool(flags & IGNORECASE)
        self.dotall = bool(flags & DOTALL)
        self.boolean = bool(boolean)
        self.count_only = bool(count_only)
        self.truncate_lines = truncate_lines
        if self.truncate_lines:
            self.context = (0, 0)
        else:
            self.context = context

        # Prepare search
        self.pattern = _literal_pattern(pattern, self.ignorecase) if self.literal else _re_pattern(pattern, self.ignorecase, self.dotall)
        self.find_method = self.pattern.finditer

    def __tx_bin(self, content):
        """
        Format binary data in a friendly way. Display only ASCII.
        """

        return content.translate(HEX_TX_TABLE)

    def __get_lines(self, content, m, line_ending, binary=False):
        """
        Return the full line(s) of code of the found region.
        """

        start = m.start()
        end = m.end()
        bfr_end = len(content) - 1
        before = 0
        after = 0

        # Get the start of the context
        while start > 0:
            if content[start - 1] != line_ending:
                start -= 1
            elif before >= self.context[0]:
                break
            else:
                before += 1
                start -= 1

        # Get the end of the context
        while end < bfr_end:
            if content[end] != line_ending:
                end += 1
            elif after >= self.context[1]:
                break
            else:
                after += 1
                end += 1

        # Make the match start and end relative to the context snippet
        match_start = m.start() - start
        match_end = match_start + m.end() - m.start()

        # Truncate long lines if desired
        if self.truncate_lines:
            length = end - start
            if length > 256:
                end = start + 256
                length = 256

            # Recalculate relative match start and end
            if match_start > length:
                match_start = length
            if match_end > length:
                match_end = 256

        # Return the context snippet, where the match occurs,
        # and how many lines of context before and after
        return (
            content[start:end] if not binary else self.__tx_bin(content[start:end]),
            (match_start, match_end),
            (before, after)
        )

    def __get_col(self, content, absolute_col, line_ending):
        """
        Get column of where result is found in file
        """

        col = 1
        for x in reversed(range(0, absolute_col)):
            if content[x] == line_ending:
                break
            col += 1
        return col

    def __get_line_ending(self, file_content):
        """
        Get the line ending for the file content by
        scanning for and evaluating the first new line occurance.
        """

        ending = LINE_ENDINGS.search(file_content)
        return "\r" if ending is not None and ending.group(2) else "\n"

    def __findall(self, file_content):
        """
        Find all occurences of search pattern in file.
        """

        for m in self.find_method(file_content):
            yield m

    def search(self, target, file_content, max_count=None, binary=False):
        """
        Search target file or buffer returning a generator of results.
        """

        line_ending = None

        file_record_sent = False

        for m in self.__findall(file_content):
            if not self.boolean and not self.count_only:
                if line_ending is None:
                    line_ending = self.__get_line_ending(file_content)

            # Have we exceeded the maximum desired matches?
            if max_count is not None:
                if max_count == 0:
                    break
                else:
                    max_count -= 1

            if not file_record_sent:
                file_record_sent = True
                yield FileRecord(target, True, None)

            if not self.boolean and not self.count_only:
                # Get context etc.
                lines, match, context = self.__get_lines(file_content, m, line_ending, binary)

                yield MatchRecord(
                    file_content.count(line_ending, 0, m.start()) + 1,     # lineno
                    self.__get_col(file_content, m.start(), line_ending),  # colno
                    match,                                                 # Postion of match
                    lines,                                                 # Line(s) in which match is found
                    line_ending,                                           # Line ending for file
                    context                                                # Number of lines shown before and after matched line(s)
                )
            else:
                yield MatchRecord(
                    0,                                                     # lineno
                    0,                                                     # colno
                    (m.start(), m.end()),                                  # Postion of match
                    None,                                                  # Line(s) in which match is found
                    None,                                                  # Line ending for file
                    (0, 0)                                                 # Number of lines shown before and after matched line(s)
                )

            if self.boolean:
                break

        if not file_record_sent:
            yield FileRecord(target, False, None)


class _DirWalker(object):
    def __init__(
        self, directory, file_pattern, file_regex_match,
        folder_exclude, dir_regex_match, recursive,
        show_hidden, size, modified, created
    ):
        """
        Init the directory walker object
        """

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
        self.files = []

    def __is_hidden(self, path):
        """
        Check if file is hidden
        """

        if not self.show_hidden:
            return is_hidden(path)
        return False

    def __compare_value(self, limit_check, current):
        """
        Compare file attribute against limits
        """

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

    def __is_times_okay(self, pth):
        """
        Verify file times meet requirements
        """

        times_okay = False
        mod_okay = False
        cre_okay = False
        self.modified_time = getmtime(pth)
        self.created_time = getctime(pth)
        if self.modified is None:
            mod_okay = True
        else:
            mod_okay = self.__compare_value(self.modified, self.modified_time)
        if self.created is None:
            cre_okay = True
        else:
            cre_okay = self.__compare_value(self.created, self.created_time)
        if mod_okay and cre_okay:
            times_okay = True
        return times_okay

    def __is_size_okay(self, pth):
        """
        Verify file size meets requirements
        """

        size_okay = False
        self.current_size = getsize(pth)
        if self.size is None:
            size_okay = True
        else:
            size_okay = self.__compare_value(self.size, self.current_size)
        return size_okay

    def __valid_file(self, base, name):
        """
        Returns whether a file can be searched.
        """

        try:
            valid = False
            if self.file_pattern is not None and not self.__is_hidden(join(base, name)):
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
                    valid = self.__is_size_okay(join(base, name))
                if valid:
                    valid = self.__is_times_okay(join(base, name))
        except:
            valid = False
        return valid

    def __valid_folder(self, base, name):
        """
        Returns whether a folder can be searched.
        """

        valid = True
        try:
            if not self.recursive:
                valid = False
            elif self.__is_hidden(join(base, name)):
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
        except:
            valid = False
        return valid

    def run(self):
        """
        Start search for valid files
        """

        global _FILES
        global _ABORT
        with _LOCK:
            _FILES = []
        for base, dirs, files in walk(self.dir):
            # Remove child folders based on exclude rules
            [dirs.remove(name) for name in dirs[:] if not self.__valid_folder(base, name)]

            # Seach files if they were found
            if len(files):
                # Only search files in that are in the inlcude rules
                for f in [(name, self.current_size, self.modified_time, self.created_time) for name in files[:] if self.__valid_file(base, name)]:
                    with _LOCK:
                        _FILES.append((join(base, f[0]), f[1], f[2], f[3]))
                    if _ABORT:
                        break
            if _ABORT:
                with _LOCK:
                    _ABORT = False
                break


class Grep(object):
    def __init__(
        self, target, pattern, file_pattern=None, folder_exclude=None,
        flags=0, context=(0, 0), max_count=None,
        show_hidden=False, all_utf8=False, size=None,
        modified=None, created=None, text=False, truncate_lines=False,
        boolean=False, count_only=False
    ):
        """
        Initialize Grep object.
        """

        global _RUNNING
        global _ABORT
        with _LOCK:
            if not _RUNNING and _ABORT:
                _ABORT = False
            if _RUNNING:
                raise GrepException("Grep process already running!")

        self.search = _FileSearch(pattern, flags, context, truncate_lines, boolean, count_only)
        self.buffer_input = bool(flags & BUFFER_INPUT)
        self.all_utf8 = all_utf8
        self.current_encoding = None
        self.idx = -1
        self.records = -1
        self.target = abspath(target) if not self.buffer_input else target
        self.max = max_count
        self.process_binary = text
        file_regex_match = bool(flags & FILE_REGEX_MATCH)
        dir_regex_match = bool(flags & DIR_REGEX_MATCH)
        self.kill = False
        self.thread = None
        self.is_binary = False
        if not self.buffer_input and isdir(self.target):
            self.thread = threading.Thread(
                target=threaded_walker,
                args=(
                    self.target,
                    self.__get_file_pattern(file_pattern, file_regex_match),
                    file_regex_match,
                    self.__get_dir_pattern(folder_exclude, dir_regex_match),
                    dir_regex_match,
                    bool(flags & RECURSIVE),
                    show_hidden,
                    size,
                    modified,
                    created
                )
            )
            self.thread.setDaemon(True)

    def __get_dir_pattern(self, folder_exclude, dir_regex_match):
        """
        Compile or format the directory exclusion pattern
        """

        pattern = None
        if folder_exclude is not None:
            pattern = ure.compile(folder_exclude, ure.IGNORECASE) if dir_regex_match else [f.lower() for f in folder_exclude.split("|")]
        return pattern

    def __get_file_pattern(self, file_pattern, file_regex_match):
        """
        Compile or format the file pattern
        """

        pattern = None
        if file_pattern is not None:
            pattern = ure.compile(file_pattern, ure.IGNORECASE) if file_regex_match else [f.lower() for f in file_pattern.split("|")]
        return pattern

    def __decode_file(self, filename):
        """
        Calls file encode guesser and decodes file if possible
        """

        bfr, self.current_encoding = text_decode.guess(filename, False)
        if self.current_encoding == "BIN":
            self.is_binary = True
        return bfr

    def __read_file(self, file_name):
        """
        Open the file in the best guessed encoding for search.
        Guesses by elimination
        Currently opens:
            UTF32 if BOM present
            UTF16 if BOM present or if only one null found in file
            UTF8 if it contains no bad UTF8 char sequences or includes UTF8 BOM
            LATIN-1 if not a file above and contains no NULLs, and no invalid LATIN-1 chars
            CP1252 if not above and does not contain NULLs
        """

        content = None
        self.current_encoding = "BIN"
        self.is_binary = False

        # Force UTF for all
        if self.all_utf8:
            self.current_encoding = "UTF8"
            with codecs.open(file_name, encoding="utf-8-sig", errors="replace") as f:
                content = f.read()
                return content

        # Guess encoding and decode file
        return self.__decode_file(file_name)

    def get_status(self):
        """
        Return number of files searched out
        of current number of files crawled
        """

        if self.thread is not None:
            return self.idx + 1 if self.idx != -1 else 0, len(_FILES), self.records + 1 if self.records != -1 else 0
        else:
            return 1, 1, self.records + 1 if self.records != -1 else 0

    def abort(self):
        """
        Abort the search
        """

        global _ABORT
        with _LOCK:
            _ABORT = True
        self.kill = True

    def __wait_for_thread(self):
        """
        Wait for thread to start
        """

        global _STARTED
        self.thread.start()

        # Try to wait in case the
        # "is running" check happens too quick
        while not _STARTED:
            sleep(0.1)
        with _LOCK:
            _STARTED = False

    def __get_file_info(self, filename, size, m_time, c_time, content=None):
        """
        Create file info record
        """

        string_buffer = content is not None
        error = None
        file_info = None

        try:
            if content is None:
                content = self.__read_file(filename)
                if content is None:
                    raise GrepException("Could not read %s" % filename)
        except:
            error = str(traceback.format_exc())

        try:
            file_info = FileInfo(
                self.idx,
                filename,
                "%.2fKB" % (float(size) / 1024.0),
                m_time,
                c_time,
                self.current_encoding if not string_buffer else "--"
            )
        except:
            if error is None:
                error = str(traceback.format_exc())

        return file_info, content, error

    def __get_next_file(self):
        """
        Get the next file from the file crawler results
        """

        file_info = None
        error = None
        content = None
        while file_info is None:
            if _RUNNING:
                if len(_FILES) - 1 > self.idx:
                    self.idx += 1
                    info = _FILES[self.idx]
                    file_info, content, error = self.__get_file_info(info[0], info[1], info[2], info[3])
                else:
                    sleep(0.1)
            else:
                if len(_FILES) - 1 > self.idx and not self.kill:
                    self.idx += 1
                    info = _FILES[self.idx]
                    file_info, content, error = self.__get_file_info(info[0], info[1], info[2], info[3])
                else:
                    break
        return file_info, content, error

    def multi_file_read(self, max_count):
        """
        Perform search on on files in a directory
        """

        self.idx = -1

        self.__wait_for_thread()

        # Wait for when a file is available
        while True:
            file_info, content, error = self.__get_next_file()

            if error is not None:
                # Unable to read
                yield FileRecord(file_info, False, error)
            elif file_info is None:
                # No file; quit
                break
            elif content is None or (self.is_binary and not self.process_binary):
                continue
            else:
                # Parse the given file
                try:
                    for result in self.search.search(file_info, content, max_count, self.is_binary):
                        # Report additional file info
                        self.records += 1
                        yield result

                        if max_count is not None and isinstance(result, MatchRecord):
                            max_count -= 1

                        if self.kill:
                            break
                except GeneratorExit:
                    pass

                if max_count is not None and max_count == 0:
                    break

    def single_file_read(self, file_name, max_count):
        """
        Perform search on a single file
        """

        self.idx = 0

        file_info, content, error = self.__get_file_info(
            file_name,
            getsize(file_name),
            getmtime(file_name),
            getctime(file_name)
        )

        if error is not None:
            # Unable to read
            yield FileRecord(file_info, False, error)
        elif file_info is not None or content is not None:
            try:
                for result in self.search.search(file_info, content, max_count, self.is_binary):
                    self.records += 1
                    yield result

                    if self.kill:
                        break
            except GeneratorExit:
                pass

    def buffer_read(self, target_buffer, max_count):
        """
        Perform search on an input buffer
        """

        self.idx = 0

        file_info, content, error = self.__get_file_info(
            "buffer input",
            len(target_buffer),
            ctime(),
            ctime(),
            content=target_buffer
        )

        if error is not None:
            # Unable to read
            yield FileRecord(file_info, False, error)
        elif file_info is not None or content is not None:
            try:
                for result in self.search.search(file_info, content, max_count, False):
                    self.records += 1
                    yield result

                    if self.kill:
                        break
            except GeneratorExit:
                pass

    def find(self):
        """
        Walks through a given directory searching files via the provided pattern.
        If given a file directly, it will search the file only.
        Return the results of each file via a generator.
        """
        max_count = int(self.max) if self.max is not None else None

        if self.thread is not None:
            for result in self.multi_file_read(max_count):
                yield result
        elif self.buffer_input:
            for result in self.buffer_read(self.target, max_count):
                yield result
        else:
            for result in self.single_file_read(self.target, max_count):
                yield result
