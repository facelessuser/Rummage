# -*- coding: utf-8 -*-
"""Test critic lib."""
from __future__ import unicode_literals
import unittest
from rummage.rummage.rumcore import backrefs
import re
import sys

PY3 = (3, 0) <= sys.version_info < (4, 0)

if PY3:
    binary_type = bytes  # noqa
else:
    binary_type = str  # noqa


class TestSearchTemplate(unittest.TestCase):

    """Search template tests."""

    def test_single_uppercase(self):
        """Test uppercase."""

        result = backrefs.SearchTemplate(r'Testing \ccase!').apply()

        self.assertEqual(r'Testing Case!', result)

    def test_span_uppercase(self):
        """Test uppercase block."""

        result = backrefs.SearchTemplate(r'Testing \Ccase\E!').apply()

        self.assertEqual(r'Testing CASE!', result)

    def test_single_lowercase(self):
        """Test lowercase."""

        result = backrefs.SearchTemplate(r'Testing \lCASE!').apply()

        self.assertEqual(r'Testing cASE!', result)

    def test_span_lowercase(self):
        """Test lowercase block."""

        result = backrefs.SearchTemplate(r'Testing \LCASE\E!').apply()

        self.assertEqual(r'Testing case!', result)

    def test_quote(self):
        """Test quoting/escaping."""

        result = backrefs.SearchTemplate(r'Testing \Q(\s+[quote]*\s+)?\E!').apply()

        self.assertEqual(r'Testing %s!' % re.escape(r'(\s+[quote]*\s+)?'), result)

    def test_nesting_case(self):
        """Test nesting upper and lower case."""

        result = backrefs.SearchTemplate(r'\c\ltesting \c\LTITLE\E \Cc\la\Ls\Ee\E!').apply()

        self.assertEqual(r'Testing Title CasE!', result)

    def test_quote_preserve(self):
        """Test scenario where first letter in quote was not preserved."""

        result = backrefs.SearchTemplate(r'Testing \c\l\Qpreserve quote\E!').apply()

        self.assertEqual(r'Testing %s!' % re.escape(r'preserve quote'), result)

    def test_avoid_char_blocks(self):
        """Test that backrefs are ignored in character groups."""

        result = backrefs.SearchTemplate(r'Testing [\Cchar\E \lblock] \L[\QAVOIDANCE\E]\E!').apply()

        self.assertEqual(r'Testing [char block] [avoidance]!', result)

    def test_extraneous_end_char(self):
        r"""Test that stray '\E's get removed."""

        result = backrefs.SearchTemplate(r'Testing \Eextraneous end char\E!').apply()

        self.assertEqual(r'Testing extraneous end char!', result)

    def test_end_outside_block(self):
        """Test that a single upper/lowercase on end boundary terminates proper."""

        result = backrefs.SearchTemplate(r'Testing \Cabrupt end\c\E outside block!').apply()

        self.assertEqual(r'Testing ABRUPT END outside block!', result)

    def test_unicode_properties_capital(self):
        """
        Excercising that unicode properties are built correctly.

        We want to test uppercase and make sure things make sense,
        and then test lower case later.  Not extensive, just making sure its genrally working.
        """

        pattern = backrefs.compile_search(r'EX\p{Lu}MPLE', re.UNICODE)
        m = pattern.match(r'EXÁMPLE')
        self.assertTrue(m is not None)
        m = pattern.match(r'exámple')
        self.assertTrue(m is None)

    def test_unicode_properties_lower(self):
        """Exercise the unicode properties for lower case."""

        pattern = backrefs.compile_search(r'ex\p{Ll}mple', re.UNICODE)
        m = pattern.match('exámple')
        self.assertTrue(m is not None)
        m = pattern.match('EXÁMPLE')
        self.assertTrue(m is None)

    def test_unicode_properties_in_char_group(self):
        """Exercise the unicode properties inside a char group."""

        pattern = backrefs.compile_search(r'ex[\p{Ll}\p{Lu}]mple', re.UNICODE)
        m = pattern.match('exámple')
        self.assertTrue(m is not None)
        m = pattern.match('exÁmple')
        self.assertTrue(m is not None)

    def test_unicode_properties_names(self):
        """Test unicode group friendly names."""

        pattern = backrefs.compile_search(r'ex[\p{Letter}]mple', re.UNICODE)
        m = pattern.match('exámple')
        print(pattern.pattern)
        self.assertTrue(m is not None)
        m = pattern.match('exÁmple')
        self.assertTrue(m is not None)

    def test_char_cases(self):
        r"""Backrefs should work on char escapes."""

        pattern = backrefs.compile_search(r'\c\x67\c\u0137\C\x67\u0137\E')
        m = pattern.match(r'GĶGĶ')
        self.assertTrue(m is not None)

    def test_binary_char_cases(self):
        r"""Backrefs should work on char escapes."""

        pattern = backrefs.compile_search(br'\c\x67\l\x47\C\x47\x67\E')
        m = pattern.match(br'GgGG')
        self.assertTrue(m is not None)

    def test_binary_unicode_ignore(self):
        r"""Binary patterns should not process \p references."""

        pattern = backrefs.compile_search(br'EX\p{Lu}MPLE')
        m = pattern.match(br'EXp{Lu}MPLE')
        self.assertTrue(m is not None)

    def test_binary_backrefs(self):
        """Non-unicode back refs should still work on binary patterns."""

        pattern = backrefs.compile_search(br'\cg\lG\Cgg\E\LGG\E\Q()\E')
        m = pattern.match(br'GgGGgg()')
        self.assertTrue(m is not None)

    def test_detect_verbose_string_flag(self):
        """Test verbose string flag (?x)."""

        pattern = backrefs.compile_search(
            r'''(?x)
            This is a # \Ccomment\E
            This is not a \# \Ccomment\E
            This is not a [#\ ] \Ccomment\E
            This is not a [\#] \Ccomment\E
            This\ is\ a # \Ccomment\E
            '''
        )

        self.assertEqual(
            pattern.pattern,
            r'''(?x)
            This is a # \Ccomment\E
            This is not a \# COMMENT
            This is not a [#\ ] COMMENT
            This is not a [\#] COMMENT
            This\ is\ a # \Ccomment\E
            '''
        )

    def test_detect_verbose(self):
        """Test verbose."""

        pattern = backrefs.compile_search(
            r'''
            This is a # \Ccomment\E
            This is not a \# \Ccomment\E
            This is not a [#\ ] \Ccomment\E
            This is not a [\#] \Ccomment\E
            This\ is\ a # \Ccomment\E
            ''',
            re.VERBOSE
        )

        self.assertEqual(
            pattern.pattern,
            r'''
            This is a # \Ccomment\E
            This is not a \# COMMENT
            This is not a [#\ ] COMMENT
            This is not a [\#] COMMENT
            This\ is\ a # \Ccomment\E
            '''
        )

    def test_no_verbose(self):
        """Test no verbose."""

        pattern = backrefs.compile_search(
            r'''
            This is a # \Ccomment\E
            This is not a \# \Ccomment\E
            This is not a [#\ ] \Ccomment\E
            This is not a [\#] \Ccomment\E
            This\ is\ a # \Ccomment\E
            '''
        )

        self.assertEqual(
            pattern.pattern,
            r'''
            This is a # COMMENT
            This is not a \# COMMENT
            This is not a [#\ ] COMMENT
            This is not a [\#] COMMENT
            This\ is\ a # COMMENT
            '''
        )

    def test_other_backrefs(self):
        """Test that other backrefs make it through."""

        pattern = backrefs.compile_search(
            r'''(?x)
            This \bis a # \Ccomment\E
            This is\w+ not a \# \Ccomment\E
            '''
        )

        self.assertEqual(
            pattern.pattern,
            r'''(?x)
            This \bis a # \Ccomment\E
            This is\w+ not a \# COMMENT
            '''
        )


