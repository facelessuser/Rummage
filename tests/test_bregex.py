# -*- coding: utf-8 -*-
"""Test critic lib."""
from __future__ import unicode_literals
import unittest
from rummage.rummage.rumcore.backrefs import bregex
import regex
import sys

PY3 = (3, 0) <= sys.version_info < (4, 0)

if PY3:
    binary_type = bytes  # noqa
else:
    binary_type = str  # noqa


class TestSearchTemplate(unittest.TestCase):
    """Search template tests."""

    def test_unrecognized_backrefs(self):
        """Test unrecognized backrefs."""

        result = bregex.RegexSearchTemplate(r'Testing unrecognized backrefs \k!').apply()
        self.assertEqual(r'Testing unrecognized backrefs \k!', result)

    def test_quote(self):
        """Test quoting/escaping."""

        result = bregex.RegexSearchTemplate(r'Testing \Q(\s+[quote]*\s+)?\E!').apply()
        self.assertEqual(r'Testing %s!' % regex.escape(r'(\s+[quote]*\s+)?'), result)

    def test_normal_backrefs(self):
        """
        Test normal builtin backrefs.

        They should all pass through unaltered.
        """

        result = bregex.RegexSearchTemplate(r'\a\b\f\n\r\t\v\A\b\B\d\D\s\S\w\W\Z\\[\b]\M\m\G').apply()
        self.assertEqual(r'\a\b\f\n\r\t\v\A\b\B\d\D\s\S\w\W\Z\\[\b]\M\m\G', result)

    def test_quote_no_end(self):
        r"""Test quote where no \E is defined."""

        result = bregex.RegexSearchTemplate(r'Testing \Q(quote) with no [end]!').apply()
        self.assertEqual(r'Testing %s' % regex.escape(r'(quote) with no [end]!'), result)

    def test_quote_avoid_char_blocks(self):
        """Test that quote backrefs are ignored in character groups."""

        result = bregex.RegexSearchTemplate(r'Testing [\Qchar\E block] [\Q(AVOIDANCE)\E]!').apply()
        self.assertEqual(r'Testing [char block] [(AVOIDANCE)]!', result)

    def test_quote_avoid_with_right_square_bracket_first(self):
        """Test that quote backrefs are ignored in character groups that have a right square bracket as first char."""

        result = bregex.RegexSearchTemplate(r'Testing [^]\Qchar\E block] []\Q(AVOIDANCE)\E]!').apply()
        self.assertEqual(r'Testing [^]char block] [](AVOIDANCE)]!', result)

    def test_extraneous_end_char(self):
        r"""Test that stray '\E's get removed."""

        result = bregex.RegexSearchTemplate(r'Testing \Eextraneous end char\E!').apply()
        self.assertEqual(r'Testing extraneous end char!', result)

    def test_escaped_backrefs(self):
        """Ensure escaped backrefs don't get processed."""

        result = bregex.RegexSearchTemplate(r'Testing escaped \\Qbackrefs\\E!').apply()
        self.assertEqual(r'Testing escaped \Qbackrefs\E!', result)

    def test_escaped_escaped_backrefs(self):
        """Ensure escaping escaped backrefs do get processed."""

        result = bregex.RegexSearchTemplate(r'Testing escaped escaped \\\Qbackrefs\\\E!').apply()
        self.assertEqual(r'Testing escaped escaped \backrefs\\!', result)

    def test_escaped_escaped_escaped_backrefs(self):
        """Ensure escaping escaped escaped backrefs don't get processed."""

        result = bregex.RegexSearchTemplate(r'Testing escaped escaped \\\\Qbackrefs\\\\E!').apply()
        self.assertEqual(r'Testing escaped escaped \\Qbackrefs\\E!', result)

    def test_escaped_escaped_escaped_escaped_backrefs(self):
        """
        Ensure escaping escaped escaped escaped backrefs do get processed.

        This is far enough to prove out that we are handeling them well enough.
        """

        result = bregex.RegexSearchTemplate(r'Testing escaped escaped \\\\\Qbackrefs\\\\\E!').apply()
        self.assertEqual(r'Testing escaped escaped \\backrefs\\\\!', result)

    def test_normal_escaping(self):
        """Normal escaping should be unaltered."""

        result = bregex.RegexSearchTemplate(r'\n \\n \\\n \\\\n \\\\\n').apply()
        self.assertEqual(r'\n \\n \\\n \\\\n \\\\\n', result)

    def test_normal_escaping2(self):
        """Normal escaping should be unaltered part2."""

        result = bregex.RegexSearchTemplate(r'\e \\e \\\e \\\\e \\\\\e').apply()
        self.assertEqual(r'\e \\e \\\e \\\\e \\\\\e', result)

    def test_unicode_and_verbose_flag(self):
        """Test that VERBOSE and UNICODE togethter come through."""

        pattern = bregex.compile_search(r'Some pattern', flags=bregex.VERBOSE | bregex.UNICODE)
        self.assertTrue(pattern.flags & bregex.UNICODE and pattern.flags & bregex.VERBOSE)

    def test_detect_verbose_string_flag(self):
        """Test verbose string flag (?x)."""

        pattern = bregex.compile_search(
            r'''(?x)
            This is a # \Qcomment\E
            This is not a \# \Qcomment\E
            This is not a [#\ ] \Qcomment\E
            This is not a [\#] \Qcomment\E
            This\ is\ a # \Qcomment\E
            '''
        )

        self.assertEqual(
            pattern.pattern,
            r'''(?x)
            This is a # \Qcomment\E
            This is not a \# comment
            This is not a [#\ ] comment
            This is not a [\#] comment
            This\ is\ a # \Qcomment\E
            '''
        )

    def test_detect_verbose_string_flag_at_end(self):
        """Test verbose string flag (?x) at end."""

        pattern = bregex.compile_search(
            r'''
            This is a # \Qcomment\E
            This is not a \# \Qcomment\E
            This is not a [#\ ] \Qcomment\E
            This is not a [\#] \Qcomment\E
            This\ is\ a # \Qcomment\E (?x)
            '''
        )

        self.assertEqual(
            pattern.pattern,
            r'''
            This is a # \Qcomment\E
            This is not a \# comment
            This is not a [#\ ] comment
            This is not a [\#] comment
            This\ is\ a # \Qcomment\E (?x)
            '''
        )

    def test_ignore_verbose_string(self):
        """Test verbose string flag (?x) in char set."""

        pattern = bregex.compile_search(
            r'''
            This is not a # \Qcomment\E
            This is not a \# \Qcomment\E
            This is not a [#\ (?x)] \Qcomment\E
            This is not a [\#] \Qcomment\E
            This\ is\ not a # \Qcomment\E
            '''
        )

        self.assertEqual(
            pattern.pattern,
            r'''
            This is not a # comment
            This is not a \# comment
            This is not a [#\ (?x)] comment
            This is not a [\#] comment
            This\ is\ not a # comment
            '''
        )

    def test_verbose_string_in_quote(self):
        """Test verbose string flag (?x) in quote."""

        pattern = bregex.compile_search(
            r'''
            This is not a # \Qcomment(?x)\E
            This is not a \# \Qcomment\E
            This is not a [#\ ] \Qcomment\E
            This is not a [\#] \Qcomment\E
            This\ is\ not a # \Qcomment\E
            '''
        )

        self.assertEqual(
            pattern.pattern,
            r'''
            This is not a # comment\(\?x\)
            This is not a \# comment
            This is not a [#\ ] comment
            This is not a [\#] comment
            This\ is\ not a # comment
            '''
        )

    def test_detect_complex_verbose_string_flag(self):
        """Test complex verbose string flag (?x)."""

        pattern = bregex.compile_search(
            r'''
            (?ixu)
            This is a # \Qcomment\E
            This is not a \# \Qcomment\E
            This is not a [#\ ] \Qcomment\E
            This is not a [\#] \Qcomment\E
            This\ is\ a # \Qcomment\E
            '''
        )

        self.assertEqual(
            pattern.pattern,
            r'''
            (?ixu)
            This is a # \Qcomment\E
            This is not a \# comment
            This is not a [#\ ] comment
            This is not a [\#] comment
            This\ is\ a # \Qcomment\E
            '''
        )

    def test_version0_string_flag(self):
        """Test finding V0 string flag."""

        template = bregex.RegexSearchTemplate(r'Testing for (?V0) version flag.', False, False)
        template.apply()
        self.assertTrue(template.version & bregex.V0)

    def test_version0_string_flag_in_group(self):
        """Test ignoring V0 string flag in group will still use the default."""

        template = bregex.RegexSearchTemplate(r'Testing for [(?V0)] version flag.', False, False)
        template.apply()
        self.assertTrue(template.version & bregex.DEFAULT_VERSION)

    def test_version0_string_flag_escaped(self):
        """Test ignoring V0 string flag in group will still use the default."""

        template = bregex.RegexSearchTemplate(r'Testing for \(?V0) version flag.', False, False)
        template.apply()
        self.assertTrue(template.version & bregex.DEFAULT_VERSION)

    def test_version0_string_flag_unescaped(self):
        """Test unescaped V0 string flag."""

        template = bregex.RegexSearchTemplate(r'Testing for \\(?V0) version flag.', False, False)
        template.apply()
        self.assertTrue(template.version & bregex.V0)

    def test_version0_string_flag_escaped_deep(self):
        """Test deep escaped V0 flag will still use the default."""

        template = bregex.RegexSearchTemplate(r'Testing for \\\(?V0) version flag.', False, False)
        template.apply()
        self.assertTrue(template.version & bregex.DEFAULT_VERSION)

    def test_version1_string_flag(self):
        """Test finding V1 string flag."""

        template = bregex.RegexSearchTemplate(r'Testing for (?V1) version flag.', False, False)
        template.apply()
        self.assertTrue(template.version & bregex.V1)

    def test_version1_string_flag_in_group(self):
        """Test ignoring V1 string flag in group."""

        template = bregex.RegexSearchTemplate(r'Testing for [(?V1)] version flag.', False, False)
        template.apply()
        self.assertTrue(template.version & bregex.DEFAULT_VERSION)

    def test_version1_string_flag_escaped(self):
        """Test ignoring V1 string flag in group."""

        template = bregex.RegexSearchTemplate(r'Testing for \(?V1) version flag.', False, False)
        template.apply()
        self.assertTrue(template.version & bregex.DEFAULT_VERSION)

    def test_version1_string_flag_unescaped(self):
        """Test unescaped V1 string flag."""

        template = bregex.RegexSearchTemplate(r'Testing for \\(?V1) version flag.', False, False)
        template.apply()
        self.assertTrue(template.version & bregex.V1)

    def test_version1_string_flag_escaped_deep(self):
        """Test deep escaped V1 flag."""

        template = bregex.RegexSearchTemplate(r'Testing for \\\(?V1) version flag.', False, False)
        template.apply()
        self.assertTrue(template.version & bregex.DEFAULT_VERSION)

    def test_verbose_comment_no_nl(self):
        """Test verbose comment with no newline."""

        pattern = bregex.compile_search(
            '(?x)This is a # comment with no new line'
        )

        self.assertEqual(
            pattern.pattern,
            '(?x)This is a # comment with no new line'
        )

    def test_version0_and_verbose_flag(self):
        """Test that VERBOSE and V0 togethter come through."""

        pattern = bregex.compile_search(r'Some pattern', flags=bregex.VERBOSE | bregex.V0)
        self.assertTrue(pattern.flags & bregex.V0 and pattern.flags & bregex.VERBOSE)

    def test_version1_and_verbose_flag(self):
        """Test that VERBOSE and V1 togethter come through."""

        pattern = bregex.compile_search(r'Some pattern', flags=bregex.VERBOSE | bregex.V1)
        self.assertTrue(pattern.flags & bregex.V1 and pattern.flags & bregex.VERBOSE)

    def test_detect_verbose(self):
        """Test verbose."""

        pattern = bregex.compile_search(
            r'''
            This is a # \Qcomment\E
            This is not a \# \Qcomment\E
            This is not a [#\ ] \Qcomment\E
            This is not a [\#] \Qcomment\E
            This\ is\ a # \Qcomment\E
            ''',
            regex.VERBOSE
        )

        self.assertEqual(
            pattern.pattern,
            r'''
            This is a # \Qcomment\E
            This is not a \# comment
            This is not a [#\ ] comment
            This is not a [\#] comment
            This\ is\ a # \Qcomment\E
            '''
        )

    def test_no_verbose(self):
        """Test no verbose."""

        pattern = bregex.compile_search(
            r'''
            This is a # \Qcomment\E
            This is not a \# \Qcomment\E
            This is not a [#\ ] \Qcomment\E
            This is not a [\#] \Qcomment\E
            This\ is\ a # \Qcomment\E
            '''
        )

        self.assertEqual(
            pattern.pattern,
            r'''
            This is a # comment
            This is not a \# comment
            This is not a [#\ ] comment
            This is not a [\#] comment
            This\ is\ a # comment
            '''
        )

    def test_other_backrefs_v0(self):
        """Test that other backrefs make it through."""

        pattern = bregex.compile_search(
            r'''(?x)
            This \bis a # \Qcomment\E
            This is\w+ not a \# \Qcomment\E
            '''
        )

        self.assertEqual(
            pattern.pattern,
            r'''(?x)
            This \bis a # \Qcomment\E
            This is\w+ not a \# comment
            '''
        )

    def test_detect_verbose_v1(self):
        """Test verbose."""

        pattern = bregex.compile_search(
            r'''(?V1)
            This is a # \Qcomment\E
            This is not a \# \Qcomment\E
            This is not a [#\ ] \Qcomment\E
            This is not a [\#] \Qcomment\E
            This\ is\ a # \Qcomment\E
            ''',
            regex.VERBOSE
        )

        self.assertEqual(
            pattern.pattern,
            r'''(?V1)
            This is a # \Qcomment\E
            This is not a \# comment
            This is not a [#\ ] comment
            This is not a [\#] comment
            This\ is\ a # \Qcomment\E
            '''
        )

    def test_no_verbose_v1(self):
        """Test no verbose."""

        pattern = bregex.compile_search(
            r'''(?V1)
            This is a # \Qcomment\E
            This is not a \# \Qcomment\E
            This is not a [^#\ ] \Qcomment\E
            This is not a [\#[^\ \t]] \Qcomment\E
            This\ is\ a # \Qcomment also'''
        )

        self.assertEqual(
            pattern.pattern,
            r'''(?V1)
            This is a # comment
            This is not a \# comment
            This is not a [^#\ ] comment
            This is not a [\#[^\ \t]] comment
            This\ is\ a # comment\ also'''
        )

    def test_other_backrefs_v1(self):
        """Test that other backrefs make it through."""

        pattern = bregex.compile_search(
            r'''(?xV1)
            This \bis a # \Qcomment\E
            This is\w+ not a \# \Qcomment\E
            '''
        )

        self.assertEqual(
            pattern.pattern,
            r'''(?xV1)
            This \bis a # \Qcomment\E
            This is\w+ not a \# comment
            '''
        )

    def test_regex_pattern_input(self):
        """Test that search pattern input can be a compiled bregex pattern."""

        pattern1 = regex.compile("(test)")
        pattern2 = bregex.compile_search(pattern1)
        m = pattern2.match('test')
        self.assertTrue(m is not None)


