"""
Export Settings Dialog.

Licensed under MIT
Copyright (c) 2013 - 2017 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.
"""
from __future__ import unicode_literals
# from .app.custom_app import error
from .localization import _
from .settings import Settings
from .generic_dialogs import errormsg, infomsg
from .messages import filepickermsg
from . import gui
from .. import util


class ExportSettingsDialog(gui.ExportSettingsDialog):
    """Export settings dialog."""

    def __init__(self, parent):
        """Initialize dialog."""

        super(ExportSettingsDialog, self).__init__(parent)
        self.localize()
        self.refresh_localization()

        self.m_export_panel.Fit()
        self.Fit()
        self.SetMinSize(self.GetSize())

    def localize(self):
        """Translate strings."""

        self.TITLE = _("Export Settings")
        self.GENERAL_SETTINGS = _("General settings")
        self.CHAINS = _("Chains")
        self.PATTERNS = _("Search/replace patterns")
        self.CANCEL = _("Close")
        self.EXPORT = _("Export")
        self.EXPORT_TO = _("Export to...")
        self.ERR_NO_SELECT = _("No settings are selected!")
        self.ERR_FAILED_EXPORT = _("Failed to export settings!")
        self.SUCCESS_EXPORT = _("Settings were successfully exported!")

    def refresh_localization(self):
        """Localize dialog."""

        self.SetTitle(self.TITLE)
        self.m_general_settings_checkbox.SetLabel(self.GENERAL_SETTINGS)
        self.m_chains_checkbox.SetLabel(self.CHAINS)
        self.m_patterns_checkbox.SetLabel(self.PATTERNS)
        self.m_close_button.SetLabel(self.CANCEL)
        self.m_export_button.SetLabel(self.EXPORT)
        self.Fit()

    def on_export_click(self, event):
        """Export settings."""

        general = self.m_general_settings_checkbox.GetValue()
        chains = self.m_chains_checkbox.GetValue()
        patterns = self.m_patterns_checkbox.GetValue()

        if not general and not chains and not patterns:
            errormsg(self.ERR_NO_SELECT)
            return

        filename = filepickermsg(self.EXPORT_TO, wildcard="*.json", save=True)
        if filename is None:
            return

        settings = Settings.get_settings()
        export = {}

        for k, v in settings.items():
            if k == '__format__':
                export[k] = v
            elif k == 'chains' and chains:
                export[k] = v
            elif k == 'saved_searches' and patterns:
                export[k] = v
            elif k not in ('__format__', 'chains', 'saved_searches', 'last_update_check', 'debug') and general:
                export[k] = v

        try:
            util.write_json(filename, export)
            infomsg(self.SUCCESS_EXPORT)
        except Exception:
            errormsg(self.ERR_FAILED_EXPORT)

    def on_cancel_click(self, event):
        """Close window."""

        self.Close()
