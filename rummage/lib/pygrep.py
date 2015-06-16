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
import threading
import Queue
import sys
from os import walk
from fnmatch import fnmatch
from os.path import isdir, isfile, join, abspath, getsize
from time import ctime
from collections import namedtuple
import traceback
import codecs
from . import ure
from . import text_decode
from .file_times import getmtime, getctime
from .file_hidden import is_hidden

LITERAL = 1
IGNORECASE = 2
DOTALL = 4
RECURSIVE = 8
FILE_REGEX_MATCH = 16
DIR_REGEX_MATCH = 32
BUFFER_INPUT = 64

# There doesn't appear to be a real advantage when using multiple threads.
# It will bascially take the same amount of time because of GIL (not really parallel; switches back and forth).
# So a file that is taking a long time with multiple threads, will take even longer,
# but other threads can complete in that time.  You will get matches out of order as well since it is switching
# between search threads.
#
# Essentially, with one thread, a file taking a long time will block, but multi-threads will allow other files to
# complete while the lengthy file finishes.  But in the end, single and mult-threaded take about the same time.
# Its kind of a wash.
#
# Multiprocessing is an alternative, but Rummage currently pushes too much data through the queue; it bogs down
# the queue since it has to serialize the data and pipe it through to the other process.  Performance is bad.
_NUM_THREADS = 1
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


def set_threads(number):
    """Set number of threads to use."""

    global _NUM_THREADS
    if not _RUNNING and 0 < number < 4:
        _NUM_THREADS = number


def threaded_walker(
    directory, file_pattern, file_regex_match,
    folder_exclude, dir_regex_match, recursive,
    show_hidden, size, modified, created
):
    """Peform threaded search."""

    global _RUNNING
    global _STARTED
    _RUNNING = True
    _STARTED = True
    try:
        walker = _DirWalker(
            directory, file_pattern, file_regex_match,
            folder_exclude, dir_regex_match, recursive,
            show_hidden, size, modified, created
        )
        walker.run()
    except Exception:
        print(str(traceback.format_exc()))
        pass
    _RUNNING = False


def _re_pattern(pattern, ignorecase=False, dotall=False, multiline=True):
    """Prepare regex search pattern flags."""

    flags = ure.UNICODE
    if multiline:
        flags |= ure.MULTILINE
    if ignorecase:
        flags |= ure.IGNORECASE
    if dotall:
        flags |= ure.DOTALL
    return ure.compile(pattern, flags)


def _literal_pattern(pattern, ignorecase=False, dotall=False, multiline=True):
    """Prepare literal search pattern flags."""

    flags = ure.UNICODE
    if multiline:
        flags |= ure.MULTILINE
    if ignorecase:
        flags |= ure.IGNORECASE
    if dotall:
        flags |= ure.DOTALL
    return ure.compile(ure.escape(pattern), flags)


class GrepException(Exception):

    """Grep exception."""


class FileInfo(namedtuple('FileInfo', ['id', 'name', 'size', 'modified', 'created', 'encoding'], verbose=False)):

    """Class for tracking file info."""


class FileRecord(namedtuple('FileRecord', ['info', 'match', 'error'], verbose=False)):

    """A record that reports file info, matching status, and errors."""


class MatchRecord(namedtuple('MatchRecord', ['lineno', 'colno', 'match', 'lines', 'ending', 'context'], verbose=False)):

    """A record that contains match info, lineno content, context, etc."""


