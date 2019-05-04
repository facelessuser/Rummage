# -*- coding: utf-8 -*-
"""Tests for `rumcore`."""
from __future__ import unicode_literals
import unittest
import os
import re
import regex
import codecs
import datetime
import textwrap
from backrefs import bre
from backrefs import bregex
from rummage.lib import rumcore as rc
from rummage.lib.util import epoch_timestamp as epoch
from rummage.lib.rumcore import text_decode as td
from wcmatch import wcmatch
from . import util
import shutil


class _FileTest(unittest.TestCase):
    """Test BOM detection."""

    def mktemp(self, *parts, content=b''):
        """Make temp directory."""

        filename = self.norm(*parts)
        base, file = os.path.split(filename)
        if not os.path.exists(base):
            retry = 3
            while retry:
                try:
                    os.makedirs(base)
                    retry = 0
                except Exception:
                    retry -= 1
        util.create_empty_file(filename, content)

    def norm(self, *parts):
        """Normalizes file path (in relation to temp directory)."""
        tempdir = os.fsencode(self.tempdir) if isinstance(parts[0], bytes) else self.tempdir
        return os.path.join(tempdir, *parts)

    def dedent(self, text):
        """Reduce indentation."""

        return textwrap.dedent(text).lstrip('\n')

    def setUp(self):
        """Setup temp folder."""

        self.tempdir = util.TESTFN + "_dir"

    def tearDown(self):
        """Tear down."""

        retry = 3
        while retry:
            try:
                shutil.rmtree(self.tempdir)
                retry = 0
            except Exception:
                retry -= 1


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
        """Test the `bre` flag settings."""

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


class TestRummageFileContent(_FileTest):
    """Tests for `_RummageFileContent`."""

    def compare_encoding(self, filename, content, file_encoding, expected, bfr=False):
        """Compare encoding."""

        if not bfr:
            self.mktemp(filename, content=content)
            name = self.norm(filename)
            size = os.path.getsize(name)
        else:
            name = filename
            size = None
        if not bfr:
            rfc = rc._RummageFileContent(name, size, file_encoding)
        else:
            rfc = rc._RummageFileContent(name, size, file_encoding, content)
        with rfc as f:
            text = f[:]
        if not bfr:
            if expected.startswith('utf-8'):
                enc = 'utf-8-sig'
            elif expected.startswith('utf-32'):
                enc = 'utf-32'
            elif expected.startswith('utf-16'):
                enc = 'utf-16'
            else:
                enc = expected
            if enc == 'bin':
                with open(name, 'rb') as f:
                    text2 = f.read()
            else:
                with codecs.open(name, 'r', encoding=enc) as f:
                    text2 = f.read()
        else:
            text2 = content
        self.assertEqual(rfc.encoding.encode, expected)
        self.assertEqual(text, text2)

    def test_string_bin(self):
        """Test passing a binary string."""

        self.compare_encoding(
            'buffer',
            b'test',
            td.Encoding('bin', None),
            'bin',
            True
        )

    def test_string_unicode(self):
        """Test passing a binary string."""

        self.compare_encoding(
            'buffer',
            'test',
            td.Encoding('unicode', None),
            'unicode',
            True
        )

    def test_bin(self):
        """Test bin file."""

        self.compare_encoding(
            'binary.txt',
            b'This is a \x00\x00\x00binary test.\n',
            td.Encoding('bin', None),
            'bin'
        )

    def test_utf8(self):
        """Test `utf-8` file."""

        self.compare_encoding(
            'utf8-bom.txt',
            'UTF8 file with BOM'.encode('utf-8-sig'),
            td.Encoding('utf-8', codecs.BOM_UTF8),
            'utf-8'
        )

    def test_utf16(self):
        """Test `utf-16` file."""

        self.compare_encoding(
            'utf16_be_bom.txt',
            codecs.BOM_UTF16_BE + 'UTF16BE file with BOM'.encode('utf-16-be'),
            td.Encoding('utf-16-be', codecs.BOM_UTF16_BE),
            'utf-16-be'
        )

    def test_utf32(self):
        """Test `utf-8` file."""

        self.compare_encoding(
            'utf16_be_bom.txt',
            codecs.BOM_UTF32_BE + 'UTF32BE file with BOM'.encode('utf-32-be'),
            td.Encoding('utf-32-be', codecs.BOM_UTF32_BE),
            'utf-32-be'
        )

    def test_wrong(self):
        """Test wrong encoding failure."""

        self.compare_encoding(
            'utf8.txt',
            'exámple'.encode('utf-8'),
            td.Encoding('utf-32-be', codecs.BOM_UTF32_BE),
            'bin'
        )

    def test_rummageexception(self):
        """Test `RummageException` with file."""

        rfc = rc._RummageFileContent(self.norm('does_not_exist.txt'), 10, td.Encoding('ascii', None))
        self.assertRaises(rc.RummageException, rfc.__enter__)

    def test_bin_rummageexception(self):
        """Test `RummageException` with a bin file."""

        rfc = rc._RummageFileContent(self.norm('does_not_exist.txt'), 10, td.Encoding('bin', None))
        self.assertRaises(rc.RummageException, rfc.__enter__)


