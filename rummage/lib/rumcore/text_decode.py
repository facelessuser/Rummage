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
import codecs
import os
import re
import functools
from collections import namedtuple
try:
    from cchardet import UniversalDetector as CCDetect
    from chardet.universaldetector import UniversalDetector as CDetect
    DetectEncoding = CCDetect
except ImportError:  # pragma: no cover
    from chardet.universaldetector import UniversalDetector as CDetect
    DetectEncoding = CDetect
    CCDetect = None

# 30 MB: maybe this should be lower for Python?
MAX_GUESS_SIZE = 31457280
MIN_GUESS_SIZE = 512

MIN_CONFIDENCE = 0.5

CONFIDENCE_MAP = {
}

CHARDET_DEFAULT = 0
CHARDET_PYTHON = 1
CHARDET_CLIB = 2

# Middle endian encodings
# Python won't really be able to process these,
# but we'll identify them and most likely fallback to bin.
BOM_10646_UC4_3412 = b'\xFE\xFF\x00\x00'
BOM_10646_UC4_2143 = b'\x00\x00\xFF\xFE'
ENCODING_10646_UC4_3412 = "X-ISO-10646-UCS-4-3412"
ENCODING_10646_UC4_2143 = "X-ISO-10646-UCS-4-2143"

DEFAULT_ENCODING_OPTIONS = {
    "chardet_mode": CHARDET_DEFAULT,
    "bin": [
        ".bin", ".jpg", ".jpeg", ".png", ".gif", ".ttf", ".tga", ".dds",
        ".ico", ".eot", ".pdf", ".swf", ".jar", ".zip", ".exe"
    ],
    "python": [".py", ".pyw"],
    "html": [".html", ".htm", ".xhtml"],
    "xml": [".xml"]
}

RE_XML_START = re.compile(
    b'^(?:(' +
    b'<\\?xml[^>]+?>' +  # ASCII like
    b')|(' +
    re.escape('<?xml'.encode('utf-32-be')) + b'.+?' + re.escape('>'.encode('utf-32-be')) +
    b')|(' +
    re.escape('<?xml'.encode('utf-32-le')) + b'.+?' + re.escape('>'.encode('utf-32-le')) +
    b')|(' +
    re.escape('<?xml'.encode('utf-16-be')) + b'.+?' + re.escape('>'.encode('utf-16-be')) +
    b')|(' +
    re.escape('<?xml'.encode('utf-16-le')) + b'.+?' + re.escape('>'.encode('utf-16-le')) +
    b'))'
)

RE_PY_ENCODE = re.compile(
    br'^[^\r\n]*?coding[:=]\s*([-\w.]+)|[^\r\n]*?\r?\n[^\r\n]*?coding[:=]\s*([-\w.]+)'
)

RE_HTML_ENCODE = re.compile(
    br'''(?xi)
    <\s*meta(?!\s*(?:name|value)\s*=)(?:[^>]*?content\s*=[\s"']*)?(?:[^>]*?)[\s"';]*charset\s*=[\s"']*([^\s"'/>]*)
    '''
)

RE_XML_ENCODE = re.compile(br'''(?i)^<\?xml[^>]*encoding=(['"])(.*?)\1[^>]*\?>''')
RE_XML_ENCODE_U = re.compile(r'''(?i)^<\?xml[^>]*encoding=(['"])(.*?)\1[^>]*\?>''')

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
    [\xE0-\xEF].{0,1}(?:[^\x80-\xBF]|$) |
    [\xF0-\xF7].{0,2}(?:[^\x80-\xBF]|$) |
    [\xF8-\xFB].{0,3}(?:[^\x80-\xBF]|$) |
    [\xFC-\xFD].{0,4}(?:[^\x80-\xBF]|$) |
    [\xFE-\xFE].{0,5}(?:[^\x80-\xBF]|$) |
    [\x00-\x7F][\x80-\xBF]              |
    [\xC0-\xDF].[\x80-\xBF]             |
    [\xE0-\xEF]..[\x80-\xBF]            |
    [\xF0-\xF7]...[\x80-\xBF]           |
    [\xF8-\xFB]....[\x80-\xBF]          |
    [\xFC-\xFD].....[\x80-\xBF]         |
    [\xFE-\xFE]......[\x80-\xBF]        |
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


