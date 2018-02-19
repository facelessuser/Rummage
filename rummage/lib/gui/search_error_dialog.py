"""
Search Error Dialog.

Licensed under MIT
Copyright (c) 2013 - 2015 Isaac Muse <isaacmuse@gmail.com>

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
from .app.custom_app import error
from .error_text_dialog import ErrorTextDialog
from .localization import _
from . import gui


class SearchErrorDialog(gui.SearchErrorDialog):
    """Load search dialog."""

    def __init__(self, parent, errors):
        """Init LoadSearchDialog."""

        super(SearchErrorDialog, self).__init__(parent)
        self.localize()
        self.refresh_localization()

        self.m_error_panel.Fit()
        self.Fit()
        self.SetMinSize(self.GetSize())
        self.load_errors(errors)
        self.m_error_list.SetFocus()

    def localize(self):
        """Translate strings."""

        self.TITLE = _("Errors")
        self.ERR_COULD_NOT_PROCESS = _("Cound not process %s:\n%s")

    def refresh_localization(self):
        """Localize dialog."""

        self.SetTitle(self.TITLE)
        self.Fit()

    def show_error(self, text):
        """Show full single error in dialog."""

        dlg = ErrorTextDialog(self, text)
        dlg.ShowModal()
        dlg.Destroy()

    def load_errors(self, errors):
        """Populate list with error entries."""

        count = 0
        for e in errors:
            if hasattr(e, 'info'):
                name = e.info.name if e.info.name is not None else ''
            else:
                name = '<NA>'
            error(
                self.ERR_COULD_NOT_PROCESS % (name, e.error[1] + e.error[0])
            )
            self.m_error_list.set_item_map("%d" % count, e.error, name)
            count += 1
        self.m_error_list.load_list(True)

    def on_close(self, event):
        """Handle on close event."""

        self.m_error_list.destroy()
        event.Skip()