class TestDirWalker(_FileTest):
    """Test the `_DirWalker` class."""

    def setUp(self):
        """Setup the tests."""

        _FileTest.setUp(self)
        self.mktemp('a.txt')
        self.mktemp('b.file')
        self.mktemp('.hidden_file')
        self.mktemp('greater_than_0.txt.rum-bak', content=b'Content greater than 0.')
        self.mktemp('.hidden', 'a.txt')
        self.mktemp('.hidden', 'b.file')
        self.default_flags = wcmatch.R | wcmatch.I | wcmatch.M | wcmatch.SL
        self.errors = []
        self.skipped = 0
        self.files = []

    def crawl_files(self, walker):
        """Crawl the files."""

        for f in walker.match():
            if hasattr(f, 'skipped') and f.skipped:
                self.skipped += 1
            elif f.error:
                self.errors.append(f)
            else:
                self.files.append(f)

    def test_non_recursive(self):
        """Test non-recursive search."""

        walker = rc._DirWalker(
            self.tempdir,
            '*.txt', None,
            self.default_flags,
            False, False,
            None, None, None,
            None, False
        )

        self.crawl_files(walker)

        self.assertEqual(len(self.errors), 0)
        self.assertEqual(self.skipped, 3)
        self.assertEqual(len(self.files), 1)
        self.assertEqual(os.path.basename(self.files[0].name), 'a.txt')

    def test_non_recursive_inverse(self):
        """Test non-recursive inverse search."""

        walker = rc._DirWalker(
            self.tempdir,
            '*.*|-*.file', None,
            self.default_flags,
            False, False,
            None, None, None,
            None, False
        )

        self.crawl_files(walker)

        self.assertEqual(len(self.errors), 0)
        self.assertEqual(self.skipped, 2)
        self.assertEqual(len(self.files), 2)

    def test_non_recursive_inverse_backup(self):
        """Test non-recursive inverse search with backup."""

        walker = rc._DirWalker(
            self.tempdir,
            '*.*|-*.file', None,
            self.default_flags,
            False, False,
            None, None, None,
            'rum-bak', False
        )

        self.crawl_files(walker)

        self.assertEqual(len(self.errors), 0)
        self.assertEqual(self.skipped, 3)
        self.assertEqual(len(self.files), 1)

    def test_recursive(self):
        """Test non-recursive search."""

        walker = rc._DirWalker(
            self.tempdir,
            '*.txt', None,
            self.default_flags | wcmatch.RECURSIVE,
            False, False,
            None, None, None,
            None, False
        )

        self.crawl_files(walker)

        self.assertEqual(len(self.errors), 0)
        self.assertEqual(self.skipped, 3)
        self.assertEqual(len(self.files), 1)
        self.assertEqual(os.path.basename(self.files[0].name), 'a.txt')

    def test_recursive_hidden(self):
        """Test non-recursive search."""

        walker = rc._DirWalker(
            self.tempdir,
            '*.txt', None,
            self.default_flags | wcmatch.RECURSIVE | wcmatch.HIDDEN,
            False, False,
            None, None, None,
            None, False
        )

        self.crawl_files(walker)

        self.assertEqual(len(self.errors), 0)
        self.assertEqual(self.skipped, 4)
        self.assertEqual(len(self.files), 2)
        self.assertEqual(os.path.basename(sorted(self.files)[0].name), 'a.txt')

    def test_recursive_hidden_folder_exclude(self):
        """Test non-recursive search."""

        walker = rc._DirWalker(
            self.tempdir,
            '*.txt', '.hidden',
            self.default_flags | wcmatch.RECURSIVE | wcmatch.HIDDEN,
            False, False,
            None, None, None,
            None, False
        )

        self.crawl_files(walker)

        self.assertEqual(len(self.errors), 0)
        self.assertEqual(self.skipped, 3)
        self.assertEqual(len(self.files), 1)
        self.assertEqual(os.path.basename(self.files[0].name), 'a.txt')

    def test_recursive_hidden_folder_exclude_inverse(self):
        """Test non-recursive search with inverse."""

        walker = rc._DirWalker(
            self.tempdir,
            '*.txt', '*|-.hidden',
            self.default_flags | wcmatch.RECURSIVE | wcmatch.HIDDEN,
            False, False,
            None, None, None,
            None, False
        )

        self.crawl_files(walker)

        self.assertEqual(len(self.errors), 0)
        self.assertEqual(self.skipped, 4)
        self.assertEqual(len(self.files), 2)
        self.assertEqual(os.path.basename(sorted(self.files)[0].name), 'a.txt')

    def test_recursive_hidden_re_folder_exclude(self):
        """Test non-recursive search."""

        walker = rc._DirWalker(
            self.tempdir,
            '*.txt', r'\.hidden',
            self.default_flags | wcmatch.RECURSIVE | wcmatch.HIDDEN,
            False, True,
            None, None, None,
            None, False
        )

        self.crawl_files(walker)

        self.assertEqual(len(self.errors), 0)
        self.assertEqual(self.skipped, 3)
        self.assertEqual(len(self.files), 1)
        self.assertEqual(os.path.basename(self.files[0].name), 'a.txt')

    def test_raw_chars(self):
        """Test raw chars."""

        walker = rc._DirWalker(
            self.tempdir,
            r'*.\x74\N{LATIN SMALL LETTER X}\u0074', r'\.\U00000068idden',
            self.default_flags | wcmatch.RECURSIVE | wcmatch.HIDDEN,
            False, True,
            None, None, None,
            None, False
        )

        self.crawl_files(walker)

        self.assertEqual(len(self.errors), 0)
        self.assertEqual(self.skipped, 3)
        self.assertEqual(len(self.files), 1)
        self.assertEqual(os.path.basename(self.files[0].name), 'a.txt')

    def test_re(self):
        """Test regex search."""

        walker = rc._DirWalker(
            self.tempdir,
            r'.*?\.txt', None,
            self.default_flags,
            True, False,
            None, None, None,
            None, False
        )

        self.crawl_files(walker)

        self.assertEqual(walker.regex_mode, rc.RE_MODE)
        self.assertEqual(len(self.errors), 0)
        self.assertEqual(self.skipped, 3)
        self.assertEqual(len(self.files), 1)
        self.assertEqual(os.path.basename(sorted(self.files)[0].name), 'a.txt')

    def test_bre(self):
        """Test `bre` search."""

        walker = rc._DirWalker(
            self.tempdir,
            r'.*?\.txt', None,
            self.default_flags,
            True, False,
            None, None, None,
            None, False,
            rc.BRE_MODE
        )

        self.crawl_files(walker)

        self.assertEqual(walker.regex_mode, rc.BRE_MODE)
        self.assertEqual(len(self.errors), 0)
        self.assertEqual(self.skipped, 3)
        self.assertEqual(len(self.files), 1)
        self.assertEqual(os.path.basename(sorted(self.files)[0].name), 'a.txt')

    def test_regex(self):
        """Test regex search."""

        walker = rc._DirWalker(
            self.tempdir,
            r'.*?\.txt', None,
            self.default_flags,
            True, False,
            None, None, None,
            None, False,
            rc.REGEX_MODE
        )

        self.crawl_files(walker)

        self.assertEqual(walker.regex_mode, rc.REGEX_MODE)
        self.assertEqual(len(self.errors), 0)
        self.assertEqual(self.skipped, 3)
        self.assertEqual(len(self.files), 1)
        self.assertEqual(os.path.basename(sorted(self.files)[0].name), 'a.txt')

    def test_bregex(self):
        """Test `bregex` search."""

        walker = rc._DirWalker(
            self.tempdir,
            r'.*?\.txt', None,
            self.default_flags,
            True, False,
            None, None, None,
            None, False,
            rc.BREGEX_MODE
        )

        self.crawl_files(walker)

        self.assertEqual(walker.regex_mode, rc.BREGEX_MODE)
        self.assertEqual(len(self.errors), 0)
        self.assertEqual(self.skipped, 3)
        self.assertEqual(len(self.files), 1)
        self.assertEqual(os.path.basename(sorted(self.files)[0].name), 'a.txt')

    def test_bad_regular_expression_mode(self):
        """Test bad regular expression mode search."""

        walker = rc._DirWalker(
            self.tempdir,
            r'.*?\.txt', None,
            self.default_flags,
            True, False,
            None, None, None,
            None, False,
            -1
        )

        self.crawl_files(walker)

        self.assertEqual(walker.regex_mode, rc.RE_MODE)
        self.assertEqual(len(self.errors), 0)
        self.assertEqual(self.skipped, 3)
        self.assertEqual(len(self.files), 1)
        self.assertEqual(os.path.basename(sorted(self.files)[0].name), 'a.txt')

    def test_abort(self):
        """Test aborting."""

        walker = rc._DirWalker(
            self.tempdir,
            '*.txt', None,
            self.default_flags | wcmatch.RECURSIVE | wcmatch.HIDDEN,
            False, False,
            None, None, None,
            None, False
        )

        records = 0
        for f in walker.imatch():
            records += 1
            walker.kill()

        self.assertEqual(records, 1)

    def test_abort_early(self):
        """Test aborting early."""

        walker = rc._DirWalker(
            self.tempdir,
            '*.txt*', None,
            self.default_flags | wcmatch.RECURSIVE | wcmatch.HIDDEN,
            False, False,
            None, None, None,
            None, False
        )

        walker.kill()
        records = 0
        for f in walker.imatch():
            records += 1

        self.assertTrue(records == 0 or walker.get_skipped() == 0)

    def test_size_less(self):
        """Test size less than x."""

        walker = rc._DirWalker(
            self.tempdir,
            r'*.*', None,
            self.default_flags | wcmatch.RECURSIVE | wcmatch.HIDDEN,
            False, False,
            ("lt", 1), None, None,
            None, False
        )

        self.crawl_files(walker)

        self.assertEqual(len(self.errors), 0)
        self.assertEqual(self.skipped, 1)
        self.assertEqual(len(self.files), 5)

    def test_size_greater(self):
        """Test size greater than x."""

        walker = rc._DirWalker(
            self.tempdir,
            r'*.*', None,
            self.default_flags | wcmatch.RECURSIVE | wcmatch.HIDDEN,
            False, False,
            ("gt", 1), None, None,
            None, False
        )

        self.crawl_files(walker)

        self.assertEqual(len(self.errors), 0)
        self.assertEqual(self.skipped, 5)
        self.assertEqual(len(self.files), 1)

    def test_size_equal(self):
        """Test size equals than x."""

        walker = rc._DirWalker(
            self.tempdir,
            r'*.*', None,
            self.default_flags | wcmatch.RECURSIVE | wcmatch.HIDDEN,
            False, False,
            ("eq", 0), None, None,
            None, False
        )

        self.crawl_files(walker)

        self.assertEqual(len(self.errors), 0)
        self.assertEqual(self.skipped, 1)
        self.assertEqual(len(self.files), 5)

    def test_time_modified_less(self):
        """Test modified time less than x."""

        future = datetime.datetime.today() + datetime.timedelta(days=2)
        date = "%02d/%02d/%04d" % (future.month, future.day, future.year)

        walker = rc._DirWalker(
            self.tempdir,
            r'*.*', None,
            self.default_flags | wcmatch.RECURSIVE | wcmatch.HIDDEN,
            False, False,
            None, ("lt", epoch.local_time_to_epoch_timestamp(date, '00:00:00')), None,
            None, False
        )

        self.crawl_files(walker)

        self.assertEqual(len(self.errors), 0)
        self.assertEqual(self.skipped, 0)
        self.assertEqual(len(self.files), 6)

    def test_time_modified_greater(self):
        """Test modified time greater than x."""

        walker = rc._DirWalker(
            self.tempdir,
            r'*.*', None,
            self.default_flags | wcmatch.RECURSIVE | wcmatch.HIDDEN,
            False, False,
            None, ("gt", epoch.local_time_to_epoch_timestamp('07/07/1980', '00:00:00')), None,
            None, False
        )

        self.crawl_files(walker)

        self.assertEqual(len(self.errors), 0)
        self.assertEqual(self.skipped, 0)
        self.assertEqual(len(self.files), 6)

    def test_time_created_less(self):
        """Test created time less than x."""

        future = datetime.datetime.today() + datetime.timedelta(days=2)
        date = "%02d/%02d/%04d" % (future.month, future.day, future.year)

        walker = rc._DirWalker(
            self.tempdir,
            r'*.*', None,
            self.default_flags | wcmatch.RECURSIVE | wcmatch.HIDDEN,
            False, False,
            None, None, ("lt", epoch.local_time_to_epoch_timestamp(date, '00:00:00')),
            None, False
        )

        self.crawl_files(walker)

        self.assertEqual(len(self.errors), 0)
        self.assertEqual(self.skipped, 0)
        self.assertEqual(len(self.files), 6)

    def test_time_created_greater(self):
        """Test created time greater than x."""

        walker = rc._DirWalker(
            self.tempdir,
            r'*.*', None,
            self.default_flags | wcmatch.RECURSIVE | wcmatch.HIDDEN,
            False, False,
            None, None, ("gt", epoch.local_time_to_epoch_timestamp('07/07/1980', '00:00:00')),
            None, False
        )

        self.crawl_files(walker)

        self.assertEqual(len(self.errors), 0)
        self.assertEqual(self.skipped, 0)
        self.assertEqual(len(self.files), 6)


