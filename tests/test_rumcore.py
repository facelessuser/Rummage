# -*- coding: utf-8 -*-
"""Tests for rumcore."""
from __future__ import unicode_literals
import unittest
import pytest
import os
import re
import regex
import codecs
import datetime
import tempfile
import textwrap
from backrefs import bre
from backrefs import bregex
from rummage.lib import rumcore as rc
from rummage.lib import util
from rummage.lib.util import epoch_timestamp as epoch
from rummage.lib.rumcore import text_decode as td


class TestWildcard(unittest.TestCase):
    """Test wildcard pattern parsing."""

    def test_wildcard_parsing(self):
        """Test wildcard parsing."""

        p1, p2 = rc.Wildcard2Regex('*test[a-z]?|*test2[a-z]?|-test[!a-z]|-test[!-|a-z]').translate()
        if util.PY36:
            self.assertEqual(p1.pattern, r'(?s:.*test[a-z].|.*test2[a-z].)\Z')
            self.assertEqual(p2.pattern, r'(?s:test[^a-z]|test[^\-\|a-z])\Z')
        else:
            self.assertEqual(p1.pattern, r'(?ms)(?:.*test[a-z].|.*test2[a-z].)\Z')
            self.assertEqual(p2.pattern, r'(?ms)(?:test[^a-z]|test[^\-\|a-z])\Z')

        p1, p2 = rc.Wildcard2Regex('test[]][!][][]').translate()
        if util.PY36:
            self.assertEqual(p1.pattern, r'(?s:test[]][^][]\[\])\Z')
            self.assertEqual(p2.pattern, r'(?s:)\Z')
        else:
            self.assertEqual(p1.pattern, r'(?ms)(?:test[]][^][]\[\])\Z')
            self.assertEqual(p2.pattern, r'(?ms)(?:)\Z')

        p1, p2 = rc.Wildcard2Regex('test[!]').translate()
        if util.PY36:
            self.assertEqual(p1.pattern, r'(?s:test\[\!\])\Z')
            self.assertEqual(p2.pattern, r'(?s:)\Z')
        else:
            self.assertEqual(p1.pattern, r'(?ms)(?:test\[\!\])\Z')
            self.assertEqual(p2.pattern, r'(?ms)(?:)\Z')

        p1, p2 = rc.Wildcard2Regex('|test|').translate()
        if util.PY36:
            self.assertEqual(p1.pattern, r'(?s:|test|)\Z')
            self.assertEqual(p2.pattern, r'(?s:)\Z')
        else:
            self.assertEqual(p1.pattern, r'(?ms)(?:|test|)\Z')
            self.assertEqual(p2.pattern, r'(?ms)(?:)\Z')

        p1, p2 = rc.Wildcard2Regex('-|-test|-').translate()
        if util.PY36:
            self.assertEqual(p1.pattern, r'(?s:.*)\Z')
            self.assertEqual(p2.pattern, r'(?s:|test|)\Z')
        else:
            self.assertEqual(p1.pattern, r'(?ms)(?:.*)\Z')
            self.assertEqual(p2.pattern, r'(?ms)(?:|test|)\Z')

        p1, p2 = rc.Wildcard2Regex('test[^chars]').translate()
        if util.PY36:
            self.assertEqual(p1.pattern, r'(?s:test[\^chars])\Z')
            self.assertEqual(p2.pattern, r'(?s:)\Z')
        else:
            self.assertEqual(p1.pattern, r'(?ms)(?:test[\^chars])\Z')
            self.assertEqual(p2.pattern, r'(?ms)(?:)\Z')

        p1 = rc.Wildcard2Regex(r'test[^\-\&]').translate()[0]
        if util.PY36:
            self.assertEqual(p1.pattern, r'(?s:test[\^\\-\\\&])\Z')
        else:
            self.assertEqual(p1.pattern, r'(?ms)(?:test[\^\\-\\\&])\Z')

        p1 = rc.Wildcard2Regex(r'\*\?\|\[\]').translate()[0]
        if util.PY36:
            self.assertEqual(p1.pattern, r'(?s:\\.*\\.\\|\\[\\])\Z')
        else:
            self.assertEqual(p1.pattern, r'(?ms)(?:\\.*\\.\\|\\[\\])\Z')

        p1 = rc.Wildcard2Regex(r'\\u0300').translate()[0]
        if util.PY36:
            self.assertEqual(p1.pattern, r'(?s:\\u0300)\Z')
        else:
            self.assertEqual(p1.pattern, r'(?ms)(?:\\u0300)\Z')

        self.assertTrue(rc.Wildcard2Regex(r'test\test').translate()[0].match('test\test') is not None)
        self.assertTrue(rc.Wildcard2Regex(r'test\\test').translate()[0].match('test\\test') is not None)
        self.assertTrue(rc.Wildcard2Regex(r'test\m').translate()[0].match('test\\m') is not None)
        self.assertTrue(rc.Wildcard2Regex(r'test\[a-z]').translate()[0].match('test\\b') is not None)
        self.assertTrue(rc.Wildcard2Regex(r'test\\[a-z]').translate()[0].match('test\\b') is not None)
        self.assertTrue(rc.Wildcard2Regex('[[]').translate()[0].match('[') is not None)
        self.assertTrue(rc.Wildcard2Regex('[a&&b]').translate()[0].match('&') is not None)
        self.assertTrue(rc.Wildcard2Regex('[a||b]').translate()[0].match('|') is not None)
        self.assertTrue(rc.Wildcard2Regex('[a~~b]').translate()[0].match('~') is not None)
        self.assertTrue(rc.Wildcard2Regex('[a-z+--A-Z]').translate()[0].match(',') is not None)
        self.assertTrue(rc.Wildcard2Regex('[a-z--/A-Z]').translate()[0].match('.') is not None)

    def test_wildcard_character_notation(self):
        """Test wildcard character notations."""

        p1, p2 = rc.Wildcard2Regex(r'test\x70\u0070\160\N{LATIN SMALL LETTER P}').translate()
        if util.PY36:
            self.assertEqual(p1.pattern, r'(?s:test\x70\u0070\160\160)\Z')
            self.assertEqual(p2.pattern, r'(?s:)\Z')
        else:
            self.assertEqual(p1.pattern, r'(?ms)(?:test\x70\u0070\160\160)\Z')
            self.assertEqual(p2.pattern, r'(?ms)(?:)\Z')

        p1, p2 = rc.Wildcard2Regex(r'test[\x70][\u0070][\160][\N{LATIN SMALL LETTER P}]').translate()
        if util.PY36:
            self.assertEqual(p1.pattern, r'(?s:test[\x70][\u0070][\160][\160])\Z')
            self.assertEqual(p2.pattern, r'(?s:)\Z')
        else:
            self.assertEqual(p1.pattern, r'(?ms)(?:test[\x70][\u0070][\160][\160])\Z')
            self.assertEqual(p2.pattern, r'(?ms)(?:)\Z')

        p1, p2 = rc.Wildcard2Regex(r'test\t\m').translate()
        if util.PY36:
            self.assertEqual(p1.pattern, r'(?s:test\t\\m)\Z')
            self.assertEqual(p2.pattern, r'(?s:)\Z')
        else:
            self.assertEqual(p1.pattern, r'(?ms)(?:test\t\\m)\Z')
            self.assertEqual(p2.pattern, r'(?ms)(?:)\Z')

        p1, p2 = rc.Wildcard2Regex(r'test[\]test').translate()
        if util.PY36:
            self.assertEqual(p1.pattern, r'(?s:test[\\]test)\Z')
            self.assertEqual(p2.pattern, r'(?s:)\Z')
        else:
            self.assertEqual(p1.pattern, r'(?ms)(?:test[\\]test)\Z')
            self.assertEqual(p2.pattern, r'(?ms)(?:)\Z')

        p1, p2 = rc.Wildcard2Regex('test[\\').translate()
        if util.PY36:
            self.assertEqual(p1.pattern, r'(?s:test\[\\)\Z')
            self.assertEqual(p2.pattern, r'(?s:)\Z')
        else:
            self.assertEqual(p1.pattern, r'(?ms)(?:test\[\\)\Z')
            self.assertEqual(p2.pattern, r'(?ms)(?:)\Z')

        p1, p2 = rc.Wildcard2Regex(r'test\33test').translate()
        if util.PY36:
            self.assertEqual(p1.pattern, r'(?s:test\033test)\Z')
            self.assertEqual(p2.pattern, r'(?s:)\Z')
        else:
            self.assertEqual(p1.pattern, r'(?ms)(?:test\033test)\Z')
            self.assertEqual(p2.pattern, r'(?ms)(?:)\Z')

        p1, p2 = rc.Wildcard2Regex(r'test\33').translate()
        if util.PY36:
            self.assertEqual(p1.pattern, r'(?s:test\033)\Z')
            self.assertEqual(p2.pattern, r'(?s:)\Z')
        else:
            self.assertEqual(p1.pattern, r'(?ms)(?:test\033)\Z')
            self.assertEqual(p2.pattern, r'(?ms)(?:)\Z')

        p1, p2 = rc.Wildcard2Regex(r'test\400').translate()
        if util.PY36:
            self.assertEqual(p1.pattern, r'(?s:testĀ)\Z')
            self.assertEqual(p2.pattern, r'(?s:)\Z')
        else:
            self.assertEqual(p1.pattern, r'(?ms)(?:testĀ)\Z')
            self.assertEqual(p2.pattern, r'(?ms)(?:)\Z')

        with pytest.raises(SyntaxError):
            rc.Wildcard2Regex(r'test\N').translate()

        with pytest.raises(SyntaxError):
            rc.Wildcard2Regex(r'test\Nx').translate()

        with pytest.raises(SyntaxError):
            rc.Wildcard2Regex(r'test\N{').translate()


