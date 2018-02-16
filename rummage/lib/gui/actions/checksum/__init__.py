"""Checksum."""
import threading
import hashlib
import zlib
import traceback
import contextlib
import mmap
from . import whirlpool
from . import tiger
from . import sum_hashes

DEFAULT_CHECKSUM = "md5"
VALID_HASH = []

active_thread = None


def get_hash(name):
    """Get hash."""

    try:
        return hashlib.new(name)
    except Exception:
        return _additional_hashes[name]()


class HashThread(threading.Thread):
    """Thread hashing."""

    def __init__(self, f, obj):
        """Initialize."""

        self.hash = False
        self.file_obj = f
        self.obj = obj
        self.abort = False
        self.error = None
        self.count = 0
        threading.Thread.__init__(self)

    def kill(self):
        """Kill the thread."""

        self.abort = True

    def run(self):
        """Run command."""

        try:
            with contextlib.closing(mmap.mmap(self.file_obj.fileno(), 0, access=mmap.ACCESS_READ)) as m:
                chunk = m.read(4096)
                while chunk and not self.abort:
                    self.obj.update(chunk)
                    chunk = m.read(4096)
                    self.count += len(chunk)
        except Exception:
            self.error = str(traceback.format_exc())


class ZlibAlgorithm(object):
    """Zlib hash algorithm."""

    __algorithm = None
    __name = None
    __digest_size = 0
    __hash = 0

    @property
    def name(self):
        """The hash name."""

        return self.__name

    @property
    def digest_size(self):
        """Size of the digest."""

        return self.__digest_size

    def algorithm(self, name, digest_size, start, arg):
        """The main algorithm."""

        self.__algorithm = getattr(zlib, name)
        self.__name = name
        self.__digest_size = digest_size
        self.__hash = start
        self.update(arg)

    def copy(self):
        """Get copy."""

        import copy
        return copy.deepcopy(self)

    def digest(self):
        """Get digest."""

        return None if self.__algorithm is None else self.__hash & 0xffffffff

    def hexdigest(self):
        """Get hex digest."""

        return None if self.__algorithm is None else '%08x' % (self.digest())

    def update(self, arg):
        """Update the hash."""

        if self.__algorithm is not None:
            self.__hash = self.__algorithm(arg, self.__hash)


class crc32(ZlibAlgorithm):  # noqa

    """crc32 hash."""

    def __init__(self, arg=b''):
        """Initialize."""

        self.algorithm('crc32', 4, 0, arg)


class adler32(ZlibAlgorithm):  # noqa

    """adler32 hash."""

    def __init__(self, arg=b''):
        """Initialize."""

        self.algorithm('adler32', 4, 1, arg)


def _verify_hashes(hashes):
    """Verify the hashes are valid."""

    for item in hashes:
        try:
            hashlib.new(item)
            VALID_HASH.append(item)
        except Exception:
            pass


_available_hashes = list(set([x.lower() for x in hashlib.algorithms_available]))
_verify_hashes(_available_hashes)

_additional_hashes = {
    'adler32': adler32,
    'crc32': crc32,
    'sum8': sum_hashes.sum8,
    'sum16': sum_hashes.sum16,
    'sum24': sum_hashes.sum24,
    'sum32': sum_hashes.sum32,
    'xor8': sum_hashes.xor8,
    'tiger': tiger.tiger,
    'whirlpool': whirlpool.whirlpool
}

for k, v in _additional_hashes.items():
    try:
        hashlib.new(k)
    except Exception:
        VALID_HASH.append(k)

VALID_HASH.sort()