class _FileSearch(object):

    """Search for files."""

    hex_tx_table = ("." * 32) + "".join(chr(c) for c in xrange(32, 127)) + ("." * 129)

    def __init__(self, pattern, flags, context, truncate_lines, boolean, count_only):
        """Init the file search object."""

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

    def __decode_file(self, filename):
        """Calls file encode guesser and decodes file if possible."""

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

    def __get_file_info(self, filename, size, m_time, c_time, content=None):
        """Create file info record."""

        string_buffer = content is not None
        error = None
        file_info = None

        try:
            if content is None:
                content = self.__read_file(filename)
                if content is None:
                    raise GrepException("Could not read %s" % filename)
        except Exception:
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
        except Exception:
            if error is None:
                error = str(traceback.format_exc())

        return file_info, content, error

    def __tx_bin(self, content):
        """Format binary data in a friendly way. Display only ASCII."""

        return content.translate(self.hex_tx_table)

    def __get_lines(self, content, m, line_ending, binary=False):
        """Return the full line(s) of code of the found region."""

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
        """Get column of where result is found in file."""

        col = 1
        for x in reversed(range(0, absolute_col)):
            if content[x] == line_ending:
                break
            col += 1
        return col

    def __get_row(self, start, line_map):
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

    def __get_line_ending(self, file_content):
        """Get the line ending for the file content by scanning for and evaluating the first new line occurance."""

        line_map = []
        ending = None
        line_ending = ure.compile(r"(?:(\r\n)|(\r)|(\n))")
        for m in line_ending.finditer(file_content):
            if ending is None:
                ending = "\r" if m.group(2) else "\n"
            line_map.append(m.end())
        return "\n" if ending is None else ending, line_map

    def __findall(self, file_content):
        """Find all occurences of search pattern in file."""

        for m in self.find_method(file_content):
            yield m
            if _ABORT:
                break

    def search(
        self, file_obj, file_id, queue, max_count=None, all_utf8=False,
        process_binary=False, file_content=None
    ):
        """Search target file or buffer returning a generator of results."""

        try:
            self.idx = file_id
            self.all_utf8 = all_utf8
            self.is_binary = False

            target, file_content, error = self.__get_file_info(
                file_obj[0], file_obj[1], file_obj[2], file_obj[3], file_content
            )

            if error is not None:
                # Unable to read
                queue.put(FileRecord(target, None, error))
                return
            elif target is None or (file_content is None or (self.is_binary and not process_binary)):
                # No file or shouldn't process binary; quit
                return

            line_ending = None
            line_map = []
            file_record_sent = False

            for m in self.__findall(file_content):
                if not self.boolean and not self.count_only:
                    if line_ending is None:
                        line_ending, line_map = self.__get_line_ending(file_content)

                if not self.boolean and not self.count_only:
                    file_record_sent = True
                    # Get context etc.
                    lines, match, context = self.__get_lines(file_content, m, line_ending, self.is_binary)

                    queue.put(
                        FileRecord(
                            target,
                            MatchRecord(
                                self.__get_row(
                                    m.start(), line_map  # lineno
                                ),
                                self.__get_col(          # colno
                                    file_content,
                                    m.start(),
                                    line_ending
                                ),
                                match,                   # Postion of match
                                lines,                   # Line(s) in which match is found
                                line_ending,             # Line ending for file
                                context                  # Number of lines shown before and after matched line(s)
                            ),
                            None
                        )
                    )
                else:
                    file_record_sent = True
                    queue.put(
                        FileRecord(
                            target,
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
                    )

                if self.boolean:
                    break

                # Have we exceeded the maximum desired matches?
                if max_count is not None:
                    max_count -= 1

                    if max_count == 0:
                        break

            if not file_record_sent:
                queue.put(FileRecord(target, None, None))
        except Exception:
            queue.put(FileRecord(target, None, str(traceback.format_exc())))


def file_search(
    params, file_obj, file_id, queue, max_count=None,
    all_utf8=False, process_binary=False, file_content=None
):
    """Start a thread for a file search."""
    fs = _FileSearch(
        params.pattern, params.flags, params.context,
        params.truncate_lines, params.boolean, params.count_only
    )
    fs.search(file_obj, file_id, queue, max_count, all_utf8, process_binary, file_content)


class SearchParams(object):

    """Search parameter object."""

    def __init__(self, pattern, flags, context, truncate_lines, boolean, count_only):
        """Search parameters."""

        self.pattern = pattern
        self.flags = flags
        self.context = context
        self.truncate_lines = truncate_lines
        self.boolean = boolean
        self.count_only = count_only


class _DirWalker(object):

    """Walk the directory."""

    def __init__(
        self, directory, file_pattern, file_regex_match,
        folder_exclude, dir_regex_match, recursive,
        show_hidden, size, modified, created
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
        self.files = []

    def __is_hidden(self, path):
        """Check if file is hidden."""

        if not self.show_hidden:
            return is_hidden(path)
        return False

    def __compare_value(self, limit_check, current):
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

    def __is_times_okay(self, pth):
        """Verify file times meet requirements."""

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
        """Verify file size meets requirements."""

        size_okay = False
        self.current_size = getsize(pth)
        if self.size is None:
            size_okay = True
        else:
            size_okay = self.__compare_value(self.size, self.current_size)
        return size_okay

    def __valid_file(self, base, name):
        """Returns whether a file can be searched."""

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
        except Exception:
            valid = False
        return valid

    def __valid_folder(self, base, name):
        """Returns whether a folder can be searched."""

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
        except Exception:
            valid = False
        return valid

    def run(self):
        """Start search for valid files."""

        global _FILES
        global _ABORT
        with _LOCK:
            _FILES = []
        for base, dirs, files in walk(self.dir):
            # Remove child folders based on exclude rules
            for name in dirs[:]:
                if not self.__valid_folder(base, name):
                    dirs.remove(name)
                if _ABORT:
                    break

            # Seach files if they were found
            if len(files):
                # Only search files that are in the inlcude rules
                for name in files[:]:
                    if self.__valid_file(base, name):
                        with _LOCK:
                            _FILES.append((join(base, name), self.current_size, self.modified_time, self.created_time))
                    if _ABORT:
                        break
            if _ABORT:
                _ABORT = False
                break


class Grep(object):

    """Perform the grepping."""

    def __init__(
        self, target, pattern, file_pattern=None, folder_exclude=None,
        flags=0, context=(0, 0), max_count=None,
        show_hidden=False, all_utf8=False, size=None,
        modified=None, created=None, text=False, truncate_lines=False,
        boolean=False, count_only=False
    ):
        """Initialize Grep object."""

        global _FILES
        global _RUNNING
        global _ABORT
        if not _RUNNING and _ABORT:
            _ABORT = False
        if _RUNNING:
            raise GrepException("Grep process already running!")

        self.search_params = SearchParams(pattern, flags, context, truncate_lines, boolean, count_only)
        self.buffer_input = bool(flags & BUFFER_INPUT)
        self.all_utf8 = all_utf8
        self.current_encoding = None
        self.idx = -1
        self.records = -1
        self.max = int(max_count) if max_count is not None else None
        self.target = abspath(target) if not self.buffer_input else target
        self.process_binary = text
        file_regex_match = bool(flags & FILE_REGEX_MATCH)
        dir_regex_match = bool(flags & DIR_REGEX_MATCH)
        self.kill = False
        self.path_walker = None
        self.is_binary = False
        if not self.buffer_input and isdir(self.target):
            self.path_walker = threading.Thread(
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
            self.path_walker.setDaemon(True)
        elif not self.buffer_input and isfile(self.target):
            with _LOCK:
                _FILES = [
                    (
                        self.target,
                        getsize(self.target),
                        getmtime(self.target),
                        getctime(self.target)
                    )
                ]
        elif self.buffer_input:
            with _LOCK:
                _FILES = [
                    (
                        "buffer input",
                        len(self.target),
                        ctime(),
                        ctime()
                    )
                ]
        else:
            with _LOCK:
                _FILES = []

    def __get_dir_pattern(self, folder_exclude, dir_regex_match):
        """Compile or format the directory exclusion pattern."""

        pattern = None
        if folder_exclude is not None:
            pattern = ure.compile(
                folder_exclude, ure.IGNORECASE
            ) if dir_regex_match else [f.lower() for f in folder_exclude.split("|")]
        return pattern

    def __get_file_pattern(self, file_pattern, file_regex_match):
        """Compile or format the file pattern."""

        pattern = None
        if file_pattern is not None:
            pattern = ure.compile(
                file_pattern, ure.IGNORECASE
            ) if file_regex_match else [f.lower() for f in file_pattern.split("|")]
        return pattern

    def get_status(self):
        """Return number of files searched out of current number of files crawled."""

        if self.path_walker is not None:
            return self.idx + 1 if self.idx != -1 else 0, len(_FILES), self.records + 1 if self.records != -1 else 0
        else:
            return 1, 1, self.records + 1 if self.records != -1 else 0

    def abort(self):
        """Abort the search."""

        global _ABORT
        _ABORT = True
        self.kill = True

    def __wait_for_thread(self):
        """Wait for thread to start."""

        global _STARTED
        self.path_walker.start()

        # Try to wait in case the
        # "is running" check happens too quick
        while not _STARTED:
            pass
        _STARTED = False

    def __get_next_file(self):
        """Get the next file from the file crawler results."""

        file_info = None
        while file_info is None:
            if _RUNNING:
                if len(_FILES) - 1 > self.idx:
                    self.idx += 1
                    file_info = _FILES[self.idx]
            else:
                if len(_FILES) - 1 > self.idx and not self.kill:
                    self.idx += 1
                    file_info = _FILES[self.idx]
                else:
                    break
        return file_info

    def open_thread_slot(self, threads):
        """Find the first open thread slot."""

        idx = -1
        for x in range(0, len(threads)):
            if threads[x] is None or not threads[x].is_alive():
                idx = x
                break
        return idx

    def busy_thread(self, threads):
        """Are any of the threads busy?  Return the first index."""

        idx = -1
        for x in range(0, len(threads)):
            if threads[x] is not None and threads[x].is_alive():
                idx = x
                break
        return idx

    def drain_records(self):
        """Grab all current records."""

        for x in range(0, self.queue.qsize()):
            if self.max is not None and self.max == 0:
                break
            record = self.queue.get()
            if record.error is None:
                self.records += 1
                if self.max is not None and record.match is not None:
                    self.max -= 1
                yield record

    def file_read(self, content_buffer=None):
        """Perform search on on files in a directory."""

        # Start path walking thread if searching a path
        if self.path_walker is not None:
            self.__wait_for_thread()

        self.idx = -1
        self.queue = Queue.Queue()
        threads = [None] * _NUM_THREADS
        file_info = []

        # Wait for when a file is available
        while True:
            if self.kill:
                break

            # Acquire the maximum number of files to search (if available)
            acquire = _NUM_THREADS - len(file_info)
            for x in range(0, acquire):
                obj = self.__get_next_file()
                if obj is not None:
                    file_info.append(obj)
                else:
                    break

            # No more files to search
            if len(file_info) == 0:
                break

            # Start a search thread(s)
            idx = self.open_thread_slot(threads)
            while idx != -1 and len(file_info):
                threads[idx] = threading.Thread(
                    target=file_search,
                    args=(
                        self.search_params,
                        file_info.pop(0),
                        self.idx,
                        self.queue,
                        self.max,
                        self.all_utf8,
                        self.process_binary,
                        content_buffer
                    )
                )
                threads[idx].daemon = True
                threads[idx].start()
                idx = self.open_thread_slot(threads)

            # Grab recently finished records
            for record in self.drain_records():
                yield record

            if self.max is not None and self.max == 0:
                self.abort()
                break

        # Wait for processes to finish
        while self.busy_thread(threads) != -1:
            pass

        # Clean out remaining records
        for record in self.drain_records():
            yield record

        threads = []
        self.queue = None

    def find(self):
        """
        Walk through a given directory searching files via the provided pattern.

        If given a file directly, it will search the file only.
        Return the results of each file via a generator.
        """

        for result in self.file_read(self.target if self.buffer_input else None):
            yield result
