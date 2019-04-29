"""
File stat.

Get just what we need all in one call.
"""
from __future__ import unicode_literals
import os
from .. import util


if util.platform() == "osx":
    import ctypes

    # http://stackoverflow.com/questions/946967/get-file-creation-time-with-python-on-mac
    class StructTimeSpec(ctypes.Structure):
        """`TimeSpec` structure."""

        _fields_ = [('tv_sec', ctypes.c_long), ('tv_nsec', ctypes.c_long)]

    class StructStat64(ctypes.Structure):
        """`Stat64` structure."""

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
            ('st_size', ctypes.c_int64),
            ('dont_care', ctypes.c_uint64 * 7)
        ]

    libc = ctypes.CDLL('libc.dylib')
    stat64 = libc.stat64
    stat64.argtypes = [ctypes.c_char_p, ctypes.POINTER(StructStat64)]

    def get_stat(pth):
        """Get `stat` with the appropriate creation time on macOS."""

        buf = StructStat64()
        rv = stat64(pth.encode("utf-8"), ctypes.pointer(buf))
        if rv != 0:
            raise OSError("Couldn't stat file %r" % pth)
        size = 0 if buf.st_size < 0 else buf.st_size
        return buf.st_birthtimespec.tv_sec, buf.st_mtimespec.tv_sec, size

else:
    def get_stat(pth):
        """Get `stat`."""

        st = os.stat(pth)
        return st.st_ctime, st.st_mtime, st.st_size
