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
from __future__ import unicode_literals
import os
from ..settings import Settings
from ..app.custom_app import error
from ..generic_dialogs import errormsg
from ..localization import _
from ... import util


def open_editor(filename, line, col):
    """Open editor with the optional filename, line, and col parameters."""

    cmd = Settings.get_editor(filename=filename, line=line, col=col)
    if not cmd:
        errormsg(_("No editor is currently set!"))
        error("No editor set: %s" % cmd)
        return

    return util.call(cmd)


def reveal(event, target):
    """Reveal in file manager."""

    cmd = {
        "windows": 'explorer /select,"%s"',
        "osx": 'open -R "%s"',
        "linux": 'xdg-open "%s"'
    }

    if util.platform() == "linux":
        target = os.path.dirname(target)

    return util.call(cmd[util.platform()] % target.replace('"', '\\"'))
