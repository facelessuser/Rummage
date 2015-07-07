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
import argparse
import os
import sys
from rummage import rumcore
from rummage import version

BOOL_NONE = 0
BOOL_MATCH = 1
BOOL_UNMATCH = 2


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
            context = (int(args.context), int(args.context))
        else:
            if args.before_context is None:
                before = 0
            if args.after_context is None:
                after = 0
            context = (int(before), int(after))

        if args.regexfilepattern is not None:
            filepattern = args.regexfilepattern
        elif args.filepattern is not None:
            filepattern = args.filepattern
        else:
            filepattern = None

        self.rummage = rumcore.Rummage(
            target=target,
            pattern=args.pattern,
            file_pattern=filepattern,
            folder_exclude=args.directory_exclude,
            context=context,
            max_count=int(args.max_count) if args.max_count is not None else None,
            flags=self.get_flags(args),
            boolean=args.files_with_matches or args.files_without_match,
            show_hidden=args.show_hidden,
            truncate_lines=False,
            backup=True,
            replace=args.substitute
        )

        if args.substitute:
            self.bool_match = BOOL_NONE
        elif args.files_with_matches:
            self.bool_match = BOOL_MATCH
        elif args.files_without_match:
            self.bool_match = BOOL_UNMATCH
        else:
            self.bool_match = BOOL_NONE

        self.no_filename = args.buffer or args.no_filename
        self.count_only = args.count or args.substitute is not None
        self.show_lines = args.line_number
        self.only_matching = args.only_matching

        self.current_file = None
        self.count = 0
        self.errors = False

    def get_flags(self, args):
        """Get rummage flags."""

        flags = 0

        if args.regexfilepattern is not None:
            flags |= rumcore.FILE_REGEX_MATCH

        if not args.regexp:
            flags |= rumcore.LITERAL
        elif args.dotall:
            flags |= rumcore.DOTALL

        if args.ignore_case:
            flags |= rumcore.IGNORECASE

        if args.buffer:
            flags |= rumcore.BUFFER_INPUT
        elif args.recursive:
            flags |= rumcore.RECURSIVE

        return flags

    def count_lines(self, string, nl):
        """Count lines of context."""

        return string.count(nl) + (1 if string[-1] != nl else 0)

    def display_match(self, file_name, lineno, line, separator):
        """Display the match."""

        if self.no_filename:
            print("%s%s%s" % (separator, ("%d" % lineno) + separator if self.show_lines else "", line))
        else:
            print("%s%s%s%s" % (file_name, separator, ("%d" % lineno) + separator if self.show_lines else "", line))

    def normal_output(self, f):
        """Normal output."""

        if f.match is not None:
            lineno = f.match.lineno - f.match.context[0]
            line_printed = False
            count = 0
            start_match = f.match.context[0]
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
                print("---")

    def match_output(self, f):
        """Match output."""

        if f.match is not None:
            lineno = f.match.lineno
            content = f.match.lines[f.match.match[0]:f.match.match[1]]
            for line in content.split(f.match.ending):
                self.display_match(f.info.name, lineno, line, ":")
                lineno += 1
            if lineno - f.match.lineno > 1:
                print("---")

    def bool_output(self, f):
        """
        Show only file name.

        Can show files that have a match or file that don't.
        """

        if self.bool_match == BOOL_UNMATCH and f.match is None:
            print(f.info.name)
        elif self.bool_match == BOOL_MATCH and f.match is not None:
            print(f.info.name)

    def count_output(self, f):
        """Output for showing only the count."""

        if f.match is not None:
            if not self.no_filename and self.current_file is None:
                self.current_file = f.info.name
                self.count = 1
            elif self.no_filename or self.current_file == f.info.name:
                self.count += 1
            else:
                print("%s:%d" % (self.current_file, self.count))
                self.current_file = f.info.name
                self.count = 1
        elif self.count:
            print("%s:%d" % (self.current_file, self.count))
            self.current_file = None
            self.count = 0

    def count_flush(self):
        """Flush remaining count entries."""

        if self.count:
            if self.no_filename:
                self.current_file = ""
            print("%s:%d" % (self.current_file, self.count))
            self.current_file = None
            self.count = 0

    def display_output(self):
        """Display output."""

        for f in self.rummage.find():
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
                print("ERROR: %s" % f.error)
        self.count_flush()