class TestHiddenDirWalker(_FileTest):
    """Test the `_DirWalker` class."""

    def setUp(self):
        """Setup the tests."""

        _FileTest.setUp(self)
        self.mktemp('a.txt')
        self.mktemp('.rum-bak', 'a.txt')
        self.default_flags = wcmatch.R | wcmatch.I | wcmatch.M
        self.errors = []
        self.skipped = 0
        self.files = []

    def crawl_files(self, walker):
        """Crawl the files."""

        for f in walker.match():
            if hasattr(f, 'skipped') and f.skipped:
                self.skipped += 1
            elif f.error:
                self.errors.append(f)
            else:
                self.files.append(f)

    def test_backup_folder_no_backup(self):
        """Test directory search with backup disabled and folder backup."""

        walker = rc._DirWalker(
            self.tempdir,
            r'*.txt', None,
            self.default_flags | wcmatch.RECURSIVE | wcmatch.HIDDEN,
            False, False,
            None, None, None,
            None, True
        )

        self.crawl_files(walker)

        self.assertEqual(len(self.errors), 0)
        self.assertEqual(self.skipped, 0)
        self.assertEqual(len(self.files), 2)

    def test_backup_folder_with_backup(self):
        """Test directory search with backup disabled and folder backup."""

        walker = rc._DirWalker(
            self.tempdir,
            r'*.txt', None,
            self.default_flags | wcmatch.RECURSIVE | wcmatch.HIDDEN,
            False, False,
            None, None, None,
            '.rum-bak', True
        )

        self.crawl_files(walker)

        self.assertEqual(len(self.errors), 0)
        self.assertEqual(self.skipped, 0)
        self.assertEqual(len(self.files), 1)


