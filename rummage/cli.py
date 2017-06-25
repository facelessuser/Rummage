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
import re
import sys
from datetime import datetime
from .rummage import epoch_timestamp
from .rummage import rumcore
from .rummage import util
from .rummage import __meta__
from backrefs import bre, bregex
import decimal

CLI_ENCODING = sys.getfilesystemencoding()

BOOL_NONE = 0
BOOL_MATCH = 1
BOOL_UNMATCH = 2

RE_DATE_TIME = re.compile(
    r'''(?x)
    (?P<symbol>[><])?(?:
        (?P<date>(?P<month>0[1-9]|1[0-2])/(?P<day>0[1-9]|[1-2][0-9]|3[0-1])/(?P<year>[0-9]{4})) |
        (?P<time>(?P<hour>[0][1-9]|1[0-9]|2[0-3]):(?P<min>[0-5][0-9]|60):(?P<sec>[0-5][0-9]|60))
    )$
    '''
)

RE_DATE_TIME_FULL = re.compile(
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

    return value.decode(CLI_ENCODING) if isinstance(value, util.bstr) else value


class RummageCli(object):
    """Rummage command line frontend."""

    def __init__(self, args, is_buffer):
        """Initialize."""

        self.current_file = None
        self.count = 0
        self.errors = False

        # Parse search inputs
        target = self.parse_target(args, is_buffer)
        context = self.parse_context(args)
        file_pattern = self.parse_file_pattern(args)
        directory_exclude = self.parse_directory_exclude(args)
        size = self.parse_size_limit(args)
        created = self.parse_created(args)
        modified = self.parse_modified(args)
        flags = self.get_flags(args, is_buffer)
        regex_mode = self.get_regex_mode(args)
        self.validate_patterns(args, flags, regex_mode)

        # Parse the rest of the inputs and set associated variables
        if args.replace:
            self.bool_match = BOOL_NONE
        elif args.files_with_matches:
            self.bool_match = BOOL_MATCH
        elif args.files_without_match:
            self.bool_match = BOOL_UNMATCH
        else:
            self.bool_match = BOOL_NONE

        self.search_files = not args.search and not args.replace
        self.no_filename = is_buffer or args.no_filename
        self.count_only = args.count or args.replace is not None
        self.show_lines = args.line_numbers
        self.only_matching = args.only_matching

        self.rummage = rumcore.Rummage(
            target=target,
            pattern=args.search,
            file_pattern=file_pattern,
            folder_exclude=directory_exclude,
            context=context,
            max_count=int(args.max_count) if args.max_count is not None else None,
            flags=flags,
            encoding=args.encoding,
            size=size,
            created=created,
            modified=modified,
            replace=args.replace,
            regex_mode=regex_mode
        )

    def parse_target(self, args, is_buffer):
        """Parse target."""

        if not is_buffer:
            if os.path.exists(args.target):
                target = args.target
            else:
                raise ValueError("%s does not exist" % args.target)
        else:
            target = args.target
        return target

    def parse_context(self, args):
        """Parse context flag."""

        if args.context is not None:
            try:
                before, after = args.context.split(',')
                context = (int(before), int(after))
            except Exception:
                raise ValueError("Context should be two numbers separated by a comma")
        else:
            context = (0, 0)
        return context

    def parse_file_pattern(self, args):
        """Parse file pattern."""

        if args.regex_file_pattern is not None:
            file_pattern = args.regex_file_pattern
        elif args.file_pattern is not None:
            file_pattern = args.file_pattern
        else:
            file_pattern = None
        return file_pattern

    def parse_directory_exclude(self, args):
        """Parse directory exclude."""

        if args.regex_directory_exclude is not None:
            directory_exclude = args.regex_directory_exclude
        elif args.directory_exclude is not None:
            directory_exclude = args.directory_exclude
        else:
            directory_exclude = None
        return directory_exclude

    def parse_size_limit(self, args):
        """Parse size limit."""

        if args.size_limit is not None:
            try:
                assert args.size_limit.startswith(('<', '>', '=')), "No comparison operator"
                size_limit = round(decimal.Decimal(args.size_limit[1:]) * decimal.Decimal(1024))
                if args.size_limit.startswith('<'):
                    size = ('lt', size_limit)
                elif args.size_limit.startswith('>'):
                    size = ('gt', size_limit)
                else:
                    size = ('eq', size_limit)
            except Exception:
                raise ValueError("Size should be in KB in the form: =1000.0, <1000.0, or >1000.0")
        else:
            size = None
        return size

    def parse_created(self, args):
        """Parse created."""

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
        return created

    def parse_modified(self, args):
        """Parse modified."""

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
        return modified

    def get_regex_mode(self, args):
        """Get the regex mode."""

        if args.regex0 or args.regex1:
            if args.backrefs:
                regex_mode = rumcore.BREGEX_MODE
            else:
                regex_mode = rumcore.REGEX_MODE
        elif args.backrefs:
            regex_mode = rumcore.BRE_MODE
        else:
            regex_mode = rumcore.RE_MODE
        return regex_mode

    def validate_patterns(self, args, flags, regex_mode):
        """Validate inputs."""

        if args.re or args.regex0 or args.regex1:
            if (
                (args.search == "" and args.replace) or
                self.validate_search_regex(args.search, flags, regex_mode)
            ):
                raise ValueError("Invlaid regex search pattern")

        elif args.search == "" and args.replace:
            raise ValueError("Invlaid search pattern")

        if args.regex_file_pattern:
            if self.validate_regex(args.regex_file_pattern, 0, regex_mode):
                raise ValueError("Invalid regex file pattern")
        elif not args.file_pattern:
            raise ValueError("Invalid file pattern")

        if args.regex_directory_exclude:
            if self.validate_regex(args.regex_directory_exclude, 0, regex_mode):
                raise ValueError("Invalid regex directory exclude pattern")

    def validate_search_regex(self, search, search_flags, regex_mode):
        """Validate search regex."""

        if regex_mode in rumcore.REGEX_MODES:
            # bregex just wraps regex's flags as it uses
            # regex so we will use bregex flags for both regex and bregex
            flags = bregex.MULTILINE
            if search_flags & rumcore.VERSION1:
                flags |= bregex.VERSION1
            else:
                flags |= bregex.VERSION0
                if flags & rumcore.FULLCASE:
                    flags |= bregex.FULLCASE
            if search_flags & rumcore.DOTALL:
                flags |= bregex.DOTALL
            if not search_flags & rumcore.IGNORECASE:
                flags |= bregex.IGNORECASE
            if search_flags & rumcore.UNICODE:
                flags |= bregex.UNICODE
            else:
                flags |= bregex.ASCII
            if search_flags & rumcore.BESTMATCH:
                flags |= bregex.BESTMATCH
            if search_flags & rumcore.ENHANCEMATCH:
                flags |= bregex.ENHANCEMATCH
            if search_flags & rumcore.WORD:
                flags |= bregex.WORD
            if search_flags & rumcore.REVERSE:
                flags |= bregex.REVERSE
            if search_flags & rumcore.POSIX:
                flags |= bregex.POSIX
        else:
            # bre just wraps re's flags as it uses
            # re so we will use bre flags for both re and bre
            flags = re.MULTILINE
            if search_flags & rumcore.DOTALL:
                flags |= bre.DOTALL
            if search_flags & rumcore.IGNORECASE:
                flags |= bre.IGNORECASE
            if search_flags & rumcore.UNICODE:
                flags |= bre.UNICODE

        return self.validate_regex(search, flags, regex_mode)

    def validate_regex(self, pattern, flags=0, regex_mode=rumcore.RE_MODE):
        """Validate regular expresion compiling."""
        try:
            if regex_mode == rumcore.BREGEX_MODE:
                if flags == 0:
                    flags = bregex.ASCII
                bregex.compile_search(pattern, flags)
            elif regex_mode == rumcore.REGEX_MODE:
                import regex
                if flags == 0:
                    flags = regex.ASCII
                regex.compile(pattern, flags)
            elif regex_mode == rumcore.BRE_MODE:
                bre.compile_search(pattern, flags)
            else:
                re.compile(pattern, flags)
            return False
        except Exception:
            return True

    def get_flags(self, args, is_buffer):
        """Get rummage flags."""

        flags = rumcore.MULTILINE

        if args.regex_file_pattern is not None:
            flags |= rumcore.FILE_REGEX_MATCH

        if args.regex_directory_exclude is not None:
            flags |= rumcore.DIR_REGEX_MATCH

        if args.show_hidden:
            flags |= rumcore.SHOW_HIDDEN

        if args.process_binary:
            flags |= rumcore.PROCESS_BINARY

        if args.count:
            flags |= rumcore.COUNT_ONLY

        if args.files_with_matches or args.files_without_match:
            flags |= rumcore.BOOLEAN

        if args.backup:
            flags |= rumcore.BACKUP

        if args.truncate:
            flags |= rumcore.TRUNCATE_LINES

        if args.unicode:
            flags |= rumcore.UNICODE

        if not args.re and not args.regex0 and not args.regex1:
            flags |= rumcore.LITERAL
        elif args.dotall:
            flags |= rumcore.DOTALL

        if args.ignore_case:
            flags |= rumcore.IGNORECASE

        if is_buffer:
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
            if args.posix:
                flags |= rumcore.POSIX
            if args.format_replace:
                flags |= rumcore.FORMATREPLACE

        return flags

    def count_lines(self, string, nl):
        """Count lines of context."""

        return string.count(nl) + (1 if string[-1:] != nl else 0)

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
            if f.info.encoding in ('BIN'):
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
                    if hasattr(f, 'skipped') and f.skipped:
                        if self.bool_match == BOOL_UNMATCH:
                            pyout(f.name)
                    elif self.bool_match != BOOL_UNMATCH:
                        pyout(f.name)
                else:
                    self.errors = True
                    pyout("ERROR: %s" % "".join(f.error))
            else:
                if hasattr(f, 'skipped') and f.skipped:
                    pass
                elif not f.error:
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
                    pyout("ERROR: %s" % "".join(f.error))
        self.count_flush()


def get_file_stream():
    """Get the file stream."""

    import fileinput
    sys.argv = []
    text = []
    try:
        for line in fileinput.input():
            text.append(line)
    except Exception:
        import traceback
        pyout(traceback.format_exc())

    return b''.join(text) if text else b''


def get_stream(args):
    """Get file(s) or stream."""

    stream = False

    if not args.target:
        args.target = get_file_stream()
        stream = True
    else:
        args.target = args.target[0]
    return stream


def main():
    """Main entry point."""

    # Setup arg parsing object
    parser = argparse.ArgumentParser(
        prog="rumcl", description="Rummage CLI search and replace tool.", add_help=False
    )
    # Flag arguments
    parser.add_argument(
        "--version", action="version", version=("%(prog)s " + __meta__.__version__)
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
        help="Pattern is a regular expression for the Python 're'."
    )
    parser.add_argument(
        "--backrefs", "-b", action="store_true", default=False,
        help=(
            "Apply backrefs to regular expression. Will use the 're' module if --re is used or "
            "the 'regex' module if --regex0 or --regex1 is used."
        )
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
        "--posix", "-O", action="store_true", default=False,
        help="Use POSIX matching (regex module only)."
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
        "--format-replace", "-P", action="store_true", default=False,
        help="Use string format replacement groups in replace patterns: {group} (regex module only)."
    )
    parser.add_argument(
        "--replace", "-r", metavar="PATTERN", default=None, type=pyin,
        help="Replace find with the specified pattern."
    )
    parser.add_argument(
        "--backup", "-k", action="store_true", default=False,
        help="Backup original file when replacing."
    )

    # Search modes
    parser.add_argument(
        "--recursive", "-R", action="store_true", default=False,
        help="Recursively search a directory tree."
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
        help="File size limit in KB: equal to '-z 1000.0', less than '-z <1000.0', or greater than '-z >1000.0'"
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
        "--encoding", "-e", metavar="ENCODING", default=None, type=pyin,
        help=(
            "Do not detect encoding, but force the specified encoding. If piping a buffer, "
            "the buffer will be binary unless --encoding is passed in."
        )
    )

    # Positional arguments (must follow flag arguments)
    parser.add_argument(
        "--search", "-s", default="", type=pyin,
        help="Search pattern"
    )
    parser.add_argument(
        "target", default=[], type=pyin, nargs='?',
        help="File, directory, or string buffer to search."
    )

    args = parser.parse_args()

    is_buffer = get_stream(args)

    rumcl = RummageCli(args, is_buffer)
    rumcl.display_output()

    sys.exit(rumcl.errors)


if __name__ == "__main__":
    sys.exit(main())
