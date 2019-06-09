"""File picker controls."""
import wx
from ..localization import _
from .. import util


class FilePickerCustomCtrl(wx.FilePickerCtrl):
    """Custom file picker that allows us to override and size button."""

    def __init__(
        self, parent, id=wx.ID_ANY, path=wx.EmptyString,  # noqa: A002
        message=wx.FileSelectorPromptStr, wildcard=wx.FileSelectorDefaultWildcardStr,
        pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.FLP_DEFAULT_STYLE,
        validator=wx.DefaultValidator, name=wx.FilePickerCtrlNameStr
    ):
        """Initialization."""

        self.localize()
        self.message = self.MESSAGE

        wildcard = self.wildcard_override(wildcard)

        super().__init__(parent, id, path, message, wildcard, pos, size, style, validator, name)

        btn = self.GetPickerCtrl()
        btn.SetLabel(self.BROWSE)
        self.set_exact_fit()

    def wildcard_override(self, wildcard):
        """Allow wildcard override."""

        return wildcard

    def localize(self):
        """Translate strings."""

        self.MESSAGE = _("Select file")
        self.BROWSE = _("...")

    def set_exact_fit(self):
        """Set exact fit button size."""

        btn = self.GetPickerCtrl()
        w = btn.GetTextExtent(btn.GetLabel())[0]
        width = w + 2 + 2 * 6 + 4 * 1
        btn.SetMinSize(wx.Size(width, btn.GetSize()[1]))


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
        self.BROWSE = _("...")
