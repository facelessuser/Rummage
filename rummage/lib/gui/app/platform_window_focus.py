"""Platform window focus."""
from .. import util
import os
import subprocess

MAC_RAISE_OSASCRIPT = '''\
tell application "System Events"
  set procName to name of first process whose unix id is %s
end tell
tell application procName to activate
'''


def platform_window_focus(frame):
    """Set focus to the window frame."""

    # General window raising
    if frame.IsIconized():
        frame.Iconize(False)
    if not frame.IsShown():
        frame.Show(True)
    frame.Raise()

    # macOS specific extra to ensure raise
    if util.platform() == "macos":
        subprocess.Popen(['osascript', '-e', MAC_RAISE_OSASCRIPT % os.getpid()])