def _has_xml_encode(content):
    """Check XML encoding."""

    encode = None

    m = RE_XML_START.match(content)
    if m:
        if m.group(1):
            m2 = RE_XML_ENCODE.match(m.group(1))

            if m2:
                enc = m2.group(2).decode('ascii')

                try:
                    codecs.getencoder(enc)
                    encode = Encoding(enc, None)
                except LookupError:
                    pass
        else:
            if m.group(2):
                enc = 'utf-32-be'
                text = m.group(2)
            elif m.group(3):
                enc = 'utf-32-le'
                text = m.group(3)
            elif m.group(4):
                enc = 'utf-16-be'
                text = m.group(4)
            elif m.group(5):
                enc = 'utf-16-le'
                text = m.group(5)
            try:
                m2 = RE_XML_ENCODE_U.match(text.decode(enc))
            except Exception:  # pragma: no cover
                m2 = None

            if m2:
                enc = m2.group(2)

                try:
                    codecs.getencoder(enc)
                    encode = Encoding(enc, None)
                except Exception:
                    pass

    return encode


def _has_html_encode(content):
    """Check HTML encoding."""

    encode = None

    # Look for meta charset
    m = RE_HTML_ENCODE.search(content)
    if m:
        enc = m.group(1).decode('ascii')

        try:
            codecs.getencoder(enc)
            encode = Encoding(enc, None)
        except LookupError:
            pass
    else:
        encode = _has_xml_encode(content)

    return encode


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
    # We could assume ASCII for python files, but maybe
    # it is better to not simply assume even though that is what
    # Python will do.  I guess we are assuming if extension matches,
    # it is without a doubt encoded for use with python, but that may not be
    # the case.
    if encode is None:
        encode = Encoding('utf-8', None)
    return encode


def _special_encode_check(content, ext, ext_list):
    """Check special file type encoding."""

    encode = None
    if ext in ext_list.get('python', DEFAULT_ENCODING_OPTIONS['python']):
        encode = _has_py_encode(content)
    elif ext in ext_list.get('html', DEFAULT_ENCODING_OPTIONS['html']):
        encode = _has_html_encode(content)
    elif ext in ext_list.get('xml', DEFAULT_ENCODING_OPTIONS['xml']):
        encode = _has_xml_encode(content)

    return encode


def _is_binary_ext(ext, ext_list):
    """Check if binary extension."""

    encode = None
    if ext in ext_list.get('bin', DEFAULT_ENCODING_OPTIONS['bin']):
        encode = Encoding('bin', None)
    return encode


def _is_binary(content):
    """Search for triple null."""

    return b'\x00' in content


def _is_ascii(content):
    """Check for invalid ASCII."""

    return RE_BAD_ASCII.search(content) is None


def _is_utf8(content):
    """Check for invalid `utf-8`."""

    return RE_BAD_UTF8.search(content) is None


def _is_very_small(size):
    """Check if content is very small."""

    return size <= MIN_GUESS_SIZE


def _is_very_large(size):
    """Check if content is very large."""

    return size >= MAX_GUESS_SIZE


def _simple_detect(m):
    """Do a quick check for ASCII or `utf-8`."""

    encoding = None

    if _is_ascii(m):
        encoding = Encoding('ascii', None)
    elif encoding is None and _is_utf8(m):
        encoding = Encoding('utf-8', None)
    return encoding


def has_bom(content):
    """Check for `UTF8`, `UTF16`, and `UTF32` BOMs."""

    bom = None
    if content.startswith(codecs.BOM_UTF8):
        bom = Encoding('utf-8', codecs.BOM_UTF8)
    elif content == codecs.BOM_UTF32_BE:
        bom = Encoding('utf-32-be', codecs.BOM_UTF32_BE)
    elif content == codecs.BOM_UTF32_LE:
        bom = Encoding('utf-32-le', codecs.BOM_UTF32_LE)
    elif content == BOM_10646_UC4_3412:
        bom = Encoding(ENCODING_10646_UC4_3412, BOM_10646_UC4_3412)
    elif content == BOM_10646_UC4_2143:
        bom = Encoding(ENCODING_10646_UC4_2143, BOM_10646_UC4_2143)
    elif content.startswith(codecs.BOM_UTF16_BE):
        bom = Encoding('utf-16-be', codecs.BOM_UTF16_BE)
    elif content.startswith(codecs.BOM_UTF16_LE):
        bom = Encoding('utf-16-le', codecs.BOM_UTF16_LE)

    # It is doubtful we have an encoder that can handle these middle endian
    # encodings, but lets give it a try and default to bin if nothing is found.
    # Not sure who'd use these encodings anyways.
    if bom and bom.encode in (ENCODING_10646_UC4_2143, ENCODING_10646_UC4_3412):
        try:
            codecs.getencoder(bom.encode)
        except Exception:
            bom = Encoding('bin', None)

    return bom


