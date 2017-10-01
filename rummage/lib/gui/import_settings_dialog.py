"""
Import Settings Dialog.

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
from . import gui


class ImportSettingsDialog(gui.ImportSettingsDialog):
    """Import settings dialog."""

    def __init__(self, parent):
        """Init ImportSettingsDialog."""

        super(ImportSettingsDialog, self).__init__(parent)
        self.localize()
        self.refresh_localization()

        self.m_import_panel.Fit()
        self.Fit()
        self.SetMinSize(self.GetSize())

    def localize(self):
        """Translate strings."""

        self.TITLE = _("Import Settings")
        self.GENERAL_SETTINGS = _("General settings")
        self.CHAINS = _("Chains")
        self.PATTERNS = _("Search/replace patterns")
        self.CANCEL = _("Close")
        self.IMPORT = _("Import")

    def refresh_localization(self):
        """Localize dialog."""

        self.SetTitle(self.TITLE)
        self.m_general_settings_checkbox.SetLabel(self.GENERAL_SETTINGS)
        self.m_chains_checkbox.SetLabel(self.CHAINS)
        self.m_patterns_checkbox.SetLabel(self.PATTERNS)
        self.m_close_button.SetLabel(self.CANCEL)
        self.m_import_button.SetLabel(self.IMPORT)
        self.Fit()

    def on_import_click(self, event):
        """Import settings."""

        pass

    def on_cancel_click(self, event):
        """Close window."""

        self.Close()
