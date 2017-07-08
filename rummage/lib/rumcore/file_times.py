"""File times."""
from __future__ import unicode_literals
import os
from .. import util


if util.platform() == "osx":
    import ctypes

    # http://stackoverflow.com/questions/946967/get-file-creation-time-with-python-on-mac
    class StructTimeSpec(ctypes.Structure):
        """TimeSpec structure."""

        _fields_ = [('tv_sec', ctypes.c_long), ('tv_nsec', ctypes.c_long)]

    class StructStat64(ctypes.Structure):
        """Stat64 structure."""

        _fields_ = [
            ('st_dev', ctypes.c_int32),
            ('st_mode', ctypes.c_uint16),
            ('st_nlink', ctypes.c_uint16),
            ('st_ino', ctypes.c_uint64),
            ('st_uid', ctypes.c_uint32),
            ('st_gid', ctypes.c_uint32),
            ('st_rdev', ctypes.c_int32),
            ('st_atimespec', StructTimeSpec),
            ('st_mtimespec', StructTimeSpec),
            ('st_ctimespec', StructTimeSpec),
            ('st_birthtimespec', StructTimeSpec),
            ('dont_care', ctypes.c_uint64 * 8)
        ]

    libc = ctypes.CDLL('libc.dylib')
    stat64 = libc.stat64
    stat64.argtypes = [ctypes.c_char_p, ctypes.POINTER(StructStat64)]

    def getctime(pth):
        """Get the appropriate creation time on OSX."""

        buf = StructStat64()
        rv = stat64(pth.encode("utf-8"), ctypes.pointer(buf))
        if rv != 0:
            raise OSError("Couldn't stat file %r" % pth)
        return buf.st_birthtimespec.tv_sec

else:
    def getctime(pth):
        """Get the creation time for everyone else."""

        return os.path.getctime(pth)


def getmtime(pth):
    """Get modified time for everyone (this is just a wrapper)."""

    return os.path.getmtime(pth)
