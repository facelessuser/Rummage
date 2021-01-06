"""Custom time picker that allows us control of the control's color."""
from wx.lib.masked import TimeCtrl
from ..util.coloraide import Color
from ..util.coloraide.util import fmt_float
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
        bg = Color("#FF0000FF")
        bg.mix("#{:x}".format(ctrl.GetBackgroundColour().Get()), 0.5, in_place=True)
        coords = bg.coords()
        self._error_bg = wx.Colour(
            fmt_float(coords[0] * 255, 0),
            fmt_float(coords[1] * 255, 0),
            fmt_float(coords[2] * 255, 0)
        ).GetRGB()
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
        bg = Color("#FF0000FF")
        bg.mix("#{:x}".format(ctrl.GetBackgroundColour().Get()), 0.5, in_place=True)
        coords = bg.coords()
        self._invalidBackgroundColour = wx.Colour(
            fmt_float(coords[0] * 255, 0),
            fmt_float(coords[1] * 255, 0),
            fmt_float(coords[2] * 255, 0)
        ).GetRGB()
        ctrl.Destroy()
        self.SetParameters()
        self.SetValue(value)

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
