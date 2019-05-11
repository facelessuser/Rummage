"""Custom collapsible pane."""
from __future__ import unicode_literals
import wx
import wx.lib.agw.pycollapsiblepane as pycollapse
import wx.lib.buttons as buttons
from .. import data
from ... import util

IS_MAC = util.platform() == "osx"


class CollapsiblePane(pycollapse.PyCollapsiblePane):
    """Custom collapsible pane."""

    def __init__(
        self, parent, id=wx.ID_ANY, label="", pos=wx.DefaultPosition,  # noqa: A002
        size=wx.DefaultSize, agwStyle=wx.CP_DEFAULT_STYLE
    ):
        """Initialize."""

        super(CollapsiblePane, self).__init__(
            parent, id, label, pos, size, 0, agwStyle
        )
        btn = CollapseButton(self, label)
        self.SetButton(btn)
        btn.Bind(wx.EVT_CHAR_HOOK, self.on_tab)

    def AcceptsFocus(self):
        """
        Check if we should accept focus.

        We should never accept focus.
        """

        return False

    def on_focus(self, event):
        """Focus."""

        self._pButton.SetFocus()

    def on_tab(self, event):
        """Handle tab."""
        if event.GetUnicodeKey() == wx.WXK_TAB:
            if event.ShiftDown():
                self.Navigate(False)
            else:
                self.NavigateIn()

    def workaround(self):
        """Apply workaround for macOS."""

        self.GetPane().AcceptsFocus = self.AcceptsFocus
        self.GetPane().GetSizer().GetItem(0).GetWindow().Bind(
            wx.EVT_SET_FOCUS, self.on_focus
        )

    def GetBtnLabel(self):
        """Returns the button label."""

        return self.GetLabel()

    def Collapse(self, collapse=True):
        """Collapse."""

        self._pButton.SetToggle(collapse)
        super(CollapsiblePane, self).Collapse(collapse)


class CollapseButton(buttons.GenBitmapTextToggleButton):
    """Custom button."""

    labelDelta = 0  # noqa: N815

    def __init__(self, parent, label):
        """Initialization."""

        super(CollapseButton, self).__init__(
            parent, -1, bitmap=data.get_bitmap('arrow_down.png'), label=label,
            style=wx.BORDER_NONE | wx.BU_EXACTFIT | wx.TAB_TRAVERSAL
        )
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE))
        self.InitColours()
        self.SetBitmapLabel(data.get_bitmap('arrow_down.png', tint=self.tint))
        self.SetBitmapSelected(data.get_bitmap('arrow_right.png', tint=self.tint))
        self.SetUseFocusIndicator(True)

    def InitColours(self):
        """Calculate a new set of highlight and shadow colours."""

        face = self.GetBackgroundColour()
        rgba = data.RGBA(*face.Get())
        self.tint = (
            data.RGBA(0x33, 0x33, 0x33, 0xFF) if rgba.get_luminance() > 127 else data.RGBA(0xbb, 0xbb, 0xbb, 0xFF)
        )
        self.faceDnClr = face
        self.shadowPenClr = face
        self.highlightPenClr = face
        self.focusClr = face
