'''
pygrep

Licensed under MIT
Copyright (c) 2011 Isaac Muse <isaacmuse@gmail.com>
https://gist.github.com/facelessuser/5757669

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import ure
from os import walk
from fnmatch import fnmatch
from os.path import isdir, join, abspath, basename, getsize
import codecs
import threading
import sys
from time import sleep

LITERAL = 1
IGNORECASE = 2
DOTALL = 4
RECURSIVE = 8
FILE_REGEX_MATCH = 16
BUFFER_INPUT = 32

_FILES = []
_RUNNING = False
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


def threaded_walker(directory, file_pattern, file_regex_match, folder_exclude, recursive, show_hidden, size):
    global _RUNNING
    _RUNNING = True
    walker = _DirWalker(directory, file_pattern, file_regex_match, folder_exclude, recursive, show_hidden, size)
    walker.run()
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
        self.pattern = pattern if self.literal else _re_pattern(pattern, self.ignorecase, self.dotall)
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

    def search(self, target, file_content, max_count=None):
        """
        Search target file or buffer returning a generator of results.
        """

        results = {"name": target, "count": 0, "results": []}

        for m in self.__findall(file_content.lower() if self.literal and self.ignorecase else file_content):
            if max_count != None:
                if max_count == 0:
                    break
                else:
                    max_count -= 1
            result = {
                "lineno": file_content.count("\n", 0, m.start()) + 1
            }
            result["lines"], result["match"], result["context_count"] = self.__get_lines(file_content, m)
            results["results"].append(result)
            results["count"] += 1

        return results


class _DirWalker(object):
    def __init__(self, directory, file_pattern, file_regex_match, folder_exclude, recursive, show_hidden, size):
        self.dir = directory
        self.size = size
        self.file_pattern = file_pattern
        self.file_regex_match = file_regex_match
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

    def __is_size_okay(self, pth):
        size_okay = False
        self.current_size = getsize(pth)
        if self.size is None:
            size_okay = True
        else:
            qualifier = self.size[0]
            limit = self.size[1]
            if qualifier == "eq":
                if self.current_size == limit:
                    size_okay = True
            elif qualifier == "lt":
                if self.current_size < limit:
                    size_okay = True
            elif qualifier == "gt":
                if self.current_size > limit:
                    size_okay = True
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
                    if fnmatch(name.lower(), p[1:]):
                        exclude = True
                    elif fnmatch(name.lower(), p):
                        matched = True
                if exclude:
                    valid = False
                elif matched:
                    valid = True
            if valid:
                valid = self.__is_size_okay(join(base, name))
        return valid

    def __valid_folder(self, folder):
        """
        Returns whether a folder can be searched.
        """

        return not self.__is_hidden(folder) and not (self.folder_exclude != None and self.folder_exclude.match(folder)) and self.recursive

    def run(self):
        global _FILES
        global _ABORT
        _FILES = []
        for base, dirs, files in walk(self.dir):
            # Remove child folders based on exclude rules
            [dirs.remove(name) for name in dirs[:] if not self.__valid_folder(join(base, name))]

            # Seach files if they were found
            if len(files):
                # Only search files in that are in the inlcude rules
                for f in [(name, self.current_size) for name in files[:] if self.__valid_file(base, name)]:
                    _FILES.append((join(base, f[0]), f[1]))
                    if _ABORT:
                        break
            if _ABORT:
                _ABORT = False
                break


class Grep(object):
    def __init__(
        self, target, pattern, file_pattern=None, folder_exclude=None,
        flags=0, context=(0, 0), max_count=None,
        show_hidden=False, all_utf8=False, size=None
    ):
        """
        Initialize Grep object.
        """

        global _RUNNING
        global _ABORT
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
        file_regex_match = bool(flags & FILE_REGEX_MATCH)
        self.kill = False
        self.thread = None
        if not self.buffer_input and isdir(self.target):
            self.thread = threading.Thread(
                target=threaded_walker,
                args=(
                    self.target,
                    self.__get_file_pattern(file_pattern, file_regex_match),
                    file_regex_match,
                    folder_exclude if folder_exclude == None else ure.compile(folder_exclude, ure.IGNORECASE | ure.UNICODE),
                    bool(flags & RECURSIVE),
                    show_hidden,
                    size
                )
            )
            self.thread.setDaemon(True)

    def __get_file_pattern(self, file_pattern, file_regex_match):
        pattern = None
        if file_pattern != None:
            pattern = ure.compile(file_pattern, ure.IGNORECASE | ure.UNICODE) if file_regex_match else [f.lower() for f in file_pattern.split("|")]
        else:
            pattern = file_pattern
        return pattern

    def __read_file(self, file_name):
        encodings = ["ascii", "utf-8"] if not self.all_utf8 else ["utf-8"]
        for encode in encodings:
            try:
                with codecs.open(file_name, encoding=encode) as f:
                    self.current_encoding = encode
                    return f.read()
            except:
                pass
        # Unknown encoding, maybe binary, something else?
        return None

    def get_status(self):
        if self.thread is not None:
            return self.idx + 1 if self.idx != -1 else 0, len(_FILES)
        else:
            return 1, 1

    def abort(self):
        global _ABORT
        _ABORT = True
        self.kill = True

    def find(self):
        """
        Walks through a given directory searching files via the provided pattern.
        If given a file directly, it will search the file only.
        Return the results of each file via a generator.
        """

        max_count = int(self.max) if self.max != None else None

        if self.thread is not None:
            self.idx = -1
            self.thread.start()
            done = False
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
