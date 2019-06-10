"""
Open Editor.

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
import os
import subprocess
import codecs
import json
from .sanitize_json import sanitize
from ..settings import Settings
from ..app.custom_app import error
from ..dialogs.generic_dialogs import errormsg
from ..localization import _
from .. import util


def call(cmd):
    """Call command."""

    fail = False

    is_string = isinstance(cmd, (str, bytes))

    try:
        if util.platform() == "windows":
            startupinfo = subprocess.STARTUPINFO()
            subprocess.Popen(
                cmd,
                startupinfo=startupinfo,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE,
                shell=is_string
            )
        else:
            subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE,
                shell=is_string
            )
    except Exception:
        fail = True

    return fail


def read_json(filename):
    """Read JSON."""

    try:
        with codecs.open(filename, "r", encoding='utf-8') as f:
            content = sanitize(f.read(), True)
        obj = json.loads(content)
    except Exception:
        obj = None
    return obj


def write_json(filename, obj):
    """Write JSON."""

    fail = False

    try:
        j = json.dumps(obj, sort_keys=True, indent=4, separators=(',', ': '))
        with codecs.open(filename, 'w', encoding='utf-8') as f:
            f.write(j + "\n")
    except Exception:
        fail = True

    return fail


def open_editor(filename, line, col):
    """Open editor with the optional filename, line, and col parameters."""

    cmd = Settings.get_editor(filename=filename, line=line, col=col)
    if not cmd:
        errormsg(_("No editor is currently set!"))
        error("No editor set: %s" % cmd)
        return

    return call(cmd)


def reveal(event, target):
    """Reveal in file manager."""

    cmd = {
        "windows": 'explorer /select,"%s"',
        "macos": 'open -R "%s"',
        "linux": 'xdg-open "%s"'
    }

    if util.platform() == "linux":
        target = os.path.dirname(target)

    return call(cmd[util.platform()] % target.replace('"', '\\"'))