class TestFileSearch(_FileTest):
    """Test file searching."""

    def get_file_attr(self, *path):
        """Get the file attributes."""

        name = self.norm(*path)
        c_time, m_time = rc.get_stat(name)[:2]
        return rc.FileAttrRecord(
            name,
            os.path.splitext(name)[1].lower().lstrip('.'),
            os.path.getsize(name),
            m_time,
            c_time,
            False,
            None
        )

    def test_literal_search(self):
        """Test for literal search."""

        self.mktemp(
            'searches.txt',
            content=self.dedent(
                '''
                search1

                search2

                search1

                search2
                '''
            ).encode('ascii')
        )

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
            self.get_file_attr('searches.txt'),
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

        self.mktemp(
            'searches.txt',
            content=self.dedent(
                '''
                search1

                search2

                search1

                search2
                '''
            ).encode('ascii')
        )

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
            self.get_file_attr('searches.txt'),
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

        self.mktemp(
            'searches.txt',
            content=self.dedent(
                '''
                search1
                search1

                search2
                search2

                search3
                search3

                search1, search2, search3
                '''
            ).encode('utf-8')
        )

        after = self.dedent(
            '''
            replace1
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

        fs = rc._FileSearch(
            search_params,
            self.get_file_attr('searches.txt'),
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

        with codecs.open(self.norm('searches.txt'), 'r', encoding='utf-8') as f:
            self.assertEqual(f.read(), after)

    def test_literal_binary_search(self):
        """Test for literal search."""

        self.mktemp(
            'searches.txt',
            content=self.dedent(
                '''
                search1

                search2

                search1

                search2
                '''
            ).encode('utf-8')
        )

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
            self.get_file_attr('searches.txt'),
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

        self.mktemp(
            'searches.txt',
            content=self.dedent(
                '''
                search1

                search2

                search1

                search2
                '''
            ).encode('utf-8')
        )

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
            self.get_file_attr('searches.txt'),
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

        self.mktemp(
            'searches.txt',
            content=self.dedent(
                '''
                search1
                search1

                search2
                search2

                search3
                search3

                search1, search2, search3
                '''
            ).encode('utf-8')
        )

        after = self.dedent(
            '''
            replace1
            replace1

            replace2
            replace2

            search3
            search3

            replace1, replace2, search3
            '''
        ).encode('utf-8')

        search_params = rc.Search(True)
        search_params.add('search1', 'replace1', rc.IGNORECASE | rc.LITERAL)
        search_params.add('search2', 'replace2', rc.IGNORECASE | rc.LITERAL)

        file_id = 0
        encoding = 'bin'
        context = (0, 0)
        flags = rc.PROCESS_BINARY
        backup_ext = 'rum-bak',
        max_count = None

        fs = rc._FileSearch(
            search_params,
            self.get_file_attr('searches.txt'),
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

        with codecs.open(self.norm('searches.txt'), 'rb') as f:
            self.assertEqual(f.read(), after)
