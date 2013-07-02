"""
Rummage (cli)

Licensed under MIT
Copyright (c) 2011 Isaac Muse <isaacmuse@gmail.com>
https://gist.github.com/facelessuser/5757669

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import argparse
import _lib.pygrep as pygrep
import sys
from os.path import abspath, exists
__VERSION__ = "1.0.0"


def count_lines(string):
    return string.count("\n") + (1 if string[-1] != "\n" else 0)


def display_match(file_name, lineno, line, no_filename, show_lines, separator):
    if no_filename:
        print("%s%s" % (("%d" % lineno) + separator if show_lines else "", line))
    else:
        print("%s%s%s%s" % (file_name, separator, ("%d" % lineno) + separator if show_lines else "", line))


def file_output(f, invert):
    if invert and f["count"] == 0:
        print(f["name"])
    elif not invert and f["count"] > 0:
        print(f["name"])


def count_output(f, no_filename):
    if no_filename:
        print("%d" % len(f["results"]))
    else:
        print("%s:%d" % (f["name"], f["count"]))


def normal_output(f, no_filename, count_only, show_lines):
    if not count_only:
        for r in f["results"]:
            lineno = r["lineno"] - r["context_count"][0]
            line_printed = False
            count = 0
            start_match = r["context_count"][0]
            end_match = count_lines(r["lines"]) - r["context_count"][1]
            for line in r["lines"].split("\n"):
                if (not line_printed and count == start_match) or (line_printed and count < end_match):
                    display_match(f["name"], lineno, line, no_filename, show_lines, ":")
                    line_printed = True
                else:
                    display_match(f["name"], lineno, line, no_filename, show_lines, "-")
                count += 1
                lineno += 1
            if lineno - r["lineno"] > 1:
                print("---")
    else:
        count_output(f, no_filename)


def match_output(f, no_filename, count_only, show_lines):
    if not count_only:
        for r in f["results"]:
            lineno = r["lineno"]
            content = r["lines"][r["match"][0]: r["match"][1]]
            for line in content.split("\n"):
                display_match(f["name"], lineno, line, no_filename, show_lines, ":")
                lineno += 1
            if lineno - r["lineno"] > 1:
                print("---")
    else:
        count_output(f, no_filename)


def display_output(grep, no_filename, count_only, show_lines, files_only, only_matching):
    for f in grep.find():
        if files_only != None:
            file_output(f, files_only)
        elif only_matching:
            match_output(f, no_filename, count_only, show_lines)
        else:
            normal_output(f, no_filename, count_only, show_lines)


def get_flags(args):
    flags = 0

    if args.regexfilepattern != None:
        flags |= pygrep.FILE_REGEX_MATCH

    if not args.regexp:
        flags |= pygrep.LITERAL
    elif args.dotall:
        flags |= pygrep.DOTALL

    if args.ignore_case:
        flags |= pygrep.IGNORECASE

    if args.buffer:
        flags |= pygrep.BUFFER_INPUT
    elif args.recursive:
        flags |= pygrep.RECURSIVE

    return flags


def not_none(item, alt=None, idx=None):
    return (item if idx == None else item[idx]) if item != None else alt


def run(args):
    target = None

    target = args.target
    if not args.buffer:
        target = args.target
        if not exists(target):
            print("%s does not exist" % target)
            return 1

    if args.context != None:
        context = (int(args.context[0]), int(args.context[0]))
    else:
        context = (int(not_none(args.before_context, alt=0, idx=0)), int(not_none(args.after_context, alt=0, idx=0)))

    grep = pygrep.Grep(
        target=target,
        pattern=args.pattern,
        file_pattern=not_none(args.regexfilepattern, alt=not_none(args.filepattern, idx=0), idx=0),
        folder_exclude=not_none(args.directory_exclude, idx=0),
        context=context,
        max_count=not_none(args.max_count, alt=None, idx=0),
        flags=get_flags(args),
        show_hidden=args.show_hidden
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
    # Setup arg parsing object
    parser = argparse.ArgumentParser(prog="Rummage", description="Grep like file searcher.", add_help=False)
    # Flag arguments
    parser.add_argument("--version", action="version", version=("%(prog)s " + __VERSION__))
    parser.add_argument("--help", action="help", help="Show this help message and exit.")
    parser.add_argument("--regexp", "-e", action="store_true", default=False, help="Pattern is a regular expression.")
    parser.add_argument("--ignore_case", "-i", action="store_true", default=False, help="Ignore case when performing search.")
    parser.add_argument("--dotall", "-d", action="store_true", default=False,
        help="Make the '.' special character in regex match any character at all, including a newline."
    )
    parser.add_argument("--recursive", "-r", action="store_true", default=False, help="Recursively search a directory tree.")
    parser.add_argument("--line_number", "-n", action="store_true", default=False, help="Show line numbers.")
    parser.add_argument("--files_without_match", "-L", action="store_true", default=False,
        help='''
            Suppress normal output; instead print the name of each input
            file from which no output would normally have been printed.
            The scanning will stop on the first match.
        '''
    )
    parser.add_argument("--files_with_matches", "-l", action="store_true", default=False,
        help='''
            Suppress normal output; instead print the name of each input
            file from which output would normally have been printed
            The scanning will stop on the first match.
        '''
    )
    parser.add_argument("--only_matching", "-o", action="store_true", default=False, help="Print number lines of trailing context.")
    parser.add_argument("--count", "-c", action="store_true", default=False, help="Only show the match count in each file.")
    parser.add_argument("--buffer", "-b", action="store_true", default=False, help="Parse input parameter as a string buffer.")
    parser.add_argument("--no_filename", "-h", action="store_true", default=False, help="Hide file name in output.")
    parser.add_argument("--directory_exclude", "-D", metavar="PATTERN", nargs=1, default=None, help="Regex describing directory path(s) to exclude")
    parser.add_argument("--max_count", "-m", metavar="NUM", nargs=1, default=None, help="Max matches to find.")
    parser.add_argument("--after_context", "-A", metavar="NUM", nargs=1, default=None, help="Print number lines of leading context.")
    parser.add_argument("--before_context", "-B", metavar="NUM", nargs=1, default=None, help="Print number lines of trailing context.")
    parser.add_argument("--context", "-C", metavar="NUM", nargs=1, default=None, help="Print number lines of context before and after.")
    parser.add_argument("--regexfilepattern", "-F", metavar="PATTERN", nargs=1, default=None, help="Regex file pattern to search.")
    parser.add_argument("--filepattern", "-f", metavar="PATTERN", nargs=1, default="*", help="File pattern to search.")
    parser.add_argument("--show_hidden", "-H", action="store_true", default=False, help="Show hidden files.")

    # Positional arguments (must follow flag arguments)
    parser.add_argument("pattern", default=None, help="Search pattern")
    parser.add_argument("target", default=None, help="File, directory, or string buffer to search.")
    # Parse arguments
    return run(parser.parse_args())


if __name__ == "__main__":
    sys.exit(cli_main())
