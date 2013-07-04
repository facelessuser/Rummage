"""
Licensed under MIT
Copyright (c) 2013 Isaac Muse <isaacmuse@gmail.com>
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import _gui.messages as messages
import _gui.custom_app as _custom_app

def yesno(question, title='Yes or no?', bitmap=None, yes="Okay", no="Cancel"):
    return messages.promptmsg(question, title, bitmap, yes, no)


def infomsg(msg, title="INFO", bitmap=None):
    messages.infomsg(msg, title, bitmap)


def errormsg(msg, title="ERROR", bitmap=None):
    _custom_app.error(msg)
    messages.errormsg(msg, title, bitmap)


def warnmsg(msg, title="WARNING", bitmap=None):
    messages.warnmsg(msg, title, bitmap)
