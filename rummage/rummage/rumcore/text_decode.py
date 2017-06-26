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
import codecs
import contextlib
import mmap
import os
import re
import functools
# import traceback
from chardet.universaldetector import UniversalDetector
from collections import namedtuple

# For some reason we can only mock this
# if we assign it to a variable
DetectEncoding = UniversalDetector

# 30 MB: maybe this should be lower for Python?
MAX_GUESS_SIZE = 31457280
MIN_GUESS_SIZE = 512

MIN_CONFIDENCE = 0.5

CONFIDENCE_MAP = {
}

RE_UTF_BOM = re.compile(
    b'^(?:(' +
    codecs.BOM_UTF8 +
    b')[\x00-\xFF]{,2}|(' +
    codecs.BOM_UTF32_BE +
    b')|(' +
    codecs.BOM_UTF32_LE +
    b')|(' +
    codecs.BOM_UTF16_BE +
    b')|(' +
    codecs.BOM_UTF16_LE +
    b'))'
)

RE_PY_ENCODE = re.compile(
    br'^[^\r\n]*?coding[:=]\s*([-\w.]+)|[^\r\n]*?\r?\n[^\r\n]*?coding[:=]\s*([-\w.]+)'
)

RE_IS_BIN = re.compile(
    br'\x00{2}'
)

RE_BAD_ASCII = re.compile(
    b'''(?x)
    [\x00-\x08] |  # ASCII Control Chars
    [\x0B\x0C]  |  # ASCII Control Chars
    [\x0E-\x1F] |  # ASCII Control Chars
    [\x7F-\xFF]    # Invalid ASCII Chars
    '''
)

RE_BAD_UTF8 = re.compile(
    b'''(?x)
    [\xE0-\xEF].{0,1}([^\x80-\xBF]|$) |
    [\xF0-\xF7].{0,2}([^\x80-\xBF]|$) |
    [\xF8-\xFB].{0,3}([^\x80-\xBF]|$) |
    [\xFC-\xFD].{0,4}([^\x80-\xBF]|$) |
    [\xFE-\xFE].{0,5}([^\x80-\xBF]|$) |
    [\x00-\x7F][\x80-\xBF]            |
    [\xC0-\xDF].[\x80-\xBF]           |
    [\xE0-\xEF]..[\x80-\xBF]          |
    [\xF0-\xF7]...[\x80-\xBF]         |
    [\xF8-\xFB]....[\x80-\xBF]        |
    [\xFC-\xFD].....[\x80-\xBF]       |
    [\xFE-\xFE]......[\x80-\xBF]      |
    ^[\x80-\xBF]
    '''
)


class Encoding(namedtuple('Encoding', ['encode', 'bom'])):
    """BOM object."""


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


def _has_py_encode(content):
    """Check python encoding."""

    encode = None

    m = RE_PY_ENCODE.match(content)
    if m:
        if m.group(1):
            enc = m.group(1).decode('ascii')
        elif m.group(2):
            enc = m.group(2).decode('ascii')
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
        encode = Encoding('ascii', None)
    return encode


def _special_encode_check(content, ext):
    """Check special file type encoding."""

    encode = None
    if ext in ('.py', '.pyw'):
        encode = _has_py_encode(content)
    return encode


def _is_binary(content):
    """Search for triple null."""

    return RE_IS_BIN.search(content) is not None


def _is_ascii(content):
    """Check for invalid ascii."""

    return RE_BAD_ASCII.search(content) is None


def _is_utf8(content):
    """Check for invalid utf-8."""

    return RE_BAD_UTF8.search(content) is None


def _is_very_small(size):
    """Check if content is very small."""

    return size <= MIN_GUESS_SIZE


def _is_very_large(size):
    """Check if content is very large."""

    return size >= MAX_GUESS_SIZE


def _simple_detect(m):
    """Do a quick check for ascii or utf-8."""

    encoding = None

    if _is_ascii(m):
        encoding = Encoding('ascii', None)
    elif encoding is None and _is_utf8(m):
        encoding = Encoding('utf-8', None)
    return encoding