class TestHelperFunctions(unittest.TestCase):
    """Test helper functions."""

    def test_re_flags(self):
        """Test the re flag settings."""

        default = re.ASCII

        self.assertEqual(rc._re_pattern(r"test").flags, default)
        self.assertEqual(rc._re_pattern(r"test", rc.MULTILINE).flags, re.MULTILINE | default)
        self.assertEqual(rc._re_pattern(r"test", rc.DOTALL).flags, re.DOTALL | default)
        self.assertEqual(rc._re_pattern(r"test", rc.IGNORECASE).flags, re.IGNORECASE | default)
        self.assertEqual(rc._re_pattern(r"test", rc.UNICODE).flags, re.UNICODE)
        self.assertEqual(rc._re_pattern(br"test", rc.UNICODE, binary=True).flags, default)
        self.assertEqual(
            rc._re_pattern(r"test", rc.UNICODE | rc.DOTALL | rc.IGNORECASE | rc.MULTILINE).flags,
            re.UNICODE | re.DOTALL | re.IGNORECASE | re.MULTILINE
        )

    def test_re_literal_flags(self):
        """Test the literal re flags."""

        default = re.ASCII

        self.assertEqual(rc._re_literal_pattern(r"test").flags, default)
        self.assertEqual(rc._re_literal_pattern(r"test", rc.IGNORECASE).flags, re.IGNORECASE | default)
        self.assertEqual(
            rc._re_literal_pattern(r"test", rc.UNICODE | rc.DOTALL | rc.IGNORECASE | rc.MULTILINE).flags,
            re.IGNORECASE | re.UNICODE
        )

    def test_bre_flags(self):
        """Test the bre flag settings."""

        default = re.ASCII

        self.assertEqual(rc._bre_pattern(r"test").flags, default)
        self.assertEqual(rc._bre_pattern(r"test", rc.MULTILINE).flags, bre.MULTILINE | default)
        self.assertEqual(rc._bre_pattern(r"test", rc.DOTALL).flags, bre.DOTALL | default)
        self.assertEqual(rc._bre_pattern(r"test", rc.IGNORECASE).flags, bre.IGNORECASE | default)
        self.assertEqual(rc._bre_pattern(r"test", rc.UNICODE).flags, bre.UNICODE)
        self.assertEqual(rc._bre_pattern(br"test", rc.UNICODE, binary=True).flags, default)
        self.assertEqual(
            rc._bre_pattern(r"test", rc.UNICODE | rc.DOTALL | rc.IGNORECASE | rc.MULTILINE).flags,
            bre.UNICODE | bre.DOTALL | bre.IGNORECASE | bre.MULTILINE
        )

    def test_regex_flags(self):
        """Test the re flag settings."""

        self.assertEqual(rc._regex_pattern(r"test").flags, regex.ASCII | regex.V0)
        self.assertEqual(rc._regex_pattern(r"test", rc.VERSION1).flags, regex.ASCII | regex.V1 | regex.FULLCASE)
        self.assertEqual(
            rc._regex_pattern(r"test", rc.FULLCASE).flags, regex.ASCII | regex.V0 | regex.FULLCASE
        )
        self.assertEqual(rc._regex_pattern(r"test", rc.MULTILINE).flags, regex.ASCII | regex.V0 | regex.MULTILINE)
        self.assertEqual(rc._regex_pattern(r"test", rc.DOTALL).flags, regex.ASCII | regex.V0 | regex.DOTALL)
        self.assertEqual(rc._regex_pattern(r"test", rc.IGNORECASE).flags, regex.ASCII | regex.V0 | regex.IGNORECASE)
        self.assertEqual(rc._regex_pattern(r"test", rc.WORD).flags, regex.ASCII | regex.V0 | regex.WORD)
        self.assertEqual(rc._regex_pattern(r"test", rc.POSIX).flags, regex.ASCII | regex.V0 | regex.POSIX)
        self.assertEqual(rc._regex_pattern(r"test", rc.BESTMATCH).flags, regex.ASCII | regex.V0 | regex.BESTMATCH)
        self.assertEqual(rc._regex_pattern(r"test", rc.ENHANCEMATCH).flags, regex.ASCII | regex.V0 | regex.ENHANCEMATCH)
        self.assertEqual(rc._regex_pattern(r"test", rc.REVERSE).flags, regex.ASCII | regex.V0 | regex.REVERSE)
        self.assertEqual(rc._regex_pattern(r"test", rc.UNICODE).flags, regex.UNICODE | regex.V0)
        self.assertEqual(rc._regex_pattern(br"test", rc.UNICODE, binary=True).flags, regex.ASCII | regex.V0)
        self.assertEqual(
            rc._regex_pattern(
                r"test",
                rc.DOTALL | rc.IGNORECASE | rc.MULTILINE | rc.WORD |
                rc.BESTMATCH | rc.ENHANCEMATCH | rc.REVERSE | rc.FULLCASE | rc.POSIX
            ).flags,
            regex.V0 | regex.ASCII | regex.DOTALL | regex.IGNORECASE | regex.MULTILINE |
            regex.WORD | regex.ENHANCEMATCH | regex.BESTMATCH | regex.REVERSE | regex.FULLCASE |
            regex.POSIX
        )
        self.assertEqual(
            rc._regex_pattern(
                r"test",
                rc.UNICODE | rc.DOTALL | rc.IGNORECASE | rc.MULTILINE | rc.FULLCASE |
                rc.WORD | rc.BESTMATCH | rc.ENHANCEMATCH | rc.REVERSE | rc.VERSION1 | rc.POSIX
            ).flags,
            regex.V1 | regex.UNICODE | regex.DOTALL | regex.IGNORECASE | regex.MULTILINE |
            regex.WORD | regex.ENHANCEMATCH | regex.BESTMATCH | regex.REVERSE | regex.FULLCASE |
            regex.POSIX
        )

    def test_regex_literal_flags(self):
        """Test the literal re flags."""

        self.assertEqual(
            rc._regex_literal_pattern(r"test").flags, regex.V0 | regex.ASCII
        )
        self.assertEqual(
            rc._regex_literal_pattern(r"test", rc.IGNORECASE).flags, regex.V0 | regex.ASCII | regex.IGNORECASE
        )
        self.assertEqual(
            rc._regex_literal_pattern(
                r"test",
                rc.UNICODE | rc.DOTALL | rc.IGNORECASE | rc.MULTILINE |
                rc.WORD | rc.BESTMATCH | rc.ENHANCEMATCH | rc.REVERSE | rc.FULLCASE | rc.VERSION0
            ).flags,
            regex.IGNORECASE | regex.V0 | regex.UNICODE | regex.FULLCASE
        )

    def test_bregex_flags(self):
        """Test the re flag settings."""

        self.assertEqual(rc._bregex_pattern(r"test").flags, bregex.ASCII | bregex.V0)
        self.assertEqual(rc._bregex_pattern(r"test", rc.VERSION1).flags, bregex.ASCII | bregex.V1 | bregex.FULLCASE)
        self.assertEqual(
            rc._bregex_pattern(r"test", rc.FULLCASE).flags, bregex.ASCII | bregex.V0 | bregex.FULLCASE
        )
        self.assertEqual(rc._bregex_pattern(r"test", rc.MULTILINE).flags, bregex.ASCII | bregex.V0 | bregex.MULTILINE)
        self.assertEqual(rc._bregex_pattern(r"test", rc.DOTALL).flags, bregex.ASCII | bregex.V0 | bregex.DOTALL)
        self.assertEqual(rc._bregex_pattern(r"test", rc.IGNORECASE).flags, bregex.ASCII | bregex.V0 | bregex.IGNORECASE)
        self.assertEqual(rc._bregex_pattern(r"test", rc.WORD).flags, bregex.ASCII | bregex.V0 | bregex.WORD)
        self.assertEqual(rc._regex_pattern(r"test", rc.POSIX).flags, regex.ASCII | regex.V0 | bregex.POSIX)
        self.assertEqual(rc._bregex_pattern(r"test", rc.BESTMATCH).flags, bregex.ASCII | bregex.V0 | bregex.BESTMATCH)
        self.assertEqual(
            rc._bregex_pattern(r"test", rc.ENHANCEMATCH).flags, bregex.ASCII | bregex.V0 | bregex.ENHANCEMATCH
        )
        self.assertEqual(rc._bregex_pattern(r"test", rc.REVERSE).flags, bregex.ASCII | bregex.V0 | bregex.REVERSE)
        self.assertEqual(rc._bregex_pattern(r"test", rc.UNICODE).flags, bregex.UNICODE | bregex.V0)
        self.assertEqual(rc._bregex_pattern(br"test", rc.UNICODE, binary=True).flags, bregex.ASCII | bregex.V0)
        self.assertEqual(
            rc._bregex_pattern(
                r"test",
                rc.DOTALL | rc.IGNORECASE | rc.MULTILINE | rc.WORD |
                rc.BESTMATCH | rc.ENHANCEMATCH | rc.REVERSE | rc.FULLCASE | rc.POSIX
            ).flags,
            bregex.V0 | bregex.ASCII | bregex.DOTALL | bregex.IGNORECASE | bregex.MULTILINE |
            bregex.WORD | bregex.ENHANCEMATCH | bregex.BESTMATCH | bregex.REVERSE | bregex.FULLCASE |
            bregex.POSIX
        )
        self.assertEqual(
            rc._bregex_pattern(
                r"test",
                rc.UNICODE | rc.DOTALL | rc.IGNORECASE | rc.MULTILINE | rc.FULLCASE |
                rc.WORD | rc.BESTMATCH | rc.ENHANCEMATCH | rc.REVERSE | rc.VERSION1 | rc.POSIX
            ).flags,
            bregex.V1 | bregex.UNICODE | bregex.DOTALL | bregex.IGNORECASE | bregex.MULTILINE |
            bregex.WORD | bregex.ENHANCEMATCH | bregex.BESTMATCH | bregex.REVERSE | bregex.FULLCASE |
            bregex.POSIX
        )

    def test_exception(self):
        """Test retrieval of exceptions."""

        try:
            test = 3 + "3"
        except TypeError:
            test = None
            error = rc.get_exception()
        self.assertTrue(test is None)
        self.assertTrue(error[0].startswith('TypeError'))


