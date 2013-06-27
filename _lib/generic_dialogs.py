import _lib.messages as messages
import custom_app as _custom_app

#################################################
# Basic Dialogs
#################################################
def yesno(question, title='Yes or no?', bitmap=None, yes="Okay", no="Cancel"):
    return messages.promptmsg(question, title, bitmap, yes, no)


def infomsg(msg, title="INFO", bitmap=None):
    messages.infomsg(msg, title, bitmap)


def errormsg(msg, title="ERROR", bitmap=None):
    _custom_app.error(msg)
    messages.errormsg(msg, title, bitmap)


def warnmsg(msg, title="WARNING", bitmap=None):
    messages.warnmsg(msg, title, bitmap)