def has_bom(content):
    """Check for UTF8, UTF16, and UTF32 BOMS."""

    bom = None
    m = RE_UTF_BOM.match(content)
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


def _detect_encoding(f, ext, file_size):
    """Guess using chardet and using memory map."""

    encoding = None
    with contextlib.closing(mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)) as m:
        # Check for boms
        encoding = has_bom(m.read(4))
        m.seek(0)
        # Check start of file if there is a high likely hood of being a binary file.
        if encoding is None and _is_binary(m.read(1024)):
            encoding = Encoding('bin', None)
        m.seek(0)
        # Check file extensions
        if encoding is None:
            encoding = _special_encode_check(m, ext)
        # If content is very small, let's try and do a a utf-8 and ascii check
        # before giving it to chardet.  Chardet doesn't work well on small buffers.
        if encoding is None and _is_very_small(file_size):
            encoding = _simple_detect(m)
        # Well, we tried everything else, lets give it to chardet and cross our fingers.
        if encoding is None:
            enc = None
            conf = None
            detector = DetectEncoding()
            m.seek(0)
            for chunk in iter(functools.partial(f.read, 4096), b""):
                detector.feed(chunk)
                if detector.done:
                    break
            result = detector.close()

            if result is not None:
                enc = result['encoding']
                conf = result['confidence']

            if enc is not None and conf >= CONFIDENCE_MAP.get(enc, MIN_CONFIDENCE):
                encoding = Encoding(
                    enc,
                    None
                )
            else:
                encoding = Encoding('bin', None)
    return encoding


def _detect_bfr_encoding(bfr, buffer_size):
    """Guess using chardet."""

    encoding = has_bom(bfr[:4])
    if encoding is None and _is_binary(bfr[:1024]):
        encoding = Encoding('bin', None)
    if encoding is None and _is_very_small(buffer_size):
        encoding = _simple_detect(bfr)
    if encoding is None:
        enc = None
        conf = None
        detector = DetectEncoding()
        start = 0
        end = start + 1024
        while start < buffer_size:
            detector.feed(bfr[start:end])
            start = end
            end = start + 1024
            if detector.done:
                break
        result = detector.close()

        if result is not None:
            enc = result['encoding']
            conf = result['confidence']

        if enc is not None and conf >= CONFIDENCE_MAP.get(enc, MIN_CONFIDENCE):
            encoding = Encoding(
                enc,
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
            encoding = has_bom(f.read(4))
    except Exception:  # pragma: no cover
        # print(traceback.format_exc())
        pass
    return encoding


def guess(filename, verify=True, verify_blocks=1, verify_block_size=4096):
    """Guess the encoding and decode the content of the file."""

    encoding = None

    try:
        ext = os.path.splitext(filename)[1].lower()
        file_size = os.path.getsize(filename)
        # If the file is really big, lets just call it binary.
        # We dont' have time to let Python chug through a massive file.
        if not _is_very_large(file_size):
            with open(filename, "rb") as f:
                if file_size == 0:
                    encoding = Encoding('ascii', None)
                else:
                    encoding = _detect_encoding(f, ext, file_size)

                if verify and encoding.encode != 'bin':
                    if not verify_encode(f, encoding.encode, verify_blocks, verify_block_size):
                        encoding = Encoding('bin', None)
        else:
            encoding = Encoding('bin', None)
    except Exception:  # pragma: no cover
        # print(traceback.format_exc())
        pass

    # If something went wrong, we will just return 'None'
    return encoding


def sguess(bfr):
    """Guess the encoding of the buffer."""

    encoding = None

    try:
        buffer_size = len(bfr)
        if not _is_very_large(buffer_size):
            if buffer_size == 0:
                encoding = Encoding('ascii', None)
            else:
                encoding = _detect_bfr_encoding(bfr, buffer_size)
        else:
            encoding = Encoding('bin', None)

    except Exception:  # pragma: no cover
        # print(traceback.format_exc())
        pass
    return encoding


if __name__ == "__main__":  # pragma: no cover
    import sys

    print("Guessing encoding for %s" % sys.argv[1])
    print(guess(sys.argv[1]))
