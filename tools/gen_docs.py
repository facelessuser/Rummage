"""Copy changelog."""
import sys
import subprocess

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


def build_internal_docs():
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


if __name__ == "__main__":
    build_internal_docs()
