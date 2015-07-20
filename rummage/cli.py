"""
Rummage (cli).

Licensed under MIT
Copyright (c) 2011 - 2015 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
from __future__ import unicode_literals
from __future__ import absolute_import
import argparse
import os
import sys
from datetime import datetime
from .rummage import epoch_timestamp
from .rummage import rumcore
from .rummage import version
from .rummage.rumcore import backrefs as bre

PY3 = (3, 0) <= sys.version_info < (4, 0)
CLI_ENCODING = sys.getfilesystemencoding()

if PY3:
    binary_type = bytes  # noqa
else:
    binary_type = str  # noqa

BOOL_NONE = 0
BOOL_MATCH = 1
BOOL_UNMATCH = 2

RE_DATE_TIME = bre.compile_search(
    r'''(?x)
    (?P<symbol>[><])?(?:
        (?P<date>(?P<month>0[1-9]|1[0-2])/(?P<day>0[1-9]|[1-2][0-9]|3[0-1])/(?P<year>[0-9]{4})) |
        (?P<time>(?P<hour>[0][1-9]|1[0-9]|2[0-3]):(?P<min>[0-5][0-9]|60):(?P<sec>[0-5][0-9]|60))
    )$
    '''
)

RE_DATE_TIME_FULL = bre.compile_search(
    r'''(?x)
    (?P<symbol>[><])?
    (?P<date>(?P<month>0[1-9]|1[0-2])/(?P<day>0[1-9]|[1-2][0-9]|3[0-1])/(?P<year>[0-9]{4})) -
    (?P<time>(?P<hour>[0][1-9]|1[0-9]|2[0-3]):(?P<min>[0-5][0-9]|60):(?P<sec>[0-5][0-9]|60))
    $
    '''
)


def pyout(value):
    """Dump to stdout."""

    print(value.encode(CLI_ENCODING, errors='replace').decode(CLI_ENCODING))


def pyin(value):
    """Read in stdin variables."""

    return value.decode(CLI_ENCODING) if isinstance(value, binary_type) else value


class RummageCli(object):

    """Rummage command line frontend."""

    def __init__(self, args):
        """Initialize."""

        if not args.buffer:
            if os.path.exists(args.target):
                target = args.target
            else:
                raise ValueError("%s does not exist" % args.target)
        else:
            target = args.target

        if args.context is not None:
            try:
                before, after = args.context.split(',')
                context = (int(before), int(after))
            except Exception:
                raise ValueError("Context should be two numbers separated by a comma")
        else:
            context = (0, 0)

        if args.regex_file_pattern is not None:
            file_pattern = args.regex_file_pattern
        elif args.file_pattern is not None:
            file_pattern = args.file_pattern
        else:
            file_pattern = None

        if args.regex_directory_exclude is not None:
            directory_exclude = args.regex_directory_exclude
        elif args.directory_exclude is not None:
            directory_exclude = args.directory_exclude
        else:
            directory_exclude = None

        if args.size_limit is not None:
            try:
                if args.size_limit.startswith('<'):
                    size = ('lt', int(args.size_limit[1:]))
                elif args.size_limit.startswith('>'):
                    size = ('gt', int(args.size_limit[1:]))
                else:
                    size = ('eq', int(args.size_limit))
            except Exception:
                raise ValueError("Size should be in KB in the form: 1000, <1000, or >1000")
        else:
            size = None

        if args.created is not None:
            sym = 'eq'
            m = RE_DATE_TIME.match(args.created)
            if m is None:
                m = RE_DATE_TIME_FULL.match(args.created)
                if m is not None:
                    if m.group('symbol'):
                        sym = 'gt' if m.group('symbol') == '>' else 'lt'
                    date = m.group('date')
                    time = m.group('time')
            else:
                if m.group('symbol'):
                    sym = 'gt' if m.group('symbol') == '>' else 'lt'
                if m.group('date'):
                    date = m.group('date')
                    time = "00:00:00"
                elif m.group('time'):
                    time = m.group('time')
                    today = datetime.today()
                    date = "%02d/%02d/%04d" % (today.year, today.month, today.day)
            if m is None:
                raise ValueError("Time should be in the form: MM/DD/YYYY-HH:MM:SS (with optional < or > in front)")
            created = (sym, epoch_timestamp.local_time_to_epoch_timestamp(date, time))
        else:
            created = None

        if args.modified is not None:
            sym = 'eq'
            m = RE_DATE_TIME.match(args.modified)
            if m is None:
                m = RE_DATE_TIME_FULL.match(args.modified)
                if m is not None:
                    if m.group('symbol'):
                        sym = 'gt' if m.group('symbol') == '>' else 'lt'
                    date = m.group('date')
                    time = m.group('time')
            else:
                if m.group('symbol'):
                    sym = 'gt' if m.group('symbol') == '>' else 'lt'
                if m.group('date'):
                    date = m.group('date')
                    time = "00:00:00"
                elif m.group('time'):
                    time = m.group('time')
                    today = datetime.today()
                    date = "%02d/%02d/%04d" % (today.year, today.month, today.day)
            if m is None:
                raise ValueError("Time should be in the form: MM/DD/YYYY-HH:MM:SS (with optional < or > in front)")
            modified = (sym, rumcore.epoch_timestamp.local_time_to_epoch_timestamp(date, time))
        else:
            modified = None

        flags = self.get_flags(args)
        regex_module = args.regex0 or args.regex1
        if args.re or regex_module:
            if (
                (args.pattern == "" and args.replace) or
                self.validate_search_regex(args.pattern, flags)
            ):
                raise ValueError("Invlaid regex search pattern")

        elif args.pattern == "" and args.replace:
            raise ValueError("Invlaid search pattern")

        if args.regex_file_pattern:
            if self.validate_regex(args.regex_file_pattern, flags=0, regex_support=regex_module):
                raise ValueError("Invalid regex file pattern")
        elif not args.file_pattern:
            raise ValueError("Invalid file pattern")

        if args.regex_directory_exclude:
            if self.validate_regex(args.regex_directory_exclude, flags=0, regex_support=regex_module):
                raise ValueError("Invalid regex directory exclude pattern")

        self.rummage = rumcore.Rummage(
            target=target,
            pattern=args.pattern,
            file_pattern=file_pattern,
            folder_exclude=directory_exclude,
            context=context,
            max_count=int(args.max_count) if args.max_count is not None else None,
            flags=self.get_flags(args),
            boolean=args.files_with_matches or args.files_without_match,
            show_hidden=args.show_hidden,
            truncate_lines=args.truncate,
            encoding=args.encoding_force,
            backup=True,
            size=size,
            process_binary=args.process_binary,
            created=created,
            modified=modified,
            replace=args.replace,
            regex_support=regex_module
        )

        if args.replace:
            self.bool_match = BOOL_NONE
        elif args.files_with_matches:
            self.bool_match = BOOL_MATCH
        elif args.files_without_match:
            self.bool_match = BOOL_UNMATCH
        else:
            self.bool_match = BOOL_NONE

        self.search_files = not args.pattern and not args.replace
        self.no_filename = args.buffer or args.no_filename
        self.count_only = args.count or args.replace is not None
        self.show_lines = args.line_numbers
        self.only_matching = args.only_matching

        self.current_file = None
        self.count = 0
        self.errors = False

    def validate_search_regex(self, search, search_flags):
        """Validate search regex."""

        regex_support = False
        if search_flags & (rumcore.VERSION0 | rumcore.VERSION1):
            import regex

            regex_support = True
            flags = regex.MULTILINE
            if search_flags & rumcore.VERSION1:
                flags |= regex.VERSION1
            else:
                flags |= regex.VERSION0
                if flags & rumcore.FULLCASE:
                    flags |= regex.FULLCASE
            if search_flags & rumcore.DOTALL:
                flags |= regex.DOTALL
            if not search_flags & rumcore.IGNORECASE:
                flags |= regex.IGNORECASE
            if search_flags & rumcore.UNICODE:
                flags |= regex.UNICODE
            else:
                flags |= regex.ASCII
            if search_flags & rumcore.BESTMATCH:
                flags |= regex.BESTMATCH
            if search_flags & rumcore.ENHANCEMATCH:
                flags |= regex.ENHANCEMATCH
            if search_flags & rumcore.WORD:
                flags |= regex.WORD
            if search_flags & rumcore.REVERSE:
                flags |= regex.REVERSE
        else:
            flags = bre.MULTILINE
            if search_flags & rumcore.DOTALL:
                flags |= bre.DOTALL
            if search_flags & rumcore.IGNORECASE:
                flags |= bre.IGNORECASE
            if search_flags & rumcore.UNICODE:
                flags |= bre.UNICODE
        return self.validate_regex(search, flags, regex_support)

    def validate_regex(self, pattern, flags=0, regex_support=False):
        """Validate regular expresion compiling."""
        try:
            if regex_support:
                import regex
                if flags == 0:
                    flags = regex.ASCII
                regex.compile(pattern, flags)
            else:
                bre.compile_search(pattern, flags)
            return False
        except Exception:
            return True

    def get_flags(self, args):
        """Get rummage flags."""

        flags = rumcore.MULTILINE

        if args.regex_file_pattern is not None:
            flags |= rumcore.FILE_REGEX_MATCH

        if args.regex_directory_exclude is not None:
            flags |= rumcore.DIR_REGEX_MATCH

        if args.unicode:
            flags |= rumcore.UNICODE

        if not args.re and not args.regex0 and not args.regex1:
            flags |= rumcore.LITERAL
        elif args.dotall:
            flags |= rumcore.DOTALL

        if args.ignore_case:
            flags |= rumcore.IGNORECASE

        if args.buffer:
            flags |= rumcore.BUFFER_INPUT
        elif args.recursive:
            flags |= rumcore.RECURSIVE

        if args.regex0 or args.regex1:
            if args.regex1:
                flags |= rumcore.VERSION1
            else:
                flags |= rumcore.VERSION0
                if args.fullcase:
                    flags |= rumcore.FULLCASE
            if args.bestmatch:
                flags |= rumcore.BESTMATCH
            if args.enhancematch:
                flags |= rumcore.ENHANCEMATCH
            if args.word:
                flags |= rumcore.WORD
            if args.reverse:
                flags |= rumcore.REVERSE

        return flags

    def count_lines(self, string, nl):
        """Count lines of context."""

        return string.count(nl) + (1 if string[-1] != nl else 0)

    def display_match(self, file_name, lineno, line, separator):
        """Display the match."""

        if self.no_filename:
            pyout("%s%s" % (("%d" % lineno) + separator if self.show_lines else "", line))
        else:
            pyout("%s%s%s%s" % (file_name, separator, ("%d" % lineno) + separator if self.show_lines else "", line))

    def normal_output(self, f):
        """Normal output."""

        if f.match is not None:
            lineno = f.match.lineno - f.match.context[0]
            line_printed = False
            count = 0
            start_match = f.match.context[0]
            if f.info.encoding == 'BIN':
                self.display_match(f.info.name, f.match.lineno, f.match.lines, ':')
            else:
                end_match = self.count_lines(f.match.lines, f.match.ending) - f.match.context[1]
                for line in f.match.lines.split(f.match.ending):
                    if (not line_printed and count == start_match) or (line_printed and count < end_match):
                        self.display_match(f.info.name, lineno, line, ":")
                        line_printed = True
                    else:
                        self.display_match(f.info.name, lineno, line, "-")
                    count += 1
                    lineno += 1
                if lineno - f.match.lineno > 1:
                    pyout("---")

    def match_output(self, f):
        """Match output."""

        if f.match is not None:
            lineno = f.match.lineno
            content = f.match.lines[f.match.match[0]:f.match.match[1]]
            if f.info.encoding == "BIN":
                self.display_match(f.info.name, lineno, content, ":")
            else:
                for line in content.split(f.match.ending):
                    self.display_match(f.info.name, lineno, line, ":")
                    lineno += 1
                if lineno - f.match.lineno > 1:
                    pyout("---")

    def bool_output(self, f):
        """
        Show only file name.

        Can show files that have a match or file that don't.
        """

        if self.bool_match == BOOL_UNMATCH and f.match is None:
            pyout(f.info.name)
        elif self.bool_match == BOOL_MATCH and f.match is not None:
            pyout(f.info.name)

    def count_output(self, f):
        """Output for showing only the count."""

        if f.match is not None:
            if not self.no_filename and self.current_file is None:
                self.current_file = f.info.name
                self.count = 1
            elif self.no_filename or self.current_file == f.info.name:
                self.count += 1
            else:
                pyout("%s:%d" % (self.current_file, self.count))
                self.current_file = f.info.name
                self.count = 1
        elif self.count:
            pyout("%s:%d" % (self.current_file, self.count))
            self.current_file = None
            self.count = 0

    def count_flush(self):
        """Flush remaining count entries."""

        if self.count:
            if self.no_filename:
                self.current_file = ""
            pyout("%s:%d" % (self.current_file, self.count))
            self.current_file = None
            self.count = 0

    def display_output(self):
        """Display output."""

        for f in self.rummage.find():
            if self.search_files:
                if not f.error:
                    pyout(f.name)
                else:
                    self.errors = True
                    pyout("ERROR: %s" % f.error)
            else:
                if not f.error:
                    if self.bool_match != BOOL_NONE:
                        self.bool_output(f)
                    elif self.count_only:
                        self.count_output(f)
                    elif self.only_matching:
                        self.match_output(f)
                    else:
                        self.normal_output(f)
                else:
                    self.errors = True
                    pyout("ERROR: %s" % f.error)
        self.count_flush()


def main():
    """Main entry point."""

    # Setup arg parsing object
    parser = argparse.ArgumentParser(prog="rumcl", description="Rummage CLI search and replace tool.", add_help=False)
    # Flag arguments
    parser.add_argument(
        "--version", action="version", version=("%(prog)s " + version.__version__)
    )
    parser.add_argument(
        "--help", action="help",
        help="Show this help message and exit."
    )

    # Result adjustments
    result_group = parser.add_mutually_exclusive_group()
    result_group.add_argument(
        "--files-without-match", "-W", action="store_true", default=False,
        help='''
            Suppress normal output; instead print the name of each input
            file from which no output would normally have been printed.
            The scanning will stop on the first match.
        '''
    )
    result_group.add_argument(
        "--files-with-matches", "-w", action="store_true", default=False,
        help='''
            Suppress normal output; instead print the name of each input
            file from which output would normally have been printed
            The scanning will stop on the first match.
        '''
    )
    result_group.add_argument(
        "--count", "-c", action="store_true", default=False,
        help="Only show the match count in each file."
    )
    result_group.add_argument(
        "--only-matching", "-o", action="store_true", default=False,
        help="Only show the match; no context."
    )
    parser.add_argument(
        "--max-count", "-m", metavar="NUM", default=None, type=pyin,
        help="Max matches to find."
    )
    parser.add_argument(
        "--line-numbers", "-n", action="store_true", default=False,
        help="Show line numbers."
    )

    # Search and replace
    parser.add_argument(
        "--re", "-x", action="store_true", default=False,
        help="Pattern is a regular expresiion for the Python 're'."
    )
    parser.add_argument(
        "--regex0", "-0", action="store_true", default=False,
        help="Pattern is a regular expression for the Python 'regex' module (ver 0) instead of 're'."
    )
    parser.add_argument(
        "--regex1", "-1", action="store_true", default=False,
        help="Pattern is a regular expression for the Python 'regex' module (ver 1) instead of 're'."
    )
    parser.add_argument(
        "--ignore-case", "-i", action="store_true", default=False,
        help="Ignore case when performing search."
    )
    parser.add_argument(
        "--fullcase", "-I", action="store_true", default=False,
        help="Use fullcase (regex module only)."
    )
    parser.add_argument(
        "--bestmatch", '-B', action="store_true", default=False,
        help="Best fuzzy match (regex module only)."
    )
    parser.add_argument(
        "--enhancematch", '-E', action="store_true", default=False,
        help="Attempt to improve fuzzy fit (regex module only)."
    )
    parser.add_argument(
        "--reverse", '-Z', action="store_true", default=False,
        help="Search backwards (regex module only)."
    )
    parser.add_argument(
        "--word", '-N', action="store_true", default=False,
        help="Use default Unicode word breaks (regex module only)."
    )
    parser.add_argument(
        "--dotall", "-a", action="store_true", default=False,
        help="Make the '.' special character in regex match any character at all, including a newline."
    )
    parser.add_argument(
        "--unicode", "-u", action="store_true", default=False,
        help=r"Use unicode properties for \w, \s, etc."
    )
    parser.add_argument(
        "--replace", "-r", metavar="PATTERN", default=None, type=pyin,
        help="Replace find with the specified pattern."
    )

    # Search modes
    search_mode_group = parser.add_mutually_exclusive_group()
    search_mode_group.add_argument(
        "--recursive", "-R", action="store_true", default=False,
        help="Recursively search a directory tree."
    )
    search_mode_group.add_argument(
        "--buffer", "-b", action="store_true", default=False,
        help="Parse input parameter as a string buffer."
    )

    # Limit search
    dir_pattern_group = parser.add_mutually_exclusive_group()
    dir_pattern_group.add_argument(
        "--regex-directory-exclude", "-D", metavar="PATTERN", default=None, type=pyin,
        help="Regex describing directory path(s) to exclude"
    )
    dir_pattern_group.add_argument(
        "--directory-exclude", "-d", metavar="PATTERN", default=None, type=pyin,
        help="File pattern describing directory path(s) to exclude"
    )
    file_pattern_group = parser.add_mutually_exclusive_group()
    file_pattern_group.add_argument(
        "--regex-file-pattern", "-F", metavar="PATTERN", default=None, type=pyin,
        help="Regex file pattern to search."
    )
    file_pattern_group.add_argument(
        "--file-pattern", "-f", metavar="PATTERN", default="*", type=pyin,
        help="File pattern to search."
    )
    parser.add_argument(
        "--size-limit", '-z', metavar="LIMIT", default=None, type=pyin,
        help="File size limit in KB: equal to '-z 1000', less than '-z <1000', or greater than '-z >1000'"
    )
    parser.add_argument(
        "--created", '-C', metavar="DATETIME", default=None, type=pyin,
        help=(
            "Date time that is either in the format: MM/DD/YYYY-HH:MM:SS.  If desired, date can be omitted, and "
            "'today' will be assumed.  If just the time is omitted, it will be replaced with '00:00:00'. "
            "Time will need to match will need to match to be searched.  If '<' or '>' is placed in front, "
            "time will need to be less than or greater than the respective time."
        )
    )
    parser.add_argument(
        "--modified", '-M', metavar="DATETIME", default=None, type=pyin,
        help=(
            "Date time that is either in the format: MM/DD/YYYY-HH:MM:SS.  If desired, date can be omitted, and "
            "'today' will be assumed.  If just the time is omitted, it will be replaced with '00:00:00'. "
            "Time will need to match will need to match to be searched.  If '<' or '>' is placed in front, "
            "time will need to be less than or greater than the respective time."
        )
    )

    # Context
    context_group = parser.add_mutually_exclusive_group()
    context_group.add_argument(
        "--context", "-T", metavar="NUM,NUM", default=None, type=pyin,
        help="Print number lines of context before and after. Before and after are separated by a comma: `-T 2,3` etc."
    )
    context_group.add_argument(
        "--truncate", "-t", action="store_true", default=False,
        help="Truncate the context result 120 chars and no additional context lines."
    )

    # Hide things
    parser.add_argument(
        "--no-filename", "-h", action="store_true", default=False,
        help="Hide file name in output."
    )

    parser.add_argument(
        "--show-hidden", "-H", action="store_true", default=False,
        help="Show hidden files."
    )

    # Binary
    parser.add_argument(
        "--process-binary", "-p", action="store_true", default=False,
        help="Process binary files (or files recognized as binary) and show thier results."
    )

    # Encoding
    parser.add_argument(
        "--encoding-force", "-e", metavar="ENCODING", default=None, type=pyin,
        help="Do not detect encoding, but force the specified encoding."
    )

    # Positional arguments (must follow flag arguments)
    parser.add_argument(
        "pattern", default=None, type=pyin,
        help="Search pattern"
    )
    parser.add_argument(
        "target", default=None, type=pyin,
        help="File, directory, or string buffer to search."
    )

    rumcl = RummageCli(parser.parse_args())
    rumcl.display_output()

    sys.exit(rumcl.errors)


if __name__ == "__main__":
    sys.exit(main())
