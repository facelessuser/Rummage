"""Localize project."""
from __future__ import print_function
import subprocess
import sys
import os
import argparse
import codecs

if sys.platform.startswith('win'):
    _PLATFORM = "windows"
elif sys.platform == "darwin":
    _PLATFORM = "osx"
else:
    _PLATFORM = "linux"


def localize(args):
    """Localize project."""

    pygettext = os.path.join(os.path.abspath(args.i18n), 'pygettext.py') if args.i18n is not None else "pygettext.py"
    msgfmt = os.path.join(os.path.abspath(args.i18n), 'msgfmt.py') if args.i18n is not None else "msgfmt.py"
    locale_pth = "locale"
    search_pth = os.path.join("rummage", "rummage", "gui", "*.py")
    cmd = [
        pygettext,
        "-na",
        "-o",
        os.path.join(locale_pth, "messages.po"),
        search_pth
    ]

    # Setup pygettext call
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=(True if _PLATFORM == "windows" else False)
    )

    print("Generating messages.po...")
    output = process.communicate()
    if process.returncode:
        print("Generation failed!")
        print(output[0])
        return 1

    en_us = os.path.join(locale_pth, "en_US")
    if not os.path.exists(en_us):
        os.mkdir(en_us)
    messages = os.path.join(en_us, "LC_MESSAGES")
    if not os.path.exists(messages):
        os.mkdir(messages)

    with codecs.open(os.path.join(locale_pth, "messages.po"), "r", encoding="utf-8") as f:
        content = f.read()
    with codecs.open(os.path.join(messages, "rummage.po"), "w", encoding="utf-8") as f:
        f.write(
            content.replace(
                '"Content-Type: text/plain; charset=CHARSET\\n"',
                '"Content-Type: text/plain; charset=utf-8\\n"'
            )
        )

    for base, dirs, files in os.walk(locale_pth):
        if len(files):
            for f in files:
                if f == "rummage.po":
                    source_file = os.path.join(base, f)
                    # Setup pygettext call
                    process = subprocess.Popen(
                        [
                            msgfmt,
                            source_file
                        ],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        shell=(True if _PLATFORM == "windows" else False)
                    )

                    print(
                        "Compiling %s/%s/%s..." % (
                            os.path.basename(os.path.dirname(base)), os.path.basename(base), "rummage.po"
                        )
                    )
                    output = process.communicate()
                    if process.returncode:
                        print("Compilation failed!")
                        print(output[0])
                        return 1

    return 0


def main():
    """Main."""

    parser = argparse.ArgumentParser(prog="localize_me", description='Localize rummage')
    # Flag arguments
    parser.add_argument('--version', action='version', version=('%(prog)s ' + "1.0.0"))
    parser.add_argument('--i18n', nargs="?", default=None, help="Path to Python's Tools/i18n")
    args = parser.parse_args()

    return localize(args)


if __name__ == "__main__":
    sys.exit(main())
