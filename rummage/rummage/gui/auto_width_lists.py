"""AutoWidthList."""
from __future__ import unicode_literals
import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin

class AutoWidthListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):
    """Auto width list."""

    def __init__(self, parent, wx_id):
        """Initialize."""
        wx.ListCtrl.__init__(self, parent, wx_id, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_NO_HEADER)
        ListCtrlAutoWidthMixin.__init__(self)