def cli_main():
    """Main entry point."""

    # Setup arg parsing object
    parser = argparse.ArgumentParser(prog="rumcl", description="Grep like file searcher.", add_help=False)
    # Flag arguments
    parser.add_argument(
        "--version", action="version", version=("%(prog)s " + version.__version__)
    )
    parser.add_argument(
        "--help", action="help",
        help="Show this help message and exit."
    )
    parser.add_argument(
        "--regexp", "-e", action="store_true", default=False,
        help="Pattern is a regular expression."
    )
    parser.add_argument(
        "--ignore_case", "-i", action="store_true", default=False,
        help="Ignore case when performing search."
    )
    parser.add_argument(
        "--dotall", "-d", action="store_true", default=False,
        help="Make the '.' special character in regex match any character at all, including a newline."
    )
    parser.add_argument(
        "--recursive", "-r", action="store_true", default=False,
        help="Recursively search a directory tree."
    )
    parser.add_argument(
        "--line_number", "-n", action="store_true", default=False,
        help="Show line numbers."
    )
    parser.add_argument(
        "--files_without_match", "-L", action="store_true", default=False,
        help='''
            Suppress normal output; instead print the name of each input
            file from which no output would normally have been printed.
            The scanning will stop on the first match.
        '''
    )
    parser.add_argument(
        "--files_with_matches", "-l", action="store_true", default=False,
        help='''
            Suppress normal output; instead print the name of each input
            file from which output would normally have been printed
            The scanning will stop on the first match.
        '''
    )
    parser.add_argument(
        "--only_matching", "-o", action="store_true", default=False,
        help="Print number lines of trailing context."
    )
    parser.add_argument(
        "--count", "-c", action="store_true", default=False,
        help="Only show the match count in each file."
    )
    parser.add_argument(
        "--buffer", "-b", action="store_true", default=False,
        help="Parse input parameter as a string buffer."
    )
    parser.add_argument(
        "--no_filename", "-h", action="store_true", default=False,
        help="Hide file name in output."
    )
    parser.add_argument(
        "--directory_exclude", "-D", metavar="PATTERN", default=None,
        help="Regex describing directory path(s) to exclude"
    )
    parser.add_argument(
        "--max_count", "-m", metavar="NUM", default=None,
        help="Max matches to find."
    )
    parser.add_argument(
        "--after_context", "-A", metavar="NUM", default=None,
        help="Print number lines of leading context."
    )
    parser.add_argument(
        "--before_context", "-B", metavar="NUM", default=None,
        help="Print number lines of trailing context."
    )
    parser.add_argument(
        "--context", "-C", metavar="NUM", default=None,
        help="Print number lines of context before and after."
    )
    parser.add_argument(
        "--regexfilepattern", "-F", metavar="PATTERN", default=None,
        help="Regex file pattern to search."
    )
    parser.add_argument(
        "--filepattern", "-f", metavar="PATTERN", default="*",
        help="File pattern to search."
    )
    parser.add_argument(
        "--show_hidden", "-H", action="store_true", default=False,
        help="Show hidden files."
    )

    parser.add_argument(
        "--substitute", "-s", metavar="PATTERN", default=None,
        help="Replace find with the specified pattern."
    )

    # Positional arguments (must follow flag arguments)
    parser.add_argument(
        "pattern", default=None,
        help="Search pattern"
    )

    parser.add_argument(
        "target", default=None,
        help="File, directory, or string buffer to search."
    )

    rumcl = RummageCli(parser.parse_args())
    rumcl.display_output()

    return rumcl.errors


if __name__ == "__main__":
    sys.exit(cli_main())
