"""
Error Text Dialog.

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
from ..localization import _
from .. import gui


class ErrorTextDialog(gui.ErrorTextDialog):
    """Error text dialog."""

    def __init__(self, parent, text):
        """Initialize."""

        super().__init__(parent)
        self.localize()
        self.refresh_localization()
        self.m_error_textbox.SetValue(text)

        self.m_error_text_panel.Fit()
        self.Fit()
        self.Centre()

    def localize(self):
        """Translate strings."""

        self.ERROR = _("Error")

    def refresh_localization(self):
        """Localize the dialog."""

        self.SetTitle(self.ERROR)
