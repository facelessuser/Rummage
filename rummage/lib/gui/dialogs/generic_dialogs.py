"""
Generic Dialogs.

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
from ..localization import _
from . import msg_dialogs


def yesno(question, title=None, bitmap=None, yes=None, no=None, checkbox=None, checked=None):
    """Wrapper for the prompt dialog."""

    if title is None:
        title = _('Yes or no?')
    if yes is None:
        yes = _("Okay")
    if no is None:
        no = _("Cancel")
    if checkbox is None:
        checkbox = _("Apply to all")

    return msg_dialogs.promptmsg(question, title, bitmap, yes, no, checkbox, checked)


def yesno_cancel(
    question, title=None, bitmap=None, yes=None, no=None, cancel=None, checkbox=None, checked=None
):
    """Wrapper for the prompt dialog."""

    if title is None:
        title = _('Yes or no?')
    if yes is None:
        yes = _("Yes")
    if no is None:
        no = _("No")
    if cancel is None:
        cancel = _("Cancel")
    if checkbox is None:
        checkbox = _("Apply to all")

    return msg_dialogs.prompt3msg(question, title, bitmap, yes, no, cancel, checkbox, checked)


def infomsg(msg, title=None, bitmap=None):
    """Wrapper for the info dialog."""

    if title is None:
        title = _("INFO")

    msg_dialogs.infomsg(msg, title, bitmap)


def errormsg(msg, title=None, bitmap=None):
    """Wrapper for the error dialog that also logs the error."""

    if title is None:
        title = _("ERROR")

    msg_dialogs.errormsg(msg, title, bitmap)


def warnmsg(msg, title=None, bitmap=None):
    """Wrapper for the warning dialog."""

    if title is None:
        title = _("WARNING")

    msg_dialogs.warnmsg(msg, title, bitmap)
