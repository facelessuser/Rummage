"""Custom collapsible pane."""
import wx
import wx.lib.agw.pycollapsiblepane as pycollapse
import wx.lib.buttons as buttons
from .. import data


class CollapsiblePane(pycollapse.PyCollapsiblePane):
    """Custom collapsible pane."""

    def __init__(
        self, parent, id=wx.ID_ANY, label="", pos=wx.DefaultPosition,  # noqa: A002
        size=wx.DefaultSize, agwStyle=wx.CP_DEFAULT_STYLE
    ):
        """Initialize."""

        super().__init__(
            parent, id, label, pos, size, 0, agwStyle
        )
        btn = CollapseButton(self, label)
        self.SetButton(btn)
        btn.Bind(wx.EVT_CHAR_HOOK, self.on_tab)

    def SetBackgroundColour(self, color):
        """Set background color."""

        super().SetBackgroundColour(color)
        self._pButton.SetBackgroundColour(color)

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
        super().Collapse(collapse)


class CollapseButton(buttons.GenBitmapTextToggleButton):
    """Custom button."""

    labelDelta = 0  # noqa: N815

    def __init__(self, parent, label):
        """Initialization."""

        super().__init__(
            parent, -1, bitmap=data.get_bitmap('arrow_down.png'), label=label,
            style=wx.BORDER_NONE | wx.BU_EXACTFIT | wx.TAB_TRAVERSAL
        )

        self.Bind(wx.EVT_SYS_COLOUR_CHANGED, self.on_color_change)
        self.set_colors()
        self.SetUseFocusIndicator(True)

    def on_color_change(self, event):
        """On color change."""

        self.set_colors()

        if event:
            event.Skip()

    def set_colors(self):
        """On color change."""

        self.SetBackgroundColour(self.GetParent().GetBackgroundColour())
        self.init_collapse_arrow()

    def init_collapse_arrow(self):
        """Initialize collapse arrow."""

        color = data.RGBA(self.GetForegroundColour().Get()[:3])
        self.SetBitmapLabel(data.get_bitmap('arrow_down.png', tint=color, alpha=0.5))
        self.SetBitmapSelected(data.get_bitmap('arrow_right.png', tint=color, alpha=0.5))

    def SetForegroundColour(self, color):
        """Set foreground color."""

        super().SetForegroundColour()
        self.init_collapse_arrow()

    def InitColours(self):
        """Calculate a new set of highlight and shadow colours."""

        face = self.GetBackgroundColour()
        self.faceDnClr = face
        self.shadowPenClr = face
        self.highlightPenClr = face
        self.focusClr = face
