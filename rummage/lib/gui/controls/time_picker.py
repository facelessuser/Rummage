"""Custom time picker that allows us control of the control's color."""
from wx.lib.masked import TimeCtrl
from .. util.colors import Color
from .. import util
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
        bg = Color('red')
        bg.mix(Color.from_wxbgr(ctrl.GetBackgroundColour().GetRGBA()), 0.5, in_place=True)
        self._error_bg = wx.Colour(bg.to_wxbgr(alpha=False)).GetRGB()
        super().__init__(parent, *args, **kwargs)
        font = ctrl.GetFont()
        self.SetFont(wx.Font(font))
        ctrl.Destroy()
        self.Bind(wx.EVT_SYS_COLOUR_CHANGED, self.on_color_change)

    def on_color_change(self, event):
        """Handle color change."""

        self.set_error_bg_color()

        if event:
            event.Skip()

    def set_error_bg_color(self):
        """Set error background color."""

        value = self.GetValue()
        ctrl = wx.TextCtrl(self.GetParent())
        self._bg = ctrl.GetBackgroundColour().GetRGB()
        bg = Color('red')
        bg.mix(Color.from_wxbgr(ctrl.GetBackgroundColour().GetRGBA()), 0.5, in_place=True)
        self._invalidBackgroundColour = wx.Colour(bg.to_wxbgr(alpha=False))
        ctrl.Destroy()
        self.SetParameters()
        self.SetValue(value)

    def SetParameters(self, **kwargs):
        """Force the colors we want."""

        if 'oob_color' in kwargs:
            del kwargs['oob_color']
        maskededit_kwargs = super().SetParameters(**kwargs)
        if util.platform() != "macos" or not util.MAC_OLD:
            maskededit_kwargs['emptyBackgroundColour'] = wx.NullColour
            maskededit_kwargs['validBackgroundColour'] = wx.NullColour
            maskededit_kwargs['foregroundColour'] = wx.NullColour
            maskededit_kwargs['signedForegroundColour'] = wx.NullColour
        maskededit_kwargs['invalidBackgroundColour'] = wx.Colour(self._error_bg)
        return maskededit_kwargs
