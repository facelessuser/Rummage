"""File picker controls."""
import wx
from ..localization import _
from .. import util


class FilePickerCustomCtrl(wx.FilePickerCtrl):
    """Custom file picker that allows us to override and size button."""

    def __init__(
        self, parent, id=wx.ID_ANY, path=wx.EmptyString,  # noqa: A002
        message=wx.FileSelectorPromptStr, wildcard=wx.FileSelectorDefaultWildcardStr,
        pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.FLP_DEFAULT_STYLE | wx.FLP_SMALL,
        validator=wx.DefaultValidator, name=wx.FilePickerCtrlNameStr
    ):
        """Initialization."""

        self.localize()
        self.message = self.MESSAGE

        if util.platform() == 'linux':
            style |= wx.FLP_USE_TEXTCTRL

        wildcard = self.wildcard_override(wildcard)

        super().__init__(parent, id, path, message, wildcard, pos, size, style, validator, name)

    def wildcard_override(self, wildcard):
        """Allow wildcard override."""

        return wildcard

    def localize(self):
        """Translate strings."""

        self.MESSAGE = _("Select file")


class FilePickerAudioCtrl(FilePickerCustomCtrl):
    """File picker for audio files."""

    def wildcard_override(self, wildcard):
        """Allow wildcard override."""

        if util.platform() == "windows":
            wildcard = "*.wav"
        elif util.platform() == "macos":
            wildcard = "*.wav;*.mp3;*.aiff"
        else:
            wildcard = "*.wav;*.mp3;*.ogg"
        return wildcard

    def localize(self):
        """Translate strings."""

        self.MESSAGE = _("Select audio file")
