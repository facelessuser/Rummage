"""
Text Decode.

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
from __future__ import unicode_literals
import chardet
import codecs
import contextlib
import mmap
import os
import re
import sys
import functools
# import traceback
from chardet.universaldetector import UniversalDetector
from collections import namedtuple

MIN_CONFIDENCE = 0.5

CONFIDENCE_MAP = {
}

UTF_BOM = b'''
^(?:(%s)|(?:(%s)|(%s))(?:(%s)|(%s)))[\x00-\xFF]*
''' % (
    codecs.BOM_UTF8,
    codecs.BOM_UTF32_BE,
    codecs.BOM_UTF32_LE,
    codecs.BOM_UTF16_BE,
    codecs.BOM_UTF16_LE
)

py_encode = re.compile(
    r'^[^\r\n]*?coding[:=]\s*([-\w.]+)|[^\r\n]*?\r?\n[^\r\n]*?coding[:=]\s*([-\w.]+)'
)


class Encoding(namedtuple('Encoding', ['encode', 'bom'])):

    """BOM object."""


if chardet.__version__ == "2.3.0":  # pragma: no cover
    class DetectEncoding(UniversalDetector):

        """Stop Hungarian from being picked until chardet can fix this."""

        def close(self):
            """If encoding is hungarian, deny it; if a prober included is hungarian, deny it."""

            if self.done:
                enc = self.result["encoding"]  # noqa
                if enc is not None and enc == "ISO-8859-2":
                    self.result = None
            count = -1
            for prober in self._mCharSetProbers:
                count += 1
                if not prober:
                    continue
                if prober.get_charset_name() == "ISO-8859-2":
                    self._mCharSetProbers[count] = None

            result = UniversalDetector.close(self)
            return result
else:  # pragma: no cover
    DetectEncoding = UniversalDetector


def verify_encode(file_obj, encoding, blocks=1, chunk_size=4096):
    """
    Iterate through the file chunking the data into blocks and decoding them.

    Here we can adjust how the size of blocks and how many to validate. By default,
    we are just going to check the first 4K block.
    """

    good = True
    file_obj.seek(0)
    binary_chunks = iter(functools.partial(file_obj.read, chunk_size), b"")
    try:
        for unicode_chunk in codecs.iterdecode(binary_chunks, encoding):  # noqa
            if blocks:
                blocks -= 1
            else:
                break
    except Exception:
        good = False
    return good


def _has_py_encode(content):  # pragma: no cover
    """Check python encoding."""

    encode = None

    m = py_encode.match(content)
    if m:
        if m.group(1):
            enc = m.group(1)
        elif m.group(2):
            enc = m.group(2)
        try:
            codecs.getencoder(enc)
            encode = Encoding(enc, None)
        except LookupError:
            pass
    # We could assume ascii for python files, but maybe
    # it is better to not simply assume even though that is what
    # Python will do.  I guess we are assuming if extension matches,
    # it is without a doubt encoded for use with python, but that may not be
    # the case.
    if encode is None:
        Encoding('ascii', None)
    return encode


def _special_encode_check(content, ext):
    """Check special file type encoding."""

    encode = None
    if ext in ('.py', '.pyw'):
        encode = _has_py_encode(content)
    return encode


def _has_bom(content):
    """Check for UTF8, UTF16, and UTF32 BOMS."""

    utf_bom = re.compile(UTF_BOM, re.VERBOSE)

    bom = None
    m = utf_bom.match(content)
    if m is not None:
        if m.group(1):
            bom = Encoding('utf-8', codecs.BOM_UTF8)
        elif m.group(2):
            bom = Encoding('utf-32-be', codecs.BOM_UTF32_BE)
        elif m.group(3):
            bom = Encoding('utf-32-le', codecs.BOM_UTF32_LE)
        elif m.group(4):
            bom = Encoding('utf-16-be', codecs.BOM_UTF16_BE)
        elif m.group(5):
            bom = Encoding('utf-16-le', codecs.BOM_UTF16_LE)
    return bom


def _detect_encoding(f, ext):
    """Guess using chardet and using memory map."""

    encoding = None
    with contextlib.closing(mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)) as m:
        encoding = _has_bom(m.read(4))
        m.seek(0)
        if encoding is None:
            encoding = _special_encode_check(m, ext)
        if encoding is None:
            detector = DetectEncoding()
            m.seek(0)
            for chunk in iter(functools.partial(f.read, 4096), b""):
                detector.feed(chunk)
                if detector.done:
                    break
            detector.close()
            enc = detector.result['encoding']
            conf = detector.result['confidence']
            if enc is not None and conf >= CONFIDENCE_MAP.get(enc, MIN_CONFIDENCE):
                encoding = Encoding(
                    detector.result['encoding'],
                    None
                )
            else:
                encoding = Encoding('bin', None)
    return encoding


def inspect_bom(filename):
    """Inspect file for bom."""

    encoding = None
    try:
        with open(filename, "rb") as f:
            encoding = _has_bom(f.read(4))
    except Exception:
        # print(traceback.format_exc())
        pass
    return encoding


def guess(filename, verify=True, verify_blocks=1, verify_block_size=4096):
    """Guess the encoding and decode the content of the file."""

    encoding = None

    try:
        ext = os.path.splitext(filename)[1].lower()
        with open(filename, "rb") as f:
            if os.fstat(f.fileno()).st_size == 0:
                encoding = Encoding('ascii', None)
            encoding = _detect_encoding(f, ext)

            if verify and encoding.encode != 'bin':
                if not verify_encode(f, encoding.encode, verify_blocks, verify_block_size):
                    encoding = Encoding('bin', None)
    except Exception:
        # print(traceback.format_exc())
        pass

    # Gave it our best shot, just return binary
    return encoding


if __name__ == "__main__":
    print("Guessing encoding for %s" % sys.argv[1])
    print(guess(sys.argv[1]))
