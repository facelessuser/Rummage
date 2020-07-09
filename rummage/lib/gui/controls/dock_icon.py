"""Dock icon."""
import wx.adv as adv


class TaskBarIcon(adv.TaskBarIcon):
    """Dock icon."""

    def __init__(self, frame, name, icon):
        """Initialize."""

        super().__init__(iconType=adv.TBI_DOCK)
        self.frame = frame
        self.name = name

        # Set the image
        self.SetIcon(icon, name)
