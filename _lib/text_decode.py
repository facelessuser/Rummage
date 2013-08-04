"""
Text Decode

Licensed under MIT
Copyright (c) 2013 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
# import traceback
import codecs
import sys
import re

BINARY = 0
ASCII = 1
UTF8 = 2
UTF16 = 3
UTF32 = 4
LATIN1 = 5
CP1252 = 6
encoding_map = {
    ASCII: ("ascii", "ASCII"),
    UTF8: ("utf-8-sig", "UTF8"),
    UTF16: ("utf-16", "UTF16"),
    UTF16: ("utf-32", "UTF32"),
    LATIN1: ("latin-1", "LATIN-1"),
    CP1252: ("cp1252", "CP1252"),
    BINARY: (None, "BIN")
}

BAD_LATIN = re.compile(
    b'''
    [\x80-\x9F]  # Invalid LATIN-1 Chars
    '''
)

BAD_ASCII = re.compile(
    b'''
    (
        [\x00-\x08] |  # ASCII Control Chars
        [\x0B\x0C]  |  # ASCII Control Chars
        [\x0E-\x1F] |  # ASCII Control Chars
        [\x7F-\xFF]    # Invalid ASCII Chars
    )
    ''',
    re.VERBOSE
)

BAD_UTF8 = re.compile(
    b'''
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
    ''',
    re.VERBOSE
)

GOOD_ASCII = re.compile(
    b'''
    \A[\x09\x0A\x0D\x20-\x7E]*\Z  # ASCII (minus control chars not commonly used)
    ''',
    re.VERBOSE
)

GOOD_UTF8 = re.compile(
    b'''
    \A(
        [\x09\x0A\x0D\x20-\x7E]           | # ASCII
        [\xC2-\xDF][\x80-\xBF]            | # non-overlong 2-byte
        \xE0[\xA0-\xBF][\x80-\xBF]        | # excluding overlongs
        [\xE1-\xEC\xEE\xEF][\x80-\xBF]{2} | # straight 3-byte
        \xED[\x80-\x9F][\x80-\xBF]        | # excluding surrogates
        \xF0[\x90-\xBF][\x80-\xBF]{2}     | # planes 1-3
        [\xF1-\xF3][\x80-\xBF]{3}         | # planes 4-15
        \xF4[\x80-\x8F][\x80-\xBF]{2}       # plane 16
    )*\Z
    ''',
    re.VERBOSE
)

UTF_BOM = re.compile(
    b"^(?:(" + codecs.BOM_UTF8 + b")|" +
    b"(" + codecs.BOM_UTF32_BE + b"|" + codecs.BOM_UTF32_LE + b")" +
    b"(" + codecs.BOM_UTF16_BE + b"|" + codecs.BOM_UTF16_LE + b"))[\x00-\xFF]*"
)

ANY_NULL_CHECK = re.compile(b"(\x00\x00+)|(\x00)")

DOUBLE_NULL_CHECK = re.compile(b"\x00{2}")


def __has_null(content):
    """
    Check if has null
    Return two kinds of checks: single null and consecutive nulls
    """

    is_null = False
    is_multi_null = False
    m = ANY_NULL_CHECK.search(content)
    if m is not None:
        is_null = True
        is_multi_null = m.group(1) is not None
    if is_null and not is_multi_null:
        is_multi_null = DOUBLE_NULL_CHECK.search(content[m.end(1):]) is not None
    return is_null, is_multi_null


def __has_bom(content):
    """
    Check for UTF8, UTF16, and UTF32 BOMS
    """

    bom = None
    length = len(content)
    m = UTF_BOM.match(content[:(4 if length >= 4 else length)])
    if m is not None:
        if m.group(1):
            bom = UTF8
        elif m.group(2):
            bom = UTF32
        elif m.group(3):
            bom = UTF16
    return bom


def guess(filename, use_ascii=True):
    """
    Guess the encoding and decode the content of the file
    """

    content = None
    encoding = None
    try:
        with open(filename, "rb") as f:
            content = f.read()
    except:
        pass
    if content is not None:
        bom = __has_bom(content)
        if bom is not None:
            encoding = bom
        else:
            single, multi = __has_null(content)
            if multi:
                # Consecutive nulls found
                # (Maybe we could try UTF32 if only two or three consecutive nulls found?)
                encoding = BINARY
            elif not single:
                # if use_ascii is True, then validate and use ascii encoding
                if use_ascii and BAD_ASCII.search(content) is None:
                    # No invalid ascii chars
                    encoding = ASCII
                if BAD_UTF8.search(content) is None:
                    # No invalid utf8 char sequences
                    encoding = UTF8
                elif BAD_LATIN.search(content) is None:
                    # No bad latin chars (I think)
                    encoding = LATIN1
                else:
                    # Well we tried everything else
                    encoding = CP1252
            elif single:
                # There were no consecutive nulls,
                # so let's give this a try
                encoding = UTF16

    if encoding is not None:
        # Try and decode
        enc, name = encoding_map[encoding]
        try:
            return unicode(content, enc), name
        except:
            pass

    # Gave it our best shot, just return binary
    return content, encoding_map[BINARY][1]


if __name__ == "__main__":
    print("Guessing encoding for %s" % sys.argv[1])
    print(guess(sys.argv[1])[1])
