"""
Checksum dialog.

Licensed under MIT
Copyright (c) 2017 Isaac Muse <isaacmuse@gmail.com>

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
import os
import time
from .localization import _
from . import gui
from .. import util
from .actions import checksum
from .generic_dialogs import errormsg


class ChecksumDialog(gui.ChecksumDialog):
    """Search chain dialog."""

    def __init__(self, parent, algorithm, target):
        """Init SaveSearchDialog object."""

        self.file = None
        self.hashing = False
        self.algorithm = algorithm
        self.target = target
        self.handling = False

        super(ChecksumDialog, self).__init__(parent)
        if util.platform() == "windows":
            self.SetDoubleBuffered(True)

        self.localize()
        self.refresh_localization()

        # Ensure good sizing of frame
        self.m_hash_progress.SetValue(0)
        self.m_hash_panel.Fit()
        self.Fit()
        self.SetMinSize(self.GetSize())

        self.total = os.path.getsize(self.target)
        self.start_hash()

    def start_hash(self):
        """Start hashing file."""

        self.m_okay_button.Enable(False)

        try:
            self.file = open(self.target, 'rb')
        except Exception:
            return

        if self.algorithm in checksum.VALID_HASH:
            self.alg = checksum.get_hash(self.algorithm)
        else:
            return
        self.hasher = checksum.HashThread(self.file, self.alg)
        self.hasher.start()
        self.hashing = True

    def localize(self):
        """Translate strings."""

        self.TITLE = _("File Hash")
        self.OKAY = _("Close")
        self.ABORT = _("Abort")

    def refresh_localization(self):
        """Localize."""

        self.SetTitle(self.TITLE)
        self.m_file_label.SetLabel(os.path.basename(self.target))
        self.m_hash_label.SetLabel(self.algorithm + ":")
        self.m_okay_button.SetLabel(self.OKAY)
        self.m_cancel_button.SetLabel(self.ABORT)

    def on_cancel_click(self, event):
        """Handle cancel/abort click."""

        try:
            self.hasher.kill()
        except Exception:
            pass

    def on_okay_click(self, event):
        """Handle okay click."""

        self.Close()

    def on_idle(self, event):
        """Handle idle events (process progress)."""

        if self.hashing and not self.handling:
            self.handling = True
            count = self.hasher.count
            ratio = float(count) / float(self.total)
            percent = int(ratio * 100)
            self.m_hash_progress.SetValue(percent)

            if not self.hasher.is_alive():
                self.hashing = False
                self.m_hash_progress.SetValue(100)
                self.file.close()
                self.file = None

                if not self.hasher.abort:
                    if self.hasher.error:
                        errormsg(self.hasher.error)
                    else:
                        self.m_hash_textbox.SetValue(str(self.alg.hexdigest()))
                self.m_cancel_button.Enable(False)
                self.m_okay_button.Enable(True)
                self.hasher = None
            self.handling = False

        if not self.hashing and self.file:
            self.file.close()
            self.file = None

    def on_close(self, event):
        """Close window."""

        if self.hasher is not None:
            try:
                self.hasher.kill()
            except Exception:
                pass

            while self.hasher is not None and self.hasher.is_alive():
                time.sleep(0.5)

        if self.file:
            self.file.close()
            self.file = None
        event.Skip()