class TestRummageFileContent(unittest.TestCase):
    """Tests for _RummageFileContent."""

    def test_string_bin(self):
        """Test passing a binary string."""

        encoding = td.Encoding('bin', None)
        rfc = rc._RummageFileContent("buffer", None, encoding, b'test')
        with rfc as bfr:
            text = bfr
        self.assertEqual(rfc.encoding.encode, 'bin')
        self.assertEqual(text, b'test')

    def test_string_unicode(self):
        """Test passing a binary string."""

        encoding = td.Encoding('unicode', None)
        rfc = rc._RummageFileContent("buffer", None, encoding, 'test')
        with rfc as bfr:
            text = bfr
        self.assertEqual(rfc.encoding.encode, 'unicode')
        self.assertEqual(text, 'test')

    def test_bin(self):
        """Test bin file."""

        encoding = td.Encoding('bin', None)
        name = "tests/encodings/binary.txt"
        rfc = rc._RummageFileContent(name, os.path.getsize(name), encoding)
        with rfc as f:
            text = f[:]
        with open(name, 'rb') as f:
            text2 = f.read()
        self.assertEqual(rfc.encoding.encode, 'bin')
        self.assertEqual(text, text2)

    def test_utf8(self):
        """Test utf-8 file."""

        encoding = td.Encoding('utf-8', codecs.BOM_UTF8)
        name = "tests/encodings/utf8_bom.txt"
        rfc = rc._RummageFileContent(name, os.path.getsize(name), encoding)
        with rfc as f:
            text = f[:]
        with codecs.open(name, 'r', encoding='utf-8-sig') as f:
            text2 = f.read()
        self.assertEqual(rfc.encoding.encode, 'utf-8')
        self.assertEqual(text, text2)

    def test_utf16(self):
        """Test utf-16 file."""

        encoding = td.Encoding('utf-16-be', codecs.BOM_UTF16_BE)
        name = "tests/encodings/utf16_be_bom.txt"
        rfc = rc._RummageFileContent(name, os.path.getsize(name), encoding)
        with rfc as f:
            text = f[:]
        with codecs.open(name, 'r', encoding='utf-16') as f:
            text2 = f.read()
        self.assertEqual(rfc.encoding.encode, 'utf-16-be')
        self.assertEqual(text, text2)

    def test_utf32(self):
        """Test utf-8 file."""

        encoding = td.Encoding('utf-32-be', codecs.BOM_UTF32_BE)
        name = "tests/encodings/utf32_be_bom.txt"
        rfc = rc._RummageFileContent(name, os.path.getsize(name), encoding)
        with rfc as f:
            text = f[:]
        with codecs.open(name, 'r', encoding='utf-32') as f:
            text2 = f.read()
        self.assertEqual(rfc.encoding.encode, 'utf-32-be')
        self.assertEqual(text, text2)

    def test_rummageexception(self):
        """Test RummageException with file."""

        encoding = td.Encoding('ascii', None)
        name = "tests/encodings/does_not_exist.txt"
        rfc = rc._RummageFileContent(name, 10, encoding)
        self.assertRaises(rc.RummageException, rfc.__enter__)

    def test_bin_rummageexception(self):
        """Test RummageException with a bin file."""

        encoding = td.Encoding('bin', None)
        name = "tests/encodings/does_not_exist.txt"
        rfc = rc._RummageFileContent(name, 10, encoding)
        self.assertRaises(rc.RummageException, rfc.__enter__)

    def test_wrong(self):
        """Test wrong encoding failure."""

        encoding = td.Encoding('utf-32-be', codecs.BOM_UTF32_BE)
        name = "tests/encodings/utf8.txt"
        rfc = rc._RummageFileContent(name, os.path.getsize(name), encoding)
        with rfc as f:
            text = f[:]
        with open(name, 'rb') as f:
            text2 = f.read()
        self.assertEqual(rfc.encoding.encode, 'bin')
        self.assertEqual(text, text2)