class TestReplaceTemplate(unittest.TestCase):
    """Test replace template."""

    def test_get_replace_template_string(self):
        """Test retrieval of the replace template original string."""

        pattern = regex.compile(r"(some)(.*?)(pattern)(!)")
        template = bregex.RegexReplaceTemplate(pattern, r'\c\1\2\C\3\E\4')

        self.assertEqual(r'\c\1\2\C\3\E\4', template.get_base_template())

    def test_uppercase(self):
        """Test uppercase."""

        text = "This is a test for uppercase!"
        pattern = regex.compile(r"(.*?)(uppercase)(!)")
        expand = bregex.compile_replace(pattern, r'\1\c\2\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a test for Uppercase!', results)

    def test_lowercase(self):
        """Test lowercase."""

        text = "This is a test for LOWERCASE!"
        pattern = regex.compile(r"(.*?)(LOWERCASE)(!)")
        expand = bregex.compile_replace(pattern, r'\1\l\2\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a test for lOWERCASE!', results)

    def test_span_uppercase(self):
        """Test span uppercase."""

        text = "This is a test for uppercase!"
        pattern = regex.compile(r"(.*?)(uppercase)(!)")
        expand = bregex.compile_replace(pattern, r'\1\C\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a test for UPPERCASE!', results)

    def test_span_lowercase(self):
        """Test span lowercase."""

        text = "This is a test for LOWERCASE!"
        pattern = regex.compile(r"(.*?)(LOWERCASE)(!)")
        expand = bregex.compile_replace(pattern, r'\1\L\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a test for lowercase!', results)

    def test_extraneous_end_char(self):
        """Test for extraneous end characters."""

        text = "This is a test for extraneous \\E chars!"
        pattern = regex.compile(r"(.*?)(extraneous)(.*)")
        expand = bregex.compile_replace(pattern, r'\1\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a test for extraneous \\E chars!', results)

    def test_normal_backrefs(self):
        """Test for normal backrefs."""

        text = "This is a test for normal backrefs!"
        pattern = regex.compile(r"(.*?)(normal)(.*)")
        expand = bregex.compile_replace(pattern, '\\1\\2\t\\3 \u0067\147\v\f\n')
        results = expand(pattern.match(text))

        self.assertEqual('This is a test for normal\t backrefs! gg\v\f\n', results)

    def test_span_case_no_end(self):
        r"""Test case where no \E is defined."""

        text = "This is a test for uppercase with no end!"
        pattern = regex.compile(r"(.*?)(uppercase)(.*)")
        expand = bregex.compile_replace(pattern, r'\1\C\2\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a test for UPPERCASE WITH NO END!', results)

    def test_span_upper_after_upper(self):
        """Test uppercase followed by uppercase span."""

        text = "This is a complex uppercase test!"
        pattern = regex.compile(r"(.*?)(uppercase)(.*)")
        expand = bregex.compile_replace(pattern, r'\1\c\C\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a complex UPPERCASE test!', results)

    def test_span_lower_after_lower(self):
        """Test lowercase followed by lowercase span."""

        text = "This is a complex LOWERCASE test!"
        pattern = regex.compile(r"(.*?)(LOWERCASE)(.*)")
        expand = bregex.compile_replace(pattern, r'\1\l\L\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a complex lowercase test!', results)

    def test_span_upper_around_upper(self):
        """Test uppercase span around an uppercase."""

        text = "This is a complex uppercase test!"
        pattern = regex.compile(r"(.*?)(uppercase)(.*)")
        expand = bregex.compile_replace(pattern, r'\1\C\c\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a complex UPPERCASE test!', results)

    def test_span_lower_around_lower(self):
        """Test lowercase span around an lowercase."""

        text = "This is a complex LOWERCASE test!"
        pattern = regex.compile(r"(.*?)(LOWERCASE)(.*)")
        expand = bregex.compile_replace(pattern, r'\1\L\l\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a complex lowercase test!', results)

    def test_upper_after_upper(self):
        """Test uppercase after uppercase."""

        text = "This is a complex uppercase test!"
        pattern = regex.compile(r"(.*?)(uppercase)(.*)")
        expand = bregex.compile_replace(pattern, r'\1\c\c\2\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a complex Uppercase test!', results)

    def test_upper_span_inside_upper_span(self):
        """Test uppercase span inside uppercase span."""

        text = "This is a complex uppercase test!"
        pattern = regex.compile(r"(.*?)(uppercase)(.*)")
        expand = bregex.compile_replace(pattern, r'\1\C\C\2\E\3\E')
        results = expand(pattern.match(text))

        self.assertEqual('This is a complex UPPERCASE TEST!', results)

    def test_lower_after_lower(self):
        """Test lowercase after lowercase."""

        text = "This is a complex LOWERCASE test!"
        pattern = regex.compile(r"(.*?)(LOWERCASE)(.*)")
        expand = bregex.compile_replace(pattern, r'\1\l\l\2\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a complex lOWERCASE test!', results)

    def test_lower_span_inside_lower_span(self):
        """Test lowercase span inside lowercase span."""

        text = "This is a complex LOWERCASE TEST!"
        pattern = regex.compile(r"(.*?)(LOWERCASE)(.*)")
        expand = bregex.compile_replace(pattern, r'\1\L\L\2\E\3\E')
        results = expand(pattern.match(text))

        self.assertEqual('This is a complex lowercase test!', results)

    def test_span_upper_after_lower(self):
        """Test lowercase followed by uppercase span."""

        text = "This is a complex uppercase test!"
        pattern = regex.compile(r"(.*?)(uppercase)(.*)")
        expand = bregex.compile_replace(pattern, r'\1\l\C\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a complex uPPERCASE test!', results)

    def test_span_lower_after_upper(self):
        """Test uppercase followed by lowercase span."""

        text = "This is a complex LOWERCASE test!"
        pattern = regex.compile(r"(.*?)(LOWERCASE)(.*)")
        expand = bregex.compile_replace(pattern, r'\1\c\L\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a complex Lowercase test!', results)

    def test_span_upper_around_lower(self):
        """Test uppercase span around a lowercase."""

        text = "This is a complex uppercase test!"
        pattern = regex.compile(r"(.*?)(uppercase)(.*)")
        expand = bregex.compile_replace(pattern, r'\1\C\l\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a complex uPPERCASE test!', results)

    def test_span_lower_around_upper(self):
        """Test lowercase span around an uppercase."""

        text = "This is a complex LOWERCASE test!"
        pattern = regex.compile(r"(.*?)(LOWERCASE)(.*)")
        expand = bregex.compile_replace(pattern, r'\1\L\c\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a complex Lowercase test!', results)

    def test_end_after_single_case(self):
        r"""Test that \E after a single case such as \l is handled proper."""

        text = "This is a single case end test!"
        pattern = regex.compile(r"(.*?)(case)(.*)")
        expand = bregex.compile_replace(pattern, r'\1\l\E\2\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a single case end test!', results)

    def test_end_after_single_case_nested(self):
        r"""Test that \E after a single case such as \l is handled proper inside a span."""

        text = "This is a nested single case end test!"
        pattern = regex.compile(r"(.*?)(case)(.*)")
        expand = bregex.compile_replace(pattern, r'\1\C\2\c\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a nested single CASE end test!', results)

    def test_single_case_at_end(self):
        """Test when a single case backref is the final char."""

        text = "This is a single case at end test!"
        pattern = regex.compile(r"(.*?)(case)(.*)")
        expand = bregex.compile_replace(pattern, r'\1\2\3\c')
        results = expand(pattern.match(text))

        self.assertEqual('This is a single case at end test!', results)

    def test_single_case_not_on_group(self):
        """Test single case when not applied to a group."""

        text = "This is a single case test that is not on a group!"
        pattern = regex.compile(r"(.*)")
        expand = bregex.compile_replace(pattern, r'\cstill works!')
        results = expand(pattern.match(text))

        self.assertEqual('Still works!', results)

    def test_case_span_not_on_group(self):
        """Test case span when not applied to a group."""

        text = "This is a case test that is not on a group!"
        pattern = regex.compile(r"(.*)")
        expand = bregex.compile_replace(pattern, r'\Cstill\E works!')
        results = expand(pattern.match(text))

        self.assertEqual('STILL works!', results)

    def test_escaped_backrefs(self):
        """Test escaped backrefs."""

        text = "This is a test of escaped backrefs!"
        pattern = regex.compile(r"(.*)")
        expand = bregex.compile_replace(pattern, r'\\\\l\\c\1')
        results = expand(pattern.match(text))

        self.assertEqual(r'\\l\cThis is a test of escaped backrefs!', results)

    def test_escaped_slash_before_backref(self):
        """Test deepeer escaped slash."""

        text = "this is a test of escaped slash backrefs!"
        pattern = regex.compile(r"(.*)")
        expand = bregex.compile_replace(pattern, r'\\\\\lTest: \\\c\1')
        results = expand(pattern.match(text))

        self.assertEqual(r'\\test: \This is a test of escaped slash backrefs!', results)

    def test_normal_escaping(self):
        """Test normal escaped slash."""

        text = "This is a test of normal escaping!"
        pattern = regex.compile(r"(.*)")
        repl_pattern = r'\e \\e \\\e \\\\e \\\\\e'
        expand = bregex.compile_replace(pattern, repl_pattern)
        m = pattern.match(text)
        results = expand(m)
        results2 = pattern.sub(repl_pattern, text)

        self.assertEqual(results2, results)
        self.assertEqual('\e \\e \\\e \\\\e \\\\\e', results)

    def test_escaped_slash_at_eol(self):
        """Test escaped slash at end of line."""

        text = "This is a test of eol escaping!"
        pattern = regex.compile(r"(.*)")
        expand = bregex.compile_replace(pattern, r'\\\\')
        results = expand(pattern.match(text))

        self.assertEqual(r'\\\\', results)

    def test_unrecognized_backrefs(self):
        """Test unrecognized backrefs, or literal backslash before a char."""

        text = "This is a test of unrecognized backrefs!"
        pattern = regex.compile(r"(.*)")
        expand = bregex.compile_replace(pattern, r'\k\1')
        results = expand(pattern.match(text))

        self.assertEqual(r'\kThis is a test of unrecognized backrefs!', results)

    def test_ignore_group(self):
        """Test that backrefs inserted by matching groups are passed over."""

        text = r"This is a test to see if \Cbackre\Efs in gr\coups get ig\Lnor\led proper!"
        pattern = regex.compile(r"(This is a test to see if \\Cbackre\\Efs )(.*?)(ig\\Lnor\\led )(proper)(!)")
        expand = bregex.compile_replace(pattern, r'Here is the first \C\1\Ethe second \c\2third \L\3\E\4\5')
        results = expand(pattern.match(text))

        self.assertEqual(
            r'Here is the first THIS IS A TEST TO SEE IF \CBACKRE\EFS the second In gr\coups get third '
            r'ig\lnor\led proper!',
            results
        )

    def test_mixed_groups1(self):
        """Test mix of upper and lower case with named groups and a string replace pattern (1)."""

        text = "this is a test for named capture groups!"
        text_pattern = r"(?P<first>this )(?P<second>.*?)(?P<third>named capture )(?P<fourth>groups)(!)"
        pattern = regex.compile(text_pattern)

        # Use uncompiled pattern when compiling replace.
        expand = bregex.compile_replace(text_pattern, r'\l\C\g<first>\l\g<second>\L\c\g<third>\E\g<fourth>\E\5')
        results = expand(pattern.match(text))
        self.assertEqual('tHIS iS A TEST FOR Named capture GROUPS!', results)

    def test_mixed_groups2(self):
        """Test mix of upper and lower case with group indexes and a string replace pattern (2)."""

        text = "this is a test for named capture groups!"
        text_pattern = r"(?P<first>this )(?P<second>.*?)(?P<third>named capture )(?P<fourth>groups)(!)"
        pattern = regex.compile(text_pattern)

        # This will pass because we do not need to resolve named groups.
        expand = bregex.compile_replace(text_pattern, r'\l\C\g<1>\l\g<2>\L\c\g<3>\E\g<4>\E\5')
        results = expand(pattern.match(text))
        self.assertEqual('tHIS iS A TEST FOR Named capture GROUPS!', results)

    def test_mixed_groups3(self):
        """Test mix of upper and lower case with named groups and a compiled replace pattern (3)."""

        text = "this is a test for named capture groups!"
        text_pattern = r"(?P<first>this )(?P<second>.*?)(?P<third>named capture )(?P<fourth>groups)(!)"
        pattern = regex.compile(text_pattern)

        # Now using compiled pattern, we can use named groups in replace template.
        expand = bregex.compile_replace(pattern, r'\l\C\g<first>\l\g<second>\L\c\g<third>\E\g<fourth>\E\5')
        results = expand(pattern.match(text))
        self.assertEqual('tHIS iS A TEST FOR Named capture GROUPS!', results)

    def test_as_replace_function(self):
        """Test that replace can be used as a replace function."""

        text = "this will be fed into regex.subn!  Here we go!  this will be fed into regex.subn!  Here we go!"
        text_pattern = r"(?P<first>this )(?P<second>.*?)(!)"
        pattern = bregex.compile_search(text_pattern)
        replace = bregex.compile_replace(pattern, r'\c\g<first>is awesome\g<3>')
        result, count = pattern.subn(replace, text)

        self.assertEqual(result, "This is awesome!  Here we go!  This is awesome!  Here we go!")
        self.assertEqual(count, 2)

    # def test_nested_group(self):
    #     """Test that replace can be used as a replace function."""

    #     text = "Here is a nested [] group search!"
    #     text_pattern = r"(Here\ is\ a\ nested\ \[(?V1)\]\ group\ )([srch[aeiou]--[iou]]+)(?x)(!)"
    #     pattern = bregex.compile_search(text_pattern)
    #     expand = bregex.compile_replace(pattern, r'\1\2\3')
    #     result = expand(pattern.match(text))

    #     self.assertEqual(result, "Here is a nested [] group search!")

    def test_binary_replace(self):
        """Test that binary regex result is a binary string."""

        text = b"This is some binary text!"
        pattern = bregex.compile_search(br"This is (some binary text)!")
        expand = bregex.compile_replace(pattern, br'\C\1\E')
        m = pattern.match(text)
        result = expand(m)
        self.assertEqual(result, b"SOME BINARY TEXT")
        self.assertTrue(isinstance(result, binary_type))

    def test_function_replace(self):
        """Test replace by passing in replace function."""

        def repl(m):
            """Replace test function."""
            return 'Success!'

        text = "Replace with function test!"
        pattern = bregex.compile_search('(.*)')
        expand = bregex.compile_replace(pattern, repl)

        m = pattern.match(text)
        result = expand(m)

        self.assertEqual('Success!', result)


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions."""

    def test_match(self):
        """Test that match works."""

        m = bregex.match(r'This is a test for match!', "This is a test for match!")
        self.assertTrue(m is not None)

    def test_fullmatch(self):
        """Test that match works."""

        m = bregex.fullmatch(r'This is a test for match!', "This is a test for match!")
        self.assertTrue(m is not None)

    def test_search(self):
        """Test that search works."""

        m = bregex.search(r'test', "This is a test for search!")
        self.assertTrue(m is not None)

    def test_split(self):
        """Test that split works."""

        self.assertEqual(
            bregex.split(r'\W+', "This is a test for split!"),
            ["This", "is", "a", "test", "for", "split", ""]
        )

    def test_splititer(self):
        """Test that split works."""

        array = []
        for x in bregex.splititer(r'\W+', "This is a test for split!"):
            array.append(x)

        self.assertEqual(array, ["This", "is", "a", "test", "for", "split", ""])

    def test_sub(self):
        """Test that sub works."""

        self.assertEqual(
            bregex.sub(r'tset', 'test', r'This is a tset for sub!'),
            "This is a test for sub!"
        )

    def test_subn(self):
        """Test that subn works."""

        self.assertEqual(
            bregex.subn(r'tset', 'test', r'This is a tset for subn! This is a tset for subn!'),
            ('This is a test for subn! This is a test for subn!', 2)
        )

    def test_subf(self):
        """Test that sub works."""

        self.assertEqual(
            bregex.subf(r'(t)(s)(e)(t)', '{1}{3}{2}{4}', r'This is a tset for subf!'),
            "This is a test for subf!"
        )

    def test_subfn(self):
        """Test that subn works."""

        self.assertEqual(
            bregex.subfn(r'(t)(s)(e)(t)', '{1}{3}{2}{4}', r'This is a tset for subfn! This is a tset for subfn!'),
            ('This is a test for subfn! This is a test for subfn!', 2)
        )

    def test_findall(self):
        """Test that findall works."""

        self.assertEqual(
            bregex.findall(r'\w+', 'This is a test for findall!'),
            ["This", "is", "a", "test", "for", "findall"]
        )

    def test_finditer(self):
        """Test that finditer works."""

        count = 0
        for m in bregex.finditer(r'\w+', 'This is a test for finditer!'):
            count += 1

        self.assertEqual(count, 6)

    def test_expand(self):
        """Test that expand works."""

        m = bregex.match(r'(This is a test for )(match!)', "This is a test for match!")
        self.assertEqual(
            bregex.expand(m, r'\1\C\2\E'),
            'This is a test for MATCH!'
        )
