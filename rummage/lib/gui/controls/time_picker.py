"""Custom time picker that allows us control of the control's color."""
from wx.lib.masked import TimeCtrl
from .. util import rgba
import wx


class TimePickerCtrl(TimeCtrl):
    """Time picker that we can force proper colors on."""

    def __init__(self, parent, *args, **kwargs):
        """
        Initialize.

        Create a temporary text control so we can get proper
        background and foreground colors.
        """

        ctrl = wx.TextCtrl(parent)
        self._bg = ctrl.GetBackgroundColour().GetRGB()
        bg = rgba.RGBA(0xFF0000)
        bg.blend(rgba.RGBA(ctrl.GetBackgroundColour().Get()), 60)
        self._error_bg = wx.Colour(*bg.get_rgb()).GetRGB()
        super().__init__(parent, *args, **kwargs)
        font = ctrl.GetFont()
        self.SetFont(wx.Font(font))
        ctrl.Destroy()

    def SetParameters(self, **kwargs):
        """Force the colors we want."""

        if 'oob_color' in kwargs:
            del kwargs['oob_color']
        maskededit_kwargs = super().SetParameters(**kwargs)
        maskededit_kwargs['emptyBackgroundColour'] = wx.NullColour
        maskededit_kwargs['validBackgroundColour'] = wx.NullColour
        maskededit_kwargs['invalidBackgroundColour'] = wx.Colour(self._error_bg)
        maskededit_kwargs['foregroundColour'] = wx.NullColour
        maskededit_kwargs['signedForegroundColour'] = wx.NullColour
        return maskededit_kwargs
