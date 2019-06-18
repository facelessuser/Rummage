"""
Delete dialog.

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
import wx
import os
import time
import threading
from ..localization import _
from .. import gui
from .. import util
from .generic_dialogs import errormsg, yesno_cancel
from send2trash import send2trash

ACTION_DELETE = 1
ACTION_RECYCLE = 2


class DeleteThread(threading.Thread):
    """Thread hashing."""

    def __init__(self, files, recycle=False):
        """Initialize."""

        self.files = files
        self.abort = False
        self.errors = []
        self.recycle = recycle
        self.request = False
        self.trouble_file = None
        self.response = None
        self.count = 0
        threading.Thread.__init__(self)

    def kill(self):
        """Kill the thread."""

        self.abort = True

    def retry(self):
        """Retry loop."""

        deleted = False
        self.request = True
        while self.trouble_file is not None and not self.abort:
            time.sleep(0.5)
            if self.response is not None:
                if self.response is True:
                    self.response = None
                    try:
                        if os.path.exists(self.trouble_file):
                            if self.recycle:
                                send2trash(self.trouble_file)
                            else:
                                os.remove(self.trouble_file)
                        deleted = True
                        self.trouble_file = None
                    except Exception:
                        self.request = True
                elif self.response is False:
                    self.response = None
                    self.trouble_file = None
        return deleted

    def run(self):
        """Run command."""

        for f in self.files:
            # Handle normal case
            try:
                if os.path.exists(f):
                    if self.recycle:
                        send2trash(f)
                    else:
                        os.remove(f)
                self.count += 1
            except Exception:
                self.trouble_file = f

            # Handle retry case
            if self.trouble_file:
                deleted = self.retry()
                if deleted:
                    self.count += 1

            # Handle abort
            if self.abort:
                break


class DeleteDialog(gui.DeleteDialog):
    """Generic progress dialog."""

    def __init__(self, parent, file_list, recycle):
        """Initialize dialog."""

        self.file_list = file_list
        self.action = ACTION_DELETE if not recycle else ACTION_RECYCLE
        self.file = None
        self.busy = False
        self.thread = None
        self.total = len(file_list)
        self.message = None
        self.processing = False
        self.handling = False
        self.skipall = False

        super().__init__(parent)
        if util.platform() == "windows":
            self.SetDoubleBuffered(True)

        title = None
        if self.action == ACTION_DELETE:
            title = _("Deleting Files")
            self.message = _("Deleting %d/%d...")
        elif self.action == ACTION_RECYCLE:
            title = _("Recycling Files")
            self.message = _("Recycling %d/%d...")

        self.localize()
        self.refresh_localization(title)
        if self.message:
            self.m_progress_label.SetLabel(self.message % (0, self.total))

        # Ensure good sizing of frame
        self.m_progress.SetValue(0)
        self.m_progress_panel.Fit()
        self.Fit()
        self.SetMinSize(self.GetSize())
        self.Centre()

        self.start_delete()

    def start_delete(self):
        """Start deleting files."""

        self.m_okay_button.Enable(False)
        self.thread = DeleteThread(self.file_list, self.action == ACTION_RECYCLE)
        self.thread.start()
        self.processing = True

    def start_recycle(self):
        """Start Recycling files."""

    def localize(self):
        """Translate strings."""

        self.OKAY = _("Close")
        self.ABORT = _("Abort")
        self.ERROR = _("Could not delete %d files!")
        self.RETRY = _("Retry?\n\nCould not delete '%s'!")
        self.RETRY_TITLE = _("Retry?")
        self.RETRY_BUTTON = _("Retry")
        self.SKIP_BUTTON = _("Skip")
        self.SKIP_ALL_BUTTON = _("Skip all")
        self.FAIL = _("Could not delete %d files!")

    def refresh_localization(self, title=None):
        """Localize."""

        if title is not None:
            self.SetTitle(title)
        self.m_okay_button.SetLabel(self.OKAY)
        self.m_cancel_button.SetLabel(self.ABORT)

    def on_cancel_click(self, event):
        """Handle cancel/abort click."""

        try:
            self.thread.kill()
        except Exception:
            pass

    def on_okay_click(self, event):
        """Handle okay click."""

        self.Close()

    def on_idle(self, event):
        """Handle idle events (process progress)."""

        if self.processing and not self.handling:
            self.handling = True
            count = self.thread.count
            ratio = float(count) / float(self.total)
            percent = int(ratio * 100)
            self.m_progress.SetValue(percent)
            self.m_progress_label.SetLabel(self.message % (count, self.total))

            if self.thread.request is True:
                self.thread.request = False
                if self.skipall:
                    self.thread.response = False
                else:
                    result = yesno_cancel(
                        self.RETRY % self.thread.trouble_file,
                        title=self.RETRY_TITLE,
                        yes=self.RETRY_BUTTON,
                        no=self.SKIP_BUTTON,
                        cancel=self.SKIP_ALL_BUTTON
                    )
                    if result == wx.ID_CANCEL:
                        self.skipall = True
                        self.thread.response = False
                    elif result == wx.ID_NO:
                        self.thread.response = False
                    else:
                        self.thread.response = True

            if not self.thread.is_alive():
                self.processing = False
                self.m_progress.SetValue(100)
                self.m_progress_label.SetLabel(self.message % (self.thread.count, self.total))

                if not self.thread.abort:
                    if self.thread.errors:
                        errormsg(self.FAIL % (self.total - self.thread.count))
                self.m_cancel_button.Enable(False)
                self.m_okay_button.Enable(True)
                self.thread = None
            self.handling = False

    def on_close(self, event):
        """Close window."""

        if self.thread is not None:
            try:
                self.thead.kill()
            except Exception:
                pass

            while self.thread is not None and self.thread.is_alive():
                time.sleep(0.5)

        event.Skip()
