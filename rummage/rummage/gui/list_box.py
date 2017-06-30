"""ListBox workaround.

WxFormBuilder on macOS currently freezes up when using a ListBox.
So to sidestep this issue, we will use a custom control, that is
actually just a ListBox. This way it doesn't try to render a live
preview of a ListBox and put us in an endless cycle of pain.

Not sure how ListBox behaves on other platforms.
"""
from __future__ import unicode_literals
import wx


class ListBox(wx.ListBox):
    """ListBox workaround."""

    def __init__(self, parent, wx_id):
        """Initialize."""
        wx.ListBox.__init__(self, parent, wx_id, style=wx.LB_SINGLE)