def _detect_encoding(f, ext, file_size, encoding_options=None):
    """Guess using `chardet` and using memory map."""

    # Check for BOMs
    encoding = has_bom(f.read(4))
    f.seek(0)

    # Is binary extension
    if encoding is None:
        encoding = _is_binary_ext(ext, encoding_options)

    if encoding is None:
        # Check file extensions
        header = f.read(1024)
        encoding = _special_encode_check(header, ext, encoding_options)

        # Check file size, if zero, assume ASCII
        if encoding is None and file_size == 0:
            encoding = Encoding('ascii', None)

        # Check start of file if there is a high likely hood of being a binary file.
        if encoding is None and _is_binary(header):
            encoding = Encoding('bin', None)

        # If content is very small, let's try and do a a `utf-8` and ASCII check
        # before giving it to `chardet`.  `chardet` doesn't work well on small buffers.
        if encoding is None and _is_very_small(file_size):
            encoding = _simple_detect(header)
        # Well, we tried everything else, lets give it to `chardet` and cross our fingers.
        if encoding is None:
            chardet_mode = encoding_options.get('chardet_mode', CHARDET_DEFAULT)
            if chardet_mode == CHARDET_DEFAULT:
                detector = DetectEncoding()
            elif chardet_mode == CHARDET_CLIB and CCDetect is not None:
                detector = CCDetect()
            else:
                detector = CDetect()
            enc = None
            conf = None
            detector.feed(header)
            # No need to force this to be covered as it its just more feeding detector.
            if not detector.done:  # pragma: no cover
                for chunk in iter(functools.partial(f.read, 4096), b""):
                    detector.feed(chunk)
                    if detector.done:

                        break
            detector.close()
            result = detector.result

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


def _detect_bfr_encoding(bfr, buffer_size, encoding_options=None):
    """Guess using `chardet`."""

    encoding = has_bom(bfr[:4])
    if encoding is None:
        header = bfr[:1024]
        if encoding is None and _is_binary(header):
            encoding = Encoding('bin', None)
        if encoding is None and _is_very_small(buffer_size):
            encoding = _simple_detect(bfr)
        if encoding is None:
            chardet_mode = encoding_options.get('chardet_mode', CHARDET_DEFAULT)
            if chardet_mode == CHARDET_DEFAULT:
                detector = DetectEncoding()
            elif chardet_mode == CHARDET_CLIB and CCDetect is not None:
                detector = CCDetect()
            else:
                detector = CDetect()
            enc = None
            conf = None
            detector.feed(header)
            # No need to force this to be covered as it its just more feeding detector.
            if not detector.done:  # pragma: no cover
                start = 1024
                end = start + 1024
                while start < buffer_size:
                    detector.feed(bfr[start:end])
                    start = end
                    end = start + 1024
                    if detector.done:
                        break
            detector.close()
            result = detector.result

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
    """Inspect file for BOM."""

    encoding = None
    try:
        with open(filename, "rb") as f:
            encoding = has_bom(f.read(4))
    except Exception:  # pragma: no cover
        pass
    return encoding


def guess(filename, verify=True, verify_blocks=1, verify_block_size=4096, encoding_options=None):
    """Guess the encoding and decode the content of the file."""

    encoding = None

    if encoding_options is None:
        encoding_options = {}

    try:
        ext = os.path.splitext(filename)[1].lower()
        file_size = os.path.getsize(filename)
        # If the file is really big, lets just call it binary.
        # We don't have time to let Python chug through a massive file.
        if not _is_very_large(file_size):
            with open(filename, "rb") as f:
                encoding = _detect_encoding(f, ext, file_size, encoding_options)

                if verify and encoding.encode != 'bin':
                    if not verify_encode(f, encoding.encode, verify_blocks, verify_block_size):
                        encoding = Encoding('bin', None)
        else:
            encoding = Encoding('bin', None)
    except Exception:  # pragma: no cover
        pass

    # If something went wrong, we will just return 'None'
    return encoding


def sguess(bfr, encoding_options=None):
    """Guess the encoding of the buffer."""

    encoding = None

    if encoding_options is None:
        encoding_options = {}

    try:
        buffer_size = len(bfr)
        if not _is_very_large(buffer_size):
            if buffer_size == 0:
                encoding = Encoding('ascii', None)
            else:
                encoding = _detect_bfr_encoding(bfr, buffer_size, encoding_options)
        else:
            encoding = Encoding('bin', None)

    except Exception:  # pragma: no cover
        pass
    return encoding


if __name__ == "__main__":  # pragma: no cover
    import sys

    print("Guessing encoding for %s" % sys.argv[1])
    print(guess(sys.argv[1]))
