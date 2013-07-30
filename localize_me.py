import subprocess
import sys
from os.path import dirname, basename, abspath, exists, join
from os import chdir, mkdir, walk
import argparse
import codecs

if sys.platform.startswith('win'):
    _PLATFORM = "windows"
elif sys.platform == "darwin":
    _PLATFORM = "osx"
else:
    _PLATFORM = "linux"


def localize(args):
    pygettext = abspath(args.pygettext) if args.pygettext is not None else "pygettext.py"
    msgfmt = abspath(args.msgfmt) if args.msgfmt is not None else "msgfmt.py"
    locale_pth = "locale"
    search_pth = join("_gui", "*.py")
    cmd = [
       pygettext,
       "-na",
       "-o",
       join(locale_pth, "messages.po"),
       search_pth
    ]

    # Setup pygettext call
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=(True if _PLATFORM == "windows" else False)
    )

    print "Generating messages.po..."
    output = process.communicate()
    if process.returncode:
        print >> sys.stderr, "Generation failed!"
        print output[0]
        return 1

    en_US = join(locale_pth, "en_US")
    if not exists(en_US):
        mkdir(en_US)
    messages = join(en_US, "LC_MESSAGES")
    if not exists(messages):
        mkdir(messages)

    with codecs.open(join(locale_pth, "messages.po"), "r", encoding="utf-8") as f:
        content = f.read()
    with codecs.open(join(messages, "rummage.po"), "w", encoding="utf-8") as f:
        f.write(content.replace('"Content-Type: text/plain; charset=CHARSET\\n"', '"Content-Type: text/plain; charset=utf-8\\n"'))

    for base, dirs, files in walk(locale_pth):
        if len(files):
            for f in files:
                if f == "rummage.po":
                    source_file = join(base, f)
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

                    print "Compiling %s/%s/%s..." % (basename(dirname(base)), basename(base), "rummage.po")
                    output = process.communicate()
                    if process.returncode:
                        print >> sys.stderr, "Compilation failed!"
                        print output[0]
                        return 1

    return 0


def main():
    parser = argparse.ArgumentParser(prog="localize_me", description='Localize rummage')
    # Flag arguments
    parser.add_argument('--version', action='version', version=('%(prog)s ' + "1.0.0"))
    parser.add_argument('--pygettext', nargs="?", default=None, help="Path to pygettext.py")
    parser.add_argument('--msgfmt', nargs="?", default=None, help="Path to msgfmt.py")
    args = parser.parse_args()

    return localize(args)


if __name__ == "__main__":
    sys.exit(main())
