"""Compatibility module."""
import sys
import os
from datetime import datetime, timedelta, tzinfo


if sys.platform.startswith('win'):
    _PLATFORM = "windows"
elif sys.platform == "darwin":
    _PLATFORM = "macos"
else:
    _PLATFORM = "linux"

ZERO = timedelta(0)


def platform():
    """Get Platform."""

    return _PLATFORM


def get_stat(pth):
    """Get file status."""

    st = os.stat(pth)
    try:
        st_ctime = st.st_birthtime if platform() != "windows" else st.st_ctime
    except AttributeError:
        st_ctime = st.st_ctime
    return st_ctime, st.st_mtime, st.st_size


class UTCTimezone(tzinfo):
    """Epoch UTC time zone object."""

    def utcoffset(self, dt):
        """Return UTC offset."""

        return ZERO

    def tzname(self, dt):
        """Return timezone name."""

        return "UTC"

    def dst(self, dt):
        """Return `dst`."""

        return ZERO


UTC = UTCTimezone()
EPOCH = datetime(1970, 1, 1, tzinfo=UTC)


def local_time_to_epoch_timestamp(date, time):
    """Take a local date and time and convert it to an epoch timestamp."""

    d = date.split("/")
    t = time.split(":")
    dt = datetime(int(d[2]), int(d[0]), int(d[1]), int(t[0]), int(t[1]), int(t[2]), 0, UTC)
    delta = dt - EPOCH
    return (delta.microseconds + (delta.seconds + delta.days * 24 * 3600) * 10 ** 6) / 1e6