class TestDirWalker(unittest.TestCase):
    """Test the _DirWalker class."""

    def setUp(self):
        """Setup the tests."""

        self.errors = []
        self.skipped = []
        self.files = []

    def crawl_files(self, walker):
        """Crawl the files."""

        for f in walker.run():
            if hasattr(f, 'skipped') and f.skipped:
                self.skipped.append(f)
            elif f.error:
                self.errors.append(f)
            else:
                self.files.append(f)

    def test_non_recursive(self):
        """Test non-recursive search."""

        walker = rc._DirWalker(
            'tests/dir_walker',
            '*.txt', False,
            None, False,
            False, False,
            None, None, None,
            None, False
        )

        self.crawl_files(walker)

        self.assertEqual(len(self.errors), 0)
        self.assertEqual(len(self.skipped), 3)
        self.assertEqual(len(self.files), 1)
        self.assertEqual(os.path.basename(self.files[0].name), 'a.txt')

    def test_non_recursive_inverse(self):
        """Test non-recursive inverse search."""

        walker = rc._DirWalker(
            'tests/dir_walker',
            '*.*|-*.file', False,
            None, False,
            False, False,
            None, None, None,
            None, False
        )

        self.crawl_files(walker)

        self.assertEqual(len(self.errors), 0)
        self.assertEqual(len(self.skipped), 2)
        self.assertEqual(len(self.files), 2)

    def test_non_recursive_inverse_backup(self):
        """Test non-recursive inverse search with backup."""

        walker = rc._DirWalker(
            'tests/dir_walker',
            '*.*|-*.file', False,
            None, False,
            False, False,
            None, None, None,
            'rum-bak', False
        )

        self.crawl_files(walker)

        self.assertEqual(len(self.errors), 0)
        self.assertEqual(len(self.skipped), 3)
        self.assertEqual(len(self.files), 1)

    def test_recursive(self):
        """Test non-recursive search."""

        walker = rc._DirWalker(
            'tests/dir_walker',
            '*.txt', False,
            None, False,
            True, False,
            None, None, None,
            None, False
        )

        self.crawl_files(walker)

        self.assertEqual(len(self.errors), 0)
        self.assertEqual(len(self.skipped), 3)
        self.assertEqual(len(self.files), 1)
        self.assertEqual(os.path.basename(self.files[0].name), 'a.txt')

    def test_recursive_hidden(self):
        """Test non-recursive search."""

        walker = rc._DirWalker(
            'tests/dir_walker',
            '*.txt', False,
            None, False,
            True, True,
            None, None, None,
            None, False
        )

        self.crawl_files(walker)

        self.assertEqual(len(self.errors), 0)
        self.assertEqual(len(self.skipped), 4)
        self.assertEqual(len(self.files), 2)
        self.assertEqual(os.path.basename(sorted(self.files)[0].name), 'a.txt')

    def test_recursive_hidden_folder_exclude(self):
        """Test non-recursive search."""

        walker = rc._DirWalker(
            'tests/dir_walker',
            '*.txt', False,
            '.hidden', False,
            True, True,
            None, None, None,
            None, False
        )

        self.crawl_files(walker)

        self.assertEqual(len(self.errors), 0)
        self.assertEqual(len(self.skipped), 3)
        self.assertEqual(len(self.files), 1)
        self.assertEqual(os.path.basename(self.files[0].name), 'a.txt')

    def test_recursive_hidden_folder_exclude_inverse(self):
        """Test non-recursive search with inverse."""

        walker = rc._DirWalker(
            'tests/dir_walker',
            '*.txt', False,
            '*|-.hidden', False,
            True, True,
            None, None, None,
            None, False
        )

        self.crawl_files(walker)

        self.assertEqual(len(self.errors), 0)
        self.assertEqual(len(self.skipped), 4)
        self.assertEqual(len(self.files), 2)
        self.assertEqual(os.path.basename(sorted(self.files)[0].name), 'a.txt')

    def test_recursive_hidden_re_folder_exclude(self):
        """Test non-recursive search."""

        walker = rc._DirWalker(
            'tests/dir_walker',
            '*.txt', False,
            r'\.hidden', True,
            True, True,
            None, None, None,
            None, False
        )

        self.crawl_files(walker)

        self.assertEqual(len(self.errors), 0)
        self.assertEqual(len(self.skipped), 3)
        self.assertEqual(len(self.files), 1)
        self.assertEqual(os.path.basename(self.files[0].name), 'a.txt')

    def test_re(self):
        """Test regex search."""

        walker = rc._DirWalker(
            'tests/dir_walker',
            r'.*?\.txt', True,
            None, False,
            False, False,
            None, None, None,
            None, False
        )

        self.crawl_files(walker)

        self.assertEqual(walker.regex_mode, rc.RE_MODE)
        self.assertEqual(len(self.errors), 0)
        self.assertEqual(len(self.skipped), 3)
        self.assertEqual(len(self.files), 1)
        self.assertEqual(os.path.basename(sorted(self.files)[0].name), 'a.txt')

    def test_bre(self):
        """Test bre search."""

        walker = rc._DirWalker(
            'tests/dir_walker',
            r'.*?\.txt', True,
            None, False,
            False, False,
            None, None, None,
            None, False,
            rc.BRE_MODE
        )

        self.crawl_files(walker)

        self.assertEqual(walker.regex_mode, rc.BRE_MODE)
        self.assertEqual(len(self.errors), 0)
        self.assertEqual(len(self.skipped), 3)
        self.assertEqual(len(self.files), 1)
        self.assertEqual(os.path.basename(sorted(self.files)[0].name), 'a.txt')

    def test_regex(self):
        """Test regex search."""

        walker = rc._DirWalker(
            'tests/dir_walker',
            r'.*?\.txt', True,
            None, False,
            False, False,
            None, None, None,
            None, False,
            rc.REGEX_MODE
        )

        self.crawl_files(walker)

        self.assertEqual(walker.regex_mode, rc.REGEX_MODE)
        self.assertEqual(len(self.errors), 0)
        self.assertEqual(len(self.skipped), 3)
        self.assertEqual(len(self.files), 1)
        self.assertEqual(os.path.basename(sorted(self.files)[0].name), 'a.txt')

    def test_bregex(self):
        """Test bregex search."""

        walker = rc._DirWalker(
            'tests/dir_walker',
            r'.*?\.txt', True,
            None, False,
            False, False,
            None, None, None,
            None, False,
            rc.BREGEX_MODE
        )

        self.crawl_files(walker)

        self.assertEqual(walker.regex_mode, rc.BREGEX_MODE)
        self.assertEqual(len(self.errors), 0)
        self.assertEqual(len(self.skipped), 3)
        self.assertEqual(len(self.files), 1)
        self.assertEqual(os.path.basename(sorted(self.files)[0].name), 'a.txt')

    def test_bad_regular_expression_mode(self):
        """Test bad regular expression mode search."""

        walker = rc._DirWalker(
            'tests/dir_walker',
            r'.*?\.txt', True,
            None, False,
            False, False,
            None, None, None,
            None, False,
            -1
        )

        self.crawl_files(walker)

        self.assertEqual(walker.regex_mode, rc.RE_MODE)
        self.assertEqual(len(self.errors), 0)
        self.assertEqual(len(self.skipped), 3)
        self.assertEqual(len(self.files), 1)
        self.assertEqual(os.path.basename(sorted(self.files)[0].name), 'a.txt')

    def test_abort(self):
        """Test aborting."""

        walker = rc._DirWalker(
            'tests/dir_walker',
            '*.txt', False,
            None, False,
            True, True,
            None, None, None,
            None, False
        )

        records = 0
        for f in walker.run():
            records += 1
            walker.kill()

        self.assertEqual(records, 1)

    def test_abort_early(self):
        """Test aborting early."""

        walker = rc._DirWalker(
            'tests/dir_walker',
            '*.txt', False,
            None, False,
            True, True,
            None, None, None,
            None, False
        )

        walker.kill()
        records = 0
        for f in walker.run():
            records += 1

        self.assertEqual(records, 1)

    def test_size_less(self):
        """Test size less than x."""

        walker = rc._DirWalker(
            'tests/dir_walker',
            r'*.*', False,
            None, False,
            True, True,
            ("lt", 1), None, None,
            None, False
        )

        self.crawl_files(walker)

        self.assertEqual(len(self.errors), 0)
        self.assertEqual(len(self.skipped), 1)
        self.assertEqual(len(self.files), 5)

    def test_size_greater(self):
        """Test size greater than x."""

        walker = rc._DirWalker(
            'tests/dir_walker',
            r'*.*', False,
            None, False,
            True, True,
            ("gt", 1), None, None,
            None, False
        )

        self.crawl_files(walker)

        self.assertEqual(len(self.errors), 0)
        self.assertEqual(len(self.skipped), 5)
        self.assertEqual(len(self.files), 1)

    def test_size_equal(self):
        """Test size equals than x."""

        walker = rc._DirWalker(
            'tests/dir_walker',
            r'*.*', False,
            None, False,
            True, True,
            ("eq", 0), None, None,
            None, False
        )

        self.crawl_files(walker)

        self.assertEqual(len(self.errors), 0)
        self.assertEqual(len(self.skipped), 1)
        self.assertEqual(len(self.files), 5)

    def test_time_modified_less(self):
        """Test modified time less than x."""

        future = datetime.datetime.today() + datetime.timedelta(days=2)
        date = "%02d/%02d/%04d" % (future.month, future.day, future.year)

        walker = rc._DirWalker(
            'tests/dir_walker',
            r'*.*', False,
            None, False,
            True, True,
            None, ("lt", epoch.local_time_to_epoch_timestamp(date, '00:00:00')), None,
            None, False
        )

        self.crawl_files(walker)

        self.assertEqual(len(self.errors), 0)
        self.assertEqual(len(self.skipped), 0)
        self.assertEqual(len(self.files), 6)

    def test_time_modified_greater(self):
        """Test modified time greater than x."""

        walker = rc._DirWalker(
            'tests/dir_walker',
            r'*.*', False,
            None, False,
            True, True,
            None, ("gt", epoch.local_time_to_epoch_timestamp('07/07/1980', '00:00:00')), None,
            None, False
        )

        self.crawl_files(walker)

        self.assertEqual(len(self.errors), 0)
        self.assertEqual(len(self.skipped), 0)
        self.assertEqual(len(self.files), 6)

    def test_time_created_less(self):
        """Test created time less than x."""

        future = datetime.datetime.today() + datetime.timedelta(days=2)
        date = "%02d/%02d/%04d" % (future.month, future.day, future.year)

        walker = rc._DirWalker(
            'tests/dir_walker',
            r'*.*', False,
            None, False,
            True, True,
            None, None, ("lt", epoch.local_time_to_epoch_timestamp(date, '00:00:00')),
            None, False
        )

        self.crawl_files(walker)

        self.assertEqual(len(self.errors), 0)
        self.assertEqual(len(self.skipped), 0)
        self.assertEqual(len(self.files), 6)

    def test_time_created_greater(self):
        """Test created time greater than x."""

        walker = rc._DirWalker(
            'tests/dir_walker',
            r'*.*', False,
            None, False,
            True, True,
            None, None, ("gt", epoch.local_time_to_epoch_timestamp('07/07/1980', '00:00:00')),
            None, False
        )

        self.crawl_files(walker)

        self.assertEqual(len(self.errors), 0)
        self.assertEqual(len(self.skipped), 0)
        self.assertEqual(len(self.files), 6)

    def test_backup_folder_no_backup(self):
        """Test directory search with backup disabled and folder backup."""

        walker = rc._DirWalker(
            'tests/dir_walker_folder_backup',
            r'*.txt', False,
            None, False,
            True, True,
            None, None, None,
            None, True
        )

        self.crawl_files(walker)

        self.assertEqual(len(self.errors), 0)
        self.assertEqual(len(self.skipped), 0)
        self.assertEqual(len(self.files), 2)

    def test_backup_folder_with_backup(self):
        """Test directory search with backup disabled and folder backup."""

        walker = rc._DirWalker(
            'tests/dir_walker_folder_backup',
            r'*.txt', False,
            None, False,
            True, True,
            None, None, None,
            '.rum-bak', True
        )

        self.crawl_files(walker)

        self.assertEqual(len(self.errors), 0)
        self.assertEqual(len(self.skipped), 0)
        self.assertEqual(len(self.files), 1)