class TestReplaceTemplate(unittest.TestCase):

    """Test replace template."""

    def test_uppercase(self):
        """Test uppercase."""

        text = "this is a test for uppercase!"
        pattern = re.compile(r"(this)(.*?)(uppercase)(!)")
        expand = backrefs.compile_replace(pattern, r'\c\1\2\C\3\E\4')
        results = expand(pattern.match(text))

        self.assertEqual('This is a test for UPPERCASE!', results)

    def test_lowercase(self):
        """Test lowercase."""

        text = "THIS is a test for LOWERCASE!"
        pattern = re.compile(r"(THIS)(.*?)(LOWERCASE)(!)")
        expand = backrefs.compile_replace(pattern, r'\l\1\2\L\3\E\4')
        results = expand(pattern.match(text))

        self.assertEqual('tHIS is a test for lowercase!', results)

    def test_mixed_nested(self):
        """
        Test mix of upper and lower case.

            - sinlge case before block case
            - single case inside of block case
            - block case inside block case
        """

        text = "this is a test for mixed and nested!"
        pattern = re.compile(r"(this )(.*?)(mixed and )(nested)(!)")
        expand = backrefs.compile_replace(pattern, r'\l\C\1\l\2\L\c\3\E\4\E\5')
        results = expand(pattern.match(text))

        self.assertEqual('tHIS iS A TEST FOR Mixed and NESTED!', results)

    def test_ignore_group(self):
        """Test that backrefs inserted by matching groups are passed over."""

        text = r"This is a test to see if \Cbackre\Efs in gr\coups get ig\Lnor\led proper!"
        pattern = re.compile(r"(This is a test to see if \\Cbackre\\Efs )(.*?)(ig\\Lnor\\led )(proper)(!)")
        expand = backrefs.compile_replace(pattern, r'Here is the first \C\1\Ethe second \c\2third \L\3\E\4\5')
        results = expand(pattern.match(text))

        self.assertEqual(
            r'Here is the first THIS IS A TEST TO SEE IF \CBACKRE\EFS the second In gr\coups get third '
            r'ig\lnor\led proper!',
            results
        )

    def test_mixed_groups(self):
        """
        Test mix of upper and lower case with named groups.

        Named groups will fail if compile_replace is given a string pattern instead of a compiled
        pattern object.  It will still work with non-named groups, it is just a limitation.
        """

        text = "this is a test for named capture groups!"
        text_pattern = r"(?P<first>this )(?P<second>.*?)(?P<third>named capture )(?P<fourth>groups)(!)"
        pattern = re.compile(text_pattern)

        # Will fail with AttributeError because non-compiled patterns can't be used to resolve
        # group names in replace template.
        with self.assertRaises(AttributeError):
            expand = backrefs.compile_replace(text_pattern, r'\l\C\g<first>\l\g<second>\L\c\g<third>\E\g<fourth>\E\5')

        # This will pass because we do not need to resolve named groups.
        expand = backrefs.compile_replace(text_pattern, r'\l\C\g<1>\l\g<2>\L\c\g<3>\E\g<4>\E\5')
        results = expand(pattern.match(text))
        self.assertEqual('tHIS iS A TEST FOR Named capture GROUPS!', results)

        # Now using compiled pattern, we can use named groups in replace template.
        expand = backrefs.compile_replace(pattern, r'\l\C\g<first>\l\g<second>\L\c\g<third>\E\g<fourth>\E\5')
        results = expand(pattern.match(text))
        self.assertEqual('tHIS iS A TEST FOR Named capture GROUPS!', results)

    def test_as_replace_function(self):
        """Test that replace can be used as a replace function."""

        text = "this will be fed into re.subn!  Here we go!  this will be fed into re.subn!  Here we go!"
        text_pattern = r"(?P<first>this )(?P<second>.*?)(!)"
        pattern = backrefs.compile_search(text_pattern)
        replace = backrefs.compile_replace(pattern, r'\c\g<first>is awesome\g<3>')
        result, count = pattern.subn(replace, text)

        self.assertEqual(result, "This is awesome!  Here we go!  This is awesome!  Here we go!")
        self.assertEqual(count, 2)

    def test_binary_replace(self):
        """Test that binary regex result is a binary string."""

        text = b"This is some binary text!"
        pattern = backrefs.compile_search(br"\cthis is (\Qsome binary text\E)!")
        expand = backrefs.compile_replace(pattern, br'\C\1\E')
        m = pattern.match(text)
        result = expand(m)
        self.assertEqual(result, b"SOME BINARY TEXT")
        self.assertTrue(isinstance(result, binary_type))
