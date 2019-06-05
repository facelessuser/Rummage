"""Picker button class."""
import wx
import os
from ..dialogs.msg_dialogs import dirpickermsg, filepickermsg

PickChangeEvent, EVT_PICK_CHANGE = wx.lib.newevent.NewEvent()


def pick_extend(instance, extension):
    """Extend instance with extension class."""

    instance.__class__ = type(
        '%s_extended_with_%s' % (
            instance.__class__.__name__, extension.__name__
        ),
        (instance.__class__, extension),
        {}
    )


class PickButton:
    """Directory pick button."""

    DIR_TYPE = 0
    FILE_TYPE = 1

    def GetPath(self):
        """Get current target path."""

        return self.target

    def SetPath(self, target):
        """Set the current target path."""

        if (
            target is not None and
            os.path.exists(target) and
            (
                (self.pick_type == self.DIR_TYPE and os.path.isdir(target)) or
                (self.pick_type == self.FILE_TYPE and os.path.isfile(target))
            )
        ):
            self.target = target

    def pick_init(self, pick_type, dialog_msg, default_path=None, pick_change_evt=None):
        """Initialize the `PickButton`."""

        self.dialog_msg = dialog_msg
        if default_path is not None and os.path.exists(default_path):
            self.default_path = default_path
        else:
            self.default_path = os.path.expanduser("~")
        self.pick_type = pick_type
        self.target = self.default_path
        self.Bind(wx.EVT_BUTTON, self.on_pick)
        self.Bind(EVT_PICK_CHANGE, self.on_change)
        self.pick_change_callback = pick_change_evt

    def AcceptsFocus(self):
        """
        Check if we should accept focus.

        If the button is hidden, we should not allow focus.
        """

        return self.IsShown()

    def on_change(self, event):
        """If the directory has changed call the callback given."""

        if self.pick_change_callback is not None:
            self.pick_change_callback(event)
        event.Skip()

    def on_pick(self, event):
        """
        When a new directory/file is picked, validate it, and set it if it is good.

        Call the `PickChangeEvent` to do any desired callback as well.
        """

        target = self.GetPath()
        if (target is None or not os.path.exists(target)):
            target = self.default_path
        if (target is None or not os.path.exists(target)):
            target = os.path.expanduser("~")
        if self.pick_type == self.DIR_TYPE:
            target = dirpickermsg(self.dialog_msg, target)
        else:
            if os.path.isfile(target):
                target = os.path.dirname(target)
            target = filepickermsg(self.dialog_msg, default_path=target, wildcard='*.py')
        if target is None or target == "":
            target = None
        self.SetPath(target)
        evt = PickChangeEvent(target=target)
        wx.PostEvent(self, evt)
        event.Skip()
