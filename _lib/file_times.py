import sys
from os.path import getmtime as get_modified_time

if sys.platform.startswith('win'):
    _PLATFORM = "windows"
elif sys.platform == "darwin":
    _PLATFORM = "osx"
else:
    _PLATFORM = "linux"


if _PLATFORM == "osx":
    from ctypes import *


    # http://stackoverflow.com/questions/946967/get-file-creation-time-with-python-on-mac
    class struct_timespec(Structure):
        _fields_ = [('tv_sec', c_long), ('tv_nsec', c_long)]


    class struct_stat64(Structure):
        _fields_ = [
            ('st_dev', c_int32),
            ('st_mode', c_uint16),
            ('st_nlink', c_uint16),
            ('st_ino', c_uint64),
            ('st_uid', c_uint32),
            ('st_gid', c_uint32),
            ('st_rdev', c_int32),
            ('st_atimespec', struct_timespec),
            ('st_mtimespec', struct_timespec),
            ('st_ctimespec', struct_timespec),
            ('st_birthtimespec', struct_timespec),
            ('dont_care', c_uint64 * 8)
        ]


    libc = CDLL('libc.dylib')
    stat64 = libc.stat64
    stat64.argtypes = [c_char_p, POINTER(struct_stat64)]

    def getctime(pth):
        """
        Get the appropriate creation time on OSX
        """

        buf = struct_stat64()
        rv = stat64(pth.encode("utf-8"), pointer(buf))
        if rv != 0:
            raise OSError("Couldn't stat file %r" % pth)
        return buf.st_birthtimespec.tv_sec

else:
    from os.path import getctime as get_creation_time


    def getctime(pth):
        """
        Get the creation time for everyone else
        """

        return get_creation_time(pth)


def getmtime(pth):
    """
    Get modified time for everyone
    """

    return get_modified_time(pth)
