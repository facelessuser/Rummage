"""File picker controls."""
import wx
from ..localization import _
from .. import util


class FilePickerAudioCtrl(wx.FilePickerCtrl):
    """File picker for audio files."""

    def __init__(
        self, parent, id=wx.ID_ANY, path=wx.EmptyString,
        message=wx.FileSelectorPromptStr, wildcard=wx.FileSelectorDefaultWildcardStr,
        pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.FLP_DEFAULT_STYLE,
        validator=wx.DefaultValidator, name=wx.FilePickerCtrlNameStr
    ):
        """Initialize."""

        self.localize()

        self.message = self.MESSAGE

        if util.platform() == "windows":
            wildcard = "*.wav"
        elif util.platform() == "macos":
            wildcard = "*.wav;*.mp3;*.aiff"
        else:
            wildcard = "*.wav;*.mp3;*.ogg"
        super().__init__(parent, id, path, message, wildcard, pos, size, style, validator, name)
        btn = self.GetPickerCtrl()
        btn.SetLabel(self.BROWSE)

    def localize(self):
        """Translate strings."""

        self.MESSAGE = _("Select audio file")
        self.BROWSE = _("Browse")
