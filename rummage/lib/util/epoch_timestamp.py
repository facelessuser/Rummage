"""Epoch timestamp."""
from __future__ import unicode_literals
from datetime import datetime, timedelta, tzinfo

ZERO = timedelta(0)


class UTCTimezone(tzinfo):
    """Epoch UTC time zone object."""

    def utcoffset(self, dt):
        """Return UTC offset."""

        return ZERO

    def tzname(self, dt):
        """Return timezone name."""

        return "UTC"

    def dst(self, dt):
        """Return dst."""

        return ZERO


UTC = UTCTimezone()
EPOCH = datetime(1970, 1, 1, tzinfo=UTC)


def totimestamp(dt, epoch=EPOCH):
    """Format datetime as timestamp."""

    td = dt - epoch
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10 ** 6) / 1e6


def local_time_to_epoch_timestamp(date, time):
    """Take a local date and time and convert it to an epoch timestamp."""

    d = date.split("/")
    t = time.split(":")
    return totimestamp(
        datetime(int(d[2]), int(d[0]), int(d[1]), int(t[0]), int(t[1]), int(t[2]), 0, UTC)
    )
