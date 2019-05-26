"""Copy changelog."""
import sys
import os
import subprocess
from wcmatch import glob
import hashlib
try:
    import mkdocs  # noqa
    import pymdownx  # noqa
except ImportError:
    print(
        '========================================================================================\n'
        'gen_docs requires mkdocs and pymdown-extensions to be installed properly.\n'
        'You can install requirements with the command `pip install -r requirements/docs.txt`.\n'
        'Please reslove the issues and try again.\n'
        '========================================================================================\n'
    )
    raise

__version__ = '2.0.0'

FLAGS = glob.G | glob.N | glob.B | glob.S

FILES_PATTERNS = [
    'mkdocs-internal.yml',
    'docs/src/markdown/**/*.{md,txt,png,gif,html}',
    'docs/internal_theme/**/*.{html,css,js}'
]

MKDOCS_CFG = "mkdocs-internal.yml"
MKDOCS_BUILD = "rummage/lib/gui/data/docs"


def console(cmd, input_file=None):
    """Call with arguments."""

    returncode = None
    output = None

    if sys.platform.startswith('win'):
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        process = subprocess.Popen(
            cmd,
            startupinfo=startupinfo,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE,
            shell=False
        )
    else:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE,
            shell=False
        )

    if input_file is not None:
        with open(input_file, 'rb') as f:
            process.stdin.write(f.read())
    output = process.communicate()
    returncode = process.returncode

    assert returncode == 0, "Runtime Error: %s" % (
        output[0].rstrip().decode('utf-8')
    )

    return output[0].decode('utf-8')


def build_internal_docs(verbose=False, debug=False):
    """Build internal docs."""

    print('Building Docs...')
    print(
        console(
            [
                sys.executable,
                '-m', 'mkdocs', 'build', '--clean',
                '-d', MKDOCS_BUILD,
                '-f', MKDOCS_CFG
            ]
        )
    )
    gen_hash(verbose, debug)


def hash_files(verbose, debug):
    """Hash the file list."""

    found = []
    h = hashlib.new('md5')
    for pattern in FILES_PATTERNS:
        for f in glob.iglob(pattern, flags=FLAGS):
            name = f.replace('\\', '/')
            found.append(name)
    if verbose:
        print('FILES:')
    for f in sorted(found):
        if verbose:
            print(f)
        h.update(f.encode('ascii'))
        with open(f, 'rb') as f:
            h.update(f.read().replace(b'\r\n', b'\n'))
    result = h.hexdigest()
    print('HASH: ', result)
    return result


def gen_hash(verbose, debug):
    """Generate hash."""

    result = hash_files(verbose, debug)
    with open(os.path.join(MKDOCS_BUILD, '.dochash'), 'w') as f:
        f.write(result)
    return 0


def test_hash(verbose=False, debug=False):
    """Test hash."""

    with open(os.path.join(MKDOCS_BUILD, '.dochash'), 'r') as f:
        original = f.read()

    result = hash_files(verbose, debug)
    match = result == original
    if not match:
        print("FAIL: Internal documents are outdated! Please update via \"python tools/gen_docs.py\"")
    return int(not match)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(prog="gen_docs", description='Internal document generator.')
    # Flag arguments
    parser.add_argument('--version', action='version', version=('%(prog)s ' + __version__))
    parser.add_argument('--debug', action='store_true', default=False, help=argparse.SUPPRESS)
    parser.add_argument('--verbose', '-v', action='store_true', default=False)
    parser.add_argument('--test', '-t', action='store_true', default=False)
    args = parser.parse_args()

    if args.test:
        code = test_hash(verbose=args.verbose, debug=args.debug)
    else:
        code = build_internal_docs(verbose=args.verbose, debug=args.debug)
    sys.exit(code)
