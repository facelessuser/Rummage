"""Tests for rumcore."""
from __future__ import unicode_literals
import unittest
from rummage.rummage import rumcore as rc
import re
import regex
from rummage.rummage.rumcore.backrefs import bre
from rummage.rummage.rumcore.backrefs import bregex


class TestHelperFunctions(unittest.TestCase):

    """Test helper functions."""

    def test_to_ascii(self):
        """Test unicode coversion to ascii."""

        unicode_string = "test"
        self.assertTrue(isinstance(rc.to_ascii_bytes(unicode_string), rc.binary_type))

    def test_re_flags(self):
        """Test the re flag settings."""

        if rc.PY3:
            default = re.UNICODE
        else:
            default = 0

        self.assertEqual(rc._re_pattern(r"test").flags, default)
        self.assertEqual(rc._re_pattern(r"test", rc.MULTILINE).flags, re.MULTILINE | default)
        self.assertEqual(rc._re_pattern(r"test", rc.DOTALL).flags, re.DOTALL | default)
        self.assertEqual(rc._re_pattern(r"test", rc.IGNORECASE).flags, re.IGNORECASE | default)
        self.assertEqual(rc._re_pattern(r"test", rc.UNICODE).flags, re.UNICODE | default)
        self.assertEqual(rc._re_pattern(br"test", rc.UNICODE, binary=True).flags, 0)
        self.assertEqual(
            rc._re_pattern(r"test", rc.UNICODE | rc.DOTALL | rc.IGNORECASE | rc.MULTILINE).flags,
            re.UNICODE | re.DOTALL | re.IGNORECASE | re.MULTILINE
        )

    def test_re_literal_flags(self):
        """Test the literal re flags."""

        if rc.PY3:
            default = re.UNICODE
        else:
            default = 0

        self.assertEqual(rc._re_literal_pattern(r"test").flags, default)
        self.assertEqual(rc._re_literal_pattern(r"test", rc.IGNORECASE).flags, re.IGNORECASE | default)
        self.assertEqual(
            rc._re_literal_pattern(r"test", rc.UNICODE | rc.DOTALL | rc.IGNORECASE | rc.MULTILINE).flags,
            re.IGNORECASE | default
        )

    def test_bre_flags(self):
        """Test the bre flag settings."""

        if rc.PY3:
            default = re.UNICODE
        else:
            default = 0

        self.assertEqual(rc._bre_pattern(r"test").flags, default)
        self.assertEqual(rc._bre_pattern(r"test", rc.MULTILINE).flags, bre.MULTILINE | default)
        self.assertEqual(rc._bre_pattern(r"test", rc.DOTALL).flags, bre.DOTALL | default)
        self.assertEqual(rc._bre_pattern(r"test", rc.IGNORECASE).flags, bre.IGNORECASE | default)
        self.assertEqual(rc._bre_pattern(r"test", rc.UNICODE).flags, bre.UNICODE | default)
        self.assertEqual(rc._bre_pattern(br"test", rc.UNICODE, binary=True).flags, 0)
        self.assertEqual(
            rc._bre_pattern(r"test", rc.UNICODE | rc.DOTALL | rc.IGNORECASE | rc.MULTILINE).flags,
            bre.UNICODE | bre.DOTALL | bre.IGNORECASE | bre.MULTILINE
        )

    def test_bre_literal_flags(self):
        """Test the literal bre flags."""

        if rc.PY3:
            default = re.UNICODE
        else:
            default = 0

        self.assertEqual(rc._bre_literal_pattern(r"test").flags, default)
        self.assertEqual(rc._bre_literal_pattern(r"test", rc.IGNORECASE).flags, bre.IGNORECASE | default)
        self.assertEqual(
            rc._bre_literal_pattern(r"test", rc.UNICODE | rc.DOTALL | rc.IGNORECASE | rc.MULTILINE).flags,
            bre.IGNORECASE | default
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
        self.assertEqual(rc._regex_pattern(r"test", rc.BESTMATCH).flags, regex.ASCII | regex.V0 | regex.BESTMATCH)
        self.assertEqual(rc._regex_pattern(r"test", rc.ENHANCEMATCH).flags, regex.ASCII | regex.V0 | regex.ENHANCEMATCH)
        self.assertEqual(rc._regex_pattern(r"test", rc.REVERSE).flags, regex.ASCII | regex.V0 | regex.REVERSE)
        self.assertEqual(rc._regex_pattern(r"test", rc.UNICODE).flags, regex.UNICODE | regex.V0)
        self.assertEqual(rc._regex_pattern(br"test", rc.UNICODE, binary=True).flags, regex.ASCII | regex.V0)
        self.assertEqual(
            rc._regex_pattern(
                r"test",
                rc.DOTALL | rc.IGNORECASE | rc.MULTILINE | rc.WORD |
                rc.BESTMATCH | rc.ENHANCEMATCH | rc.REVERSE | rc.FULLCASE
            ).flags,
            regex.V0 | regex.ASCII | regex.DOTALL | regex.IGNORECASE | regex.MULTILINE |
            regex.WORD | regex.ENHANCEMATCH | regex.BESTMATCH | regex.REVERSE | regex.FULLCASE
        )
        self.assertEqual(
            rc._regex_pattern(
                r"test",
                rc.UNICODE | rc.DOTALL | rc.IGNORECASE | rc.MULTILINE | rc.FULLCASE |
                rc.WORD | rc.BESTMATCH | rc.ENHANCEMATCH | rc.REVERSE | rc.VERSION1
            ).flags,
            regex.V1 | regex.UNICODE | regex.DOTALL | regex.IGNORECASE | regex.MULTILINE |
            regex.WORD | regex.ENHANCEMATCH | regex.BESTMATCH | regex.REVERSE | regex.FULLCASE
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
                rc.WORD | rc.BESTMATCH | rc.ENHANCEMATCH | rc.REVERSE | rc.VERSION1
            ).flags,
            regex.IGNORECASE | regex.V0 | regex.ASCII
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
                rc.BESTMATCH | rc.ENHANCEMATCH | rc.REVERSE | rc.FULLCASE
            ).flags,
            bregex.V0 | bregex.ASCII | bregex.DOTALL | bregex.IGNORECASE | bregex.MULTILINE |
            bregex.WORD | bregex.ENHANCEMATCH | bregex.BESTMATCH | bregex.REVERSE | bregex.FULLCASE
        )
        self.assertEqual(
            rc._bregex_pattern(
                r"test",
                rc.UNICODE | rc.DOTALL | rc.IGNORECASE | rc.MULTILINE | rc.FULLCASE |
                rc.WORD | rc.BESTMATCH | rc.ENHANCEMATCH | rc.REVERSE | rc.VERSION1
            ).flags,
            bregex.V1 | bregex.UNICODE | bregex.DOTALL | bregex.IGNORECASE | bregex.MULTILINE |
            bregex.WORD | bregex.ENHANCEMATCH | bregex.BESTMATCH | bregex.REVERSE | bregex.FULLCASE
        )

    def test_bregex_literal_flags(self):
        """Test the literal re flags."""

        self.assertEqual(
            rc._bregex_literal_pattern(r"test").flags, bregex.V0 | bregex.ASCII
        )
        self.assertEqual(
            rc._bregex_literal_pattern(r"test", rc.IGNORECASE).flags, bregex.V0 | bregex.ASCII | bregex.IGNORECASE
        )
        self.assertEqual(
            rc._bregex_literal_pattern(
                r"test",
                rc.UNICODE | rc.DOTALL | rc.IGNORECASE | rc.MULTILINE |
                rc.WORD | rc.BESTMATCH | rc.ENHANCEMATCH | rc.REVERSE | rc.VERSION1
            ).flags,
            bregex.IGNORECASE | bregex.V0 | bregex.ASCII
        )

    def test_exception(self):
        """Test retrieval of exceptions."""

        try:
            test = 3 + "3"
        except:
            test = None
            error = rc.get_exception()
        self.assertTrue(test is None)
        self.assertTrue(error[0].startswith('TypeError'))
