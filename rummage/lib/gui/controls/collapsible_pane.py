"""Custom collapsible pane."""
from __future__ import unicode_literals
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

        super(CollapsiblePane, self).__init__(
            parent, id, label, pos, size, 0, agwStyle
        )
        btn = CollapseButton(self, label)
        self.SetButton(btn)
        btn.Bind(wx.EVT_KEY_DOWN, self.on_tab)

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
            parent, -1, bitmap=data.get_bitmap('sd.png'), label=label,
            style=wx.BORDER_NONE | wx.BU_EXACTFIT | wx.TAB_TRAVERSAL
        )
        self.SetBitmapSelected(data.get_bitmap('su.png'))
        self.SetUseFocusIndicator(True)
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE))

    def InitColours(self):
        """Calculate a new set of highlight and shadow colours."""

        face = self.GetBackgroundColour()
        self.faceDnClr = face
        self.shadowPenClr = face
        self.highlightPenClr = face
        self.focusClr = face