class TestFileSearch(unittest.TestCase):
    """Test file searching."""

    def get_file_attr(self, name):
        """Get the file attributes."""

        return rc.FileAttrRecord(
            name,
            os.path.splitext(name)[1].lower().lstrip('.'),
            os.path.getsize(name),
            rc.getmtime(name),
            rc.getctime(name),
            False,
            None
        )

    def test_literal_search(self):
        """Test for literal search."""

        search_params = rc.Search()
        search_params.add('search1', None, rc.IGNORECASE | rc.LITERAL)

        file_id = 0
        encoding = None
        context = (0, 0)
        flags = 0
        backup_ext = 'rum-bak',
        max_count = None

        fs = rc._FileSearch(
            search_params,
            self.get_file_attr('tests/searches/searches_unix_ending.txt'),
            file_id,
            flags,
            context,
            encoding,
            backup_ext,
            max_count
        )

        results = [r for r in fs.run()]
        print(results)
        self.assertEqual(len(results), 2)

    def test_literal_chain_search(self):
        """Test for literal search."""

        search_params = rc.Search()
        search_params.add('search1', None, rc.IGNORECASE | rc.LITERAL)
        search_params.add('search2', None, rc.IGNORECASE | rc.LITERAL)

        file_id = 0
        encoding = None
        context = (0, 0)
        flags = 0
        backup_ext = 'rum-bak',
        max_count = None

        fs = rc._FileSearch(
            search_params,
            self.get_file_attr('tests/searches/searches_unix_ending.txt'),
            file_id,
            flags,
            context,
            encoding,
            backup_ext,
            max_count
        )

        results = [r for r in fs.run()]
        print(results)
        self.assertEqual(len(results), 4)

    def test_literal_chain_replace(self):
        """Test for literal search and replace."""

        before = textwrap.dedent(
            '''search1
            search1

            search2
            search2

            search3
            search3

            search1, search2, search3
            '''
        )

        after = textwrap.dedent(
            '''replace1
            replace1

            replace2
            replace2

            search3
            search3

            replace1, replace2, search3
            '''
        )

        search_params = rc.Search(True)
        search_params.add('search1', 'replace1', rc.IGNORECASE | rc.LITERAL)
        search_params.add('search2', 'replace2', rc.IGNORECASE | rc.LITERAL)

        file_id = 0
        encoding = None
        context = (0, 0)
        flags = 0
        backup_ext = 'rum-bak',
        max_count = None

        f = None
        try:
            with tempfile.NamedTemporaryFile('wb', delete=False) as f:
                f.write(before.encode('utf-8'))

            fs = rc._FileSearch(
                search_params,
                self.get_file_attr(f.name),
                file_id,
                flags,
                context,
                encoding,
                backup_ext,
                max_count
            )

            for result in fs.run():
                if result.error is not None:
                    print(''.join(result.error))

            with codecs.open(f.name, 'r', encoding='utf-8') as f:
                self.assertEqual(f.read(), after)
        finally:
            if f is not None:
                os.remove(f.name)

    def test_literal_binary_search(self):
        """Test for literal search."""

        search_params = rc.Search()
        search_params.add('search1', None, rc.IGNORECASE | rc.LITERAL)

        file_id = 0
        encoding = 'bin'
        context = (0, 0)
        flags = rc.PROCESS_BINARY
        backup_ext = 'rum-bak',
        max_count = None

        fs = rc._FileSearch(
            search_params,
            self.get_file_attr('tests/searches/searches_unix_ending.txt'),
            file_id,
            flags,
            context,
            encoding,
            backup_ext,
            max_count
        )

        results = [r for r in fs.run()]
        print(results)
        self.assertEqual(len(results), 2)

    def test_literal_chain_binary_search(self):
        """Test for literal search."""

        search_params = rc.Search()
        search_params.add('search1', None, rc.IGNORECASE | rc.LITERAL)
        search_params.add('search2', None, rc.IGNORECASE | rc.LITERAL)

        file_id = 0
        encoding = 'bin'
        context = (0, 0)
        flags = rc.PROCESS_BINARY
        backup_ext = 'rum-bak',
        max_count = None

        fs = rc._FileSearch(
            search_params,
            self.get_file_attr('tests/searches/searches_unix_ending.txt'),
            file_id,
            flags,
            context,
            encoding,
            backup_ext,
            max_count
        )

        results = [r for r in fs.run()]
        print(results)
        self.assertEqual(len(results), 4)

    def test_literal_chain_binary_replace(self):
        """Test for literal search and replace."""

        before = textwrap.dedent(
            '''search1
            search1

            search2
            search2

            search3
            search3

            search1, search2, search3
            '''
        )

        after = textwrap.dedent(
            '''replace1
            replace1

            replace2
            replace2

            search3
            search3

            replace1, replace2, search3
            '''
        )

        search_params = rc.Search(True)
        search_params.add('search1', 'replace1', rc.IGNORECASE | rc.LITERAL)
        search_params.add('search2', 'replace2', rc.IGNORECASE | rc.LITERAL)

        file_id = 0
        encoding = 'bin'
        context = (0, 0)
        flags = rc.PROCESS_BINARY
        backup_ext = 'rum-bak',
        max_count = None

        f = None
        try:
            with tempfile.NamedTemporaryFile('wb', delete=False) as f:
                f.write(before.encode('utf-8'))

            fs = rc._FileSearch(
                search_params,
                self.get_file_attr(f.name),
                file_id,
                flags,
                context,
                encoding,
                backup_ext,
                max_count
            )

            for result in fs.run():
                if result.error is not None:
                    print(''.join(result.error))

            with codecs.open(f.name, 'r', encoding='utf-8') as f:
                self.assertEqual(f.read(), after)
        finally:
            if f is not None:
                os.remove(f.name)
