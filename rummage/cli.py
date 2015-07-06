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
from rummage import rumcore
import sys
__VERSION__ = "1.0.0"


def count_lines(string, nl):
    """Count lines of context."""

    return string.count(nl) + (1 if string[-1] != nl else 0)


def display_match(file_name, lineno, line, no_filename, show_lines, separator):
    """Display the match."""

    if no_filename:
        print("%s%s%s" % (separator, ("%d" % lineno) + separator if show_lines else "", line))
    else:
        print("%s%s%s%s" % (file_name, separator, ("%d" % lineno) + separator if show_lines else "", line))


def normal_output(f, no_filename, show_lines):
    """Normal output."""

    if f.match is not None:
        # for r in f["results"]:
        lineno = f.match.lineno - f.match.context[0]
        line_printed = False
        count = 0
        start_match = f.match.context[0]
        end_match = count_lines(f.match.lines, f.match.ending) - f.match.context[1]
        for line in f.match.lines.split(f.match.ending):
            if (not line_printed and count == start_match) or (line_printed and count < end_match):
                display_match(f.info.name, lineno, line, no_filename, show_lines, ":")
                line_printed = True
            else:
                display_match(f.info.name, lineno, line, no_filename, show_lines, "-")
            count += 1
            lineno += 1
        if lineno - f.match.lineno > 1:
            print("---")


# def match_output(f, no_filename, count_only, show_lines):
#     if not count_only:
#         for r in f["results"]:
#             lineno = r["lineno"]
#             content = r["lines"][r["match"][0]: r["match"][1]]
#             for line in content.split("\n"):
#                 display_match(f["name"], lineno, line, no_filename, show_lines, ":")
#                 lineno += 1
#             if lineno - r["lineno"] > 1:
#                 print("---")
#     else:
#         count_output(f, no_filename)


def display_output(grep, no_filename, count_only, show_lines, files_only, only_matching):
    """Display output."""

    current_file = None
    count = 0
    for f in grep.find():
        if not f.error:
            if files_only is not None:
                # Show only file name.
                # Can show files that have a match or file that don't.
                if not files_only and f.match is None:
                    print(f.info.name)
                elif files_only and f.match is not None:
                    print(f.info.name)
            # elif only_matching:
            #     match_output(f, no_filename, count_only, show_lines)
            elif count_only:
                if f.match is not None:
                    if not no_filename and current_file is None:
                        current_file = f.info.name
                        count = 1
                    elif no_filename or current_file == f.info.name:
                        count += 1
                    else:
                        print("%s:%d" % (current_file, count))
                        current_file = f.info.name
                        count = 1
                elif count:
                    print("%s:%d" % (current_file, count))
                    current_file = None
                    count = 0
            else:
                normal_output(f, no_filename, show_lines)
        else:
            print("ERROR: %s" % f.error)
    if count:
        if no_filename:
            current_file = ""
        print("%s:%d" % (current_file, count))
        current_file = None
        count = 0


def get_flags(args):
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


def not_none(item, alt=None, idx=None):
    """Return item or indes of item, else return the alternate."""

    return (item if idx is None else item[idx]) if item is not None else alt


def run(args):
    """Run."""

    target = None

    target = args.target
    if not args.buffer:
        target = args.target
        if not os.path.exists(target):
            print("ERROR: %s does not exist" % target)
            return 1

    if args.context is not None:
        context = (int(args.context[0]), int(args.context[0]))
    else:
        context = (int(not_none(args.before_context, alt=0, idx=0)), int(not_none(args.after_context, alt=0, idx=0)))

    grep = rumcore.Grep(
        target=target,
        pattern=args.pattern,
        file_pattern=not_none(args.regexfilepattern, alt=not_none(args.filepattern, idx=0), idx=0),
        folder_exclude=not_none(args.directory_exclude, idx=0),
        context=context,
        max_count=not_none(args.max_count, alt=None, idx=0),
        flags=get_flags(args),
        boolean=args.files_with_matches or args.files_without_match,
        show_hidden=args.show_hidden,
        truncate_lines=True,
        backup=True
    )

    display_output(
        grep,
        (True if args.buffer else args.no_filename),
        args.count,
        args.line_number,
        (False if args.files_with_matches else True if args.files_without_match else None),
        args.only_matching
    )

    return 0


def cli_main():
    """Main entry point."""

    # Setup arg parsing object
    parser = argparse.ArgumentParser(prog="rumcl", description="Grep like file searcher.", add_help=False)
    # Flag arguments
    parser.add_argument(
        "--version", action="version", version=("%(prog)s " + __VERSION__)
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
        "--directory_exclude", "-D", metavar="PATTERN", nargs=1, default=None,
        help="Regex describing directory path(s) to exclude"
    )
    parser.add_argument(
        "--max_count", "-m", metavar="NUM", nargs=1, default=None,
        help="Max matches to find."
    )
    parser.add_argument(
        "--after_context", "-A", metavar="NUM", nargs=1, default=None,
        help="Print number lines of leading context."
    )
    parser.add_argument(
        "--before_context", "-B", metavar="NUM", nargs=1, default=None,
        help="Print number lines of trailing context."
    )
    parser.add_argument(
        "--context", "-C", metavar="NUM", nargs=1, default=None,
        help="Print number lines of context before and after."
    )
    parser.add_argument(
        "--regexfilepattern", "-F", metavar="PATTERN", nargs=1, default=None,
        help="Regex file pattern to search."
    )
    parser.add_argument(
        "--filepattern", "-f", metavar="PATTERN", nargs=1, default="*",
        help="File pattern to search."
    )
    parser.add_argument(
        "--show_hidden", "-H", action="store_true", default=False,
        help="Show hidden files."
    )

    # Positional arguments (must follow flag arguments)
    parser.add_argument("pattern", default=None, help="Search pattern")
    parser.add_argument("target", default=None, help="File, directory, or string buffer to search.")
    # Parse arguments
    return run(parser.parse_args())


if __name__ == "__main__":
    sys.exit(cli_main())
