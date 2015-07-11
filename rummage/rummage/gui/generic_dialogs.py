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
from __future__ import unicode_literals
from . import messages
from ..localization import _


def yesno(question, title=_('Yes or no?'), bitmap=None, yes=_("Okay"), no=_("Cancel")):
    """Wrapper for the prompt dialog."""

    return messages.promptmsg(question, title, bitmap, yes, no)


def infomsg(msg, title=_("INFO"), bitmap=None):
    """Wrapper for the info dialog."""

    messages.infomsg(msg, title, bitmap)


def errormsg(msg, title=_("ERROR"), bitmap=None):
    """Wrapper for the error dialog that also logs the error."""

    messages.errormsg(msg, title, bitmap)


def warnmsg(msg, title=_("WARNING"), bitmap=None):
    """Wrapper for the warning dialog."""

    messages.warnmsg(msg, title, bitmap)
