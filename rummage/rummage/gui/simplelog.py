"""
Simple Log.

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
import threading
from .. import util

ALL = 0
DEBUG = 10
INFO = 20
WARNING = 30
ERROR = 40
CRITICAL = 50

global_log = None


class Log(object):
    """Log."""

    def __init__(self, filename=None, fmt="%(message)s", level=ERROR, filemode="w"):
        """Init Log object."""

        self._lock = threading.Lock()
        if filemode == "w":
            with codecs.open(filename, "w", "utf-8") as f:
                f.write("")
        self.filename = filename
        self.level = level
        self.format = fmt
        self.save_to_file = self.filename is not None
        self.echo = not self.save_to_file

    def set_echo(self, enable):
        """Turn on/off echoing to std out."""

        with self._lock:
            if self.save_to_file:
                self.echo = bool(enable)

    def set_level(self, level):
        """Set log level."""

        with self._lock:
            self.level = int(level)

    def get_level(self):
        """Get log level."""

        return self.level

    def formatter(self, lvl, log_fmt, msg, msg_fmt=None):
        """Special formatters for log message."""

        return log_fmt % {
            "loglevel": lvl,
            "message": util.to_ustr(msg if msg_fmt is None else msg_fmt(msg))
        }

    def debug(self, msg, log_fmt="%(loglevel)s: %(message)s\n", echo=True, msg_fmt=None):
        """Debug level logging."""

        if self.level <= DEBUG:
            self._log(self.formatter("DEBUG", log_fmt, msg, msg_fmt), echo)

    def info(self, msg, log_fmt="%(loglevel)s: %(message)s\n", echo=True, msg_fmt=None):
        """Info level logging."""

        if self.level <= INFO:
            self._log(self.formatter("INFO", log_fmt, msg, msg_fmt), echo)

    def warning(self, msg, log_fmt="%(loglevel)s: %(message)s\n", echo=True, msg_fmt=None):
        """Warning level logging."""

        if self.level <= WARNING:
            self._log(self.formatter("WARNING", log_fmt, msg, msg_fmt), echo)

    def error(self, msg, log_fmt="%(loglevel)s: %(message)s\n", echo=True, msg_fmt=None):
        """Error level logging."""

        if self.level <= ERROR:
            self._log(self.formatter("ERROR", log_fmt, msg, msg_fmt), echo)

    def critical(self, msg, log_fmt="%(loglevel)s: %(message)s\n", echo=True, msg_fmt=None):
        """Critical level logging."""

        if self.level <= CRITICAL:
            self._log(self.formater("CRITICAL", log_fmt, msg, msg_fmt), echo)

    def _log(self, msg, echo=True):
        """Base logger."""

        if not (echo and self.echo) and self.save_to_file:
            with self._lock:
                with codecs.open(self.filename, "a", "utf-8") as f:
                    f.write(self.format % {"message": msg})
        if echo and self.echo:
            print(self.format % {"message": msg})

    def read(self):
        """Read the log."""

        txt = ""
        with self._lock:
            try:
                with codecs.open(self.filename, "r", "utf-8") as f:
                    txt = f.read()
            except Exception:
                pass
        return txt


def init_global_log(file_name, level=ERROR):
    """Initialize a global log object."""

    global global_log
    global_log = Log(file_name, level=level)


def get_global_log():
    """Get the global log object."""

    return global_log
