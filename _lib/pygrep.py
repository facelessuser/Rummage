"""
pygrep

Licensed under MIT
Copyright (c) 2011 Isaac Muse <isaacmuse@gmail.com>
https://gist.github.com/facelessuser/5757669

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import ure
import threading
import sys
from os import walk
from fnmatch import fnmatch
from os.path import isdir, join, abspath, basename, getsize, getmtime
from os.path import getctime as get_creation_time
from time import sleep
import struct
import traceback
import codecs
import text_decode
import traceback
from ctypes import *

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

if _PLATFORM == "osx":
    import Foundation
elif _PLATFORM == "windows":
    import ctypes

LINE_ENDINGS = ure.compile(r"(?:(\r\n)|(\r)|(\n))")


class struct_timespec(Structure):
    _fields_ = [('tv_sec', c_long), ('tv_nsec', c_long)]


class struct_stat64(Structure):
    _fields_ = [
        ('st_dev', c_int32),
        ('st_mode', c_uint16),
        ('st_nlink', c_uint16),
        ('st_ino', c_uint64),
        ('st_uid', c_uint32),
        ('st_gid', c_uint32),
        ('st_rdev', c_int32),
        ('st_atimespec', struct_timespec),
        ('st_mtimespec', struct_timespec),
        ('st_ctimespec', struct_timespec),
        ('st_birthtimespec', struct_timespec),
        ('dont_care', c_uint64 * 8)
    ]


libc = CDLL('libc.dylib')
stat64 = libc.stat64
stat64.argtypes = [c_char_p, POINTER(struct_stat64)]


def getctime(pth):
    if _PLATFORM == "osx":
        # Get the appropriate creation time on OSX
        buf = struct_stat64()
        rv = stat64(pth, pointer(buf))
        if rv != 0:
            raise OSError("Couldn't stat file %r" % pth)
        return buf.st_birthtimespec.tv_sec
    else:
        # Get the creation time for everyone else
        return get_creation_time(pth)


def threaded_walker(
    directory, file_pattern, file_regex_match,
    folder_exclude, dir_regex_match, recursive,
    show_hidden, size, modified, created
):
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
    flags = ure.UNICODE
    if multiline:
        flags |= ure.MULTILINE
    if ignorecase:
        flags |= ure.IGNORECASE
    if dotall:
        flags |= ure.DOTALL
    return ure.compile(pattern, flags)


def _literal_pattern(pattern, ignorecase=False):
    return pattern.lower() if ignorecase else pattern


class GrepException(Exception):
    pass


class _FindRegion(object):
    def __init__(self, start, end):
        """
        Initialize find region result object.
        """

        self.__find_range = [start, end]

    def start(self):
        """
        Return start of find region result.
        """

        return self.__find_range[0]

    def end(self):
        """
        Return end of find region result.
        """

        return self.__find_range[1]


class _FileSearch(object):
    def __init__(self, pattern, flags, context):
        self.literal = bool(flags & LITERAL)
        self.ignorecase = bool(flags & IGNORECASE)
        self.dotall = bool(flags & DOTALL)

        self.context = context

        # Prepare search
        self.pattern = _literal_pattern(pattern, self.ignorecase) if self.literal else _re_pattern(pattern, self.ignorecase, self.dotall)
        self.find_method = self.__findall_literal if self.literal else self.pattern.finditer

    def __get_lines(self, content, m):
        """
        Return the full line(s) of code of the found region.
        """

        start = m.start()
        end = m.end()
        bfr_end = len(content) - 1
        before = 0
        after = 0

        while start > 0:
            if content[start - 1] != "\n":
                start -= 1
            elif before >= self.context[0]:
                break
            else:
                before += 1
                start -= 1

        while end < bfr_end:
            if content[end] != "\n":
                end += 1
            elif after >= self.context[1]:
                break
            else:
                after += 1
                end += 1

        match_start = m.start() - start
        match_end = match_start + m.end() - m.start()
        return content[start:end], (match_start, match_end), (before, after)

    def __findall(self, file_content):
        for m in self.find_method(file_content):
            yield m

    def __findall_literal(self, file_content):
        """
        Literal find all.
        """

        start = 0
        offset = len(self.pattern)
        while True:
            start = file_content.find(self.pattern, start)
            if start == -1:
                return
            yield _FindRegion(start, start + offset)
            start += offset

    def __get_col(self, content, absolute_col, line_ending):
        col = 1
        for x in reversed(range(0, absolute_col)):
            if content[x] == line_ending:
                break
            col += 1
        return col

    def search(self, target, file_content, max_count=None):
        """
        Search target file or buffer returning a generator of results.
        """

        ending = LINE_ENDINGS.search(file_content)
        line_ending = "\n"
        if ending is not None:
            if ending.group(2):
                line_ending = "\r"

        results = {"name": target, "count": 0, "line_ending": line_ending, "results": []}

        for m in self.__findall(file_content.lower() if self.literal and self.ignorecase else file_content):
            if max_count != None:
                if max_count == 0:
                    break
                else:
                    max_count -= 1

            result = {
                "lineno": file_content.count(line_ending, 0, m.start()) + 1,
                "colno": self.__get_col(file_content, m.start(), line_ending)
            }
            result["lines"], result["match"], result["context_count"] = self.__get_lines(file_content, m)
            results["results"].append(result)
            results["count"] += 1

        return results


class _DirWalker(object):
    def __init__(
            self, directory, file_pattern, file_regex_match,
            folder_exclude, dir_regex_match, recursive,
            show_hidden, size, modified, created
        ):
        self.dir = directory
        self.size = size
        self.modified = modified
        self.created = created
        print(self.created)
        print(self.modified)
        self.file_pattern = file_pattern
        self.file_regex_match = file_regex_match
        self.dir_regex_match = dir_regex_match
        self.folder_exclude = folder_exclude
        self.recursive = recursive
        self.show_hidden = show_hidden
        self.files = []

    def __is_hidden(self, path):
        if not self.show_hidden:
            if _PLATFORM == "windows":
                attrs = ctypes.windll.kernel32.GetFileAttributesW(path)
                return attrs != -1 and bool(attrs & 2)
            elif _PLATFORM == "osx":
                f = basename(path)

                pool = Foundation.NSAutoreleasePool.alloc().init()
                hidden = (
                    (f.startswith('.') and f != "..") or
                    Foundation.NSURL.fileURLWithPath_(path).getResourceValue_forKey_error_(
                        None, Foundation.NSURLIsHiddenKey, None
                    )[1]
                )
                del pool
            else:
                return f.startswith('.') and f != ".."
        return False

    def __compare_value(self, limit_check, current):
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
        times_okay = False
        mod_okay = False
        cre_okay = False
        self.modified_time = getmtime(pth)
        self.created_time = getctime(pth)
        if self.modified is None:
            mod_okay = True
        else:
            print(pth)
            print(self.modified, self.modified_time)
            mod_okay = self.__compare_value(self.modified, self.modified_time)
        if self.created is None:
            cre_okay = True
        else:
            cre_okay = self.__compare_value(self.created, self.created_time)
        if mod_okay and cre_okay:
            times_okay = True
        return times_okay

    def __is_size_okay(self, pth):
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

        valid = False
        if self.file_pattern != None and not self.__is_hidden(join(base, name)):
            if self.file_regex_match:
                valid = True if self.file_pattern.match(name) != None else False
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
        return valid

    def __valid_folder(self, base, name):
        """
        Returns whether a folder can be searched.
        """

        valid = True
        if not self.recursive:
            valid = False
        elif self.__is_hidden(join(base, name)):
            valid = False
        elif self.folder_exclude != None:
            if self.dir_regex_match:
                valid = False if self.folder_exclude.match(name) != None else True
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
        return valid

    def run(self):
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
        modified=None, created=None, text=False
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

        self.search = _FileSearch(pattern, flags, context)
        self.buffer_input = bool(flags & BUFFER_INPUT)
        self.all_utf8 = all_utf8
        self.current_encoding = None
        self.idx = -1
        self.target = abspath(target) if not self.buffer_input else target
        self.max = max_count
        self.process_binary = text
        file_regex_match = bool(flags & FILE_REGEX_MATCH)
        dir_regex_match = bool(flags & DIR_REGEX_MATCH)
        self.kill = False
        self.thread = None
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
        pattern = None
        if folder_exclude != None:
            pattern = ure.compile(folder_exclude, ure.IGNORECASE) if dir_regex_match else [f.lower() for f in folder_exclude.split("|")]
        return pattern

    def __get_file_pattern(self, file_pattern, file_regex_match):
        pattern = None
        if file_pattern != None:
            pattern = ure.compile(file_pattern, ure.IGNORECASE) if file_regex_match else [f.lower() for f in file_pattern.split("|")]
        return pattern

    def __decode_file(self, filename):
        bfr, self.current_encoding = text_decode.decode(filename)
        return bfr

    def __read_file(self, file_name):
        # Force UTF for all
        if self.all_utf8:
            try:
                self.current_encoding = "UTF8"
                with codecs.open(file_name, encoding="utf-8-sig", errors="replace") as f:
                    content = f.read()
                    return content
            except:
                # print(str(traceback.format_exc()))
                pass
            return None

        # Non-Lazy decoding
        # try:
        #     return self.__decode_file(file_name)
        # except Exception:
        #     print(str(traceback.format_exc()))
        #     pass
        # Lazy decoding
        encodings = [
            "ascii",
            "utf-8-sig",
            "utf-16",
            "latin-1"
        ]
        encodings_map = {
            0: "ASCII",
            1: "UTF8",
            2: "UTF16",
            3: "LATIN-1"
        }
        content = None
        try:
            with open(file_name, "rb") as f:
                content = f.read()
                count = 0
                for encode in encodings:
                    self.current_encoding = encodings_map[count]
                    try:
                        return unicode(content, encode)
                    except:
                        # print(str(traceback.format_exc()))
                        self.current_encoding = "BIN"
                        pass
                    count += 1

        except Exception:
            # print(str(traceback.format_exc()))
            pass
        if not self.process_binary:
            content = None
        # Unknown encoding, maybe binary, something else?
        return content

    def get_status(self):
        if self.thread is not None:
            return self.idx + 1 if self.idx != -1 else 0, len(_FILES)
        else:
            return 1, 1

    def abort(self):
        global _ABORT
        with _LOCK:
            _ABORT = True
        self.kill = True

    def find(self):
        """
        Walks through a given directory searching files via the provided pattern.
        If given a file directly, it will search the file only.
        Return the results of each file via a generator.
        """
        global _STARTED
        max_count = int(self.max) if self.max != None else None

        if self.thread is not None:
            self.idx = -1
            self.thread.start()
            done = False
            # Try to wait in case the
            # "is running" check happens too quick
            while not _STARTED:
                sleep(0.3)
            with _LOCK:
                _STARTED = False

            while not done:
                file_info = None
                while file_info is None:
                    if _RUNNING:
                        if len(_FILES) - 1 > self.idx:
                            self.idx += 1
                            file_info = _FILES[self.idx]
                        else:
                            sleep(0.3)
                    else:
                        if len(_FILES) - 1 > self.idx and not self.kill:
                            self.idx += 1
                            file_info = _FILES[self.idx]
                        elif self.kill:
                            break
                        else:
                            done = True
                            break

                if file_info is None:
                    done = True
                else:
                    file_name = file_info[0]
                    sz = file_info[1]
                    content = self.__read_file(file_name)
                    if content == None:
                        continue
                    result = self.search.search(file_name, content, max_count)
                    result["size"] = '%.2fKB' % (float(sz) / 1024.0)
                    result["encode"] = self.current_encoding
                    result["m_time"] = file_info[2]
                    result["c_time"] = file_info[3]
                    yield result
                    if max_count != None:
                        max_count -= result["count"]
                        if max_count == 0:
                            done = True
        elif self.buffer_input:
            # Perform search
            result = self.search.search("buffer input", self.target, max_count)
            result["size"] = "--KB"
            result["encode"] = "--"
            yield result
        else:
            # Perform search
            file_name = self.target
            content = self.__read_file(file_name)
            if content != None:
                result = self.search.search(file_name, content, max_count)
                result["size"] = "%.2fKB" % (float(getsize(file_name)) / 1024.0)
                result["encode"] = self.current_encoding
                yield result
