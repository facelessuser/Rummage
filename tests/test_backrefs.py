# -*- coding: utf-8 -*-
"""Test critic lib."""
from __future__ import unicode_literals
import unittest
from rummage.rummage.rumcore import backrefs as bre
import re
import sys

PY3 = (3, 0) <= sys.version_info < (4, 0)

if PY3:
    binary_type = bytes  # noqa
else:
    binary_type = str  # noqa


class TestSearchTemplate(unittest.TestCase):

    """Search template tests."""

    def test_ascii_upper_props(self):
        """Test ascii uppercase properties."""

        pattern = bre.compile_search(br'EX\c+LE')
        m = pattern.match(br'EXAMPLE')
        self.assertTrue(m is not None)

    def test_ascii_upper_props_group(self):
        """Test ascii uppercase properties in a char group."""

        pattern = bre.compile_search(br'EX[\c]+LE')
        m = pattern.match(br'EXAMPLE')
        self.assertTrue(m is not None)

    def test_ascii_lower_props(self):
        """Test ascii lowercase properties."""

        pattern = bre.compile_search(br'EX\l+LE')
        m = pattern.match(br'EXampLE')
        self.assertTrue(m is not None)

    def test_ascii_lower_props_group(self):
        """Test ascii uppercase properties in a char group."""

        pattern = bre.compile_search(br'EX[\l]+LE')
        m = pattern.match(br'EXampLE')
        self.assertTrue(m is not None)

    def test_ascii_props_mixed_group(self):
        """Test mixed ascii properties in group."""

        pattern = bre.compile_search(br'EX[\l\c]+LE')
        m = pattern.match(br'EXaMpLE')
        self.assertTrue(m is not None)

    def test_ascii_props_mixed(self):
        """Test mixed ascii properties."""

        pattern = bre.compile_search(br'EX\l\c\lLE')
        m = pattern.match(br'EXaMpLE')
        self.assertTrue(m is not None)

    def test_reverse_ascii_lower_props(self):
        """Test reverse ascii lowercase properties."""

        pattern = bre.compile_search(br'EX\L+LE')
        m = pattern.match(br'EXAMPLE')
        self.assertTrue(m is not None)

    def test_reverse_ascii_lower_props_group(self):
        """Test reverse ascii lowercase properties in a group."""

        pattern = bre.compile_search(br'EX[\L]+LE')
        m = pattern.match(br'EXAMPLE')
        self.assertTrue(m is not None)

    def test_reverse_ascii_upper_props(self):
        """Test reveerse ascii uppercase properties."""

        pattern = bre.compile_search(br'EX\C+LE')
        m = pattern.match(br'EXampLE')
        self.assertTrue(m is not None)

    def test_reverse_ascii_upper_props_group(self):
        """Test reverse ascii uppercase properties in a group."""

        pattern = bre.compile_search(br'EX[\C]+LE')
        m = pattern.match(br'EXampLE')
        self.assertTrue(m is not None)

    def test_reverse_ascii_props_mixed_group(self):
        """Test reverse mixed ascii properties in a group."""

        pattern = bre.compile_search(br'EX[\C\L]+LE')
        m = pattern.match(br'EXaMpLE')
        self.assertTrue(m is not None)

    def test_reverse_ascii_props_mixed(self):
        """Test reverse ascii properties."""

        pattern = bre.compile_search(br'EX\C\L\CLE')
        m = pattern.match(br'EXaMpLE')
        self.assertTrue(m is not None)

    def test_unrecognized_backrefs(self):
        """Test unrecognized backrefs."""

        result = bre.SearchTemplate(r'Testing unrecognized backrefs \k!').apply()
        self.assertEqual(r'Testing unrecognized backrefs \k!', result)

    def test_quote(self):
        """Test quoting/escaping."""

        result = bre.SearchTemplate(r'Testing \Q(\s+[quote]*\s+)?\E!').apply()
        self.assertEqual(r'Testing %s!' % re.escape(r'(\s+[quote]*\s+)?'), result)

    def test_normal_backrefs(self):
        """
        Test normal builtin backrefs.

        They should all pass through unaltered.
        """

        result = bre.SearchTemplate(r'\a\b\f\n\r\t\v\A\b\B\d\D\s\S\w\W\Z\\[\b]').apply()
        self.assertEqual(r'\a\b\f\n\r\t\v\A\b\B\d\D\s\S\w\W\Z\\[\b]', result)

    def test_quote_no_end(self):
        r"""Test quote where no \E is defined."""

        result = bre.SearchTemplate(r'Testing \Q(quote) with no [end]!').apply()
        self.assertEqual(r'Testing %s' % re.escape(r'(quote) with no [end]!'), result)

    def test_quote_avoid_char_blocks(self):
        """Test that quote backrefs are ignored in character groups."""

        result = bre.SearchTemplate(r'Testing [\Qchar\E block] [\Q(AVOIDANCE)\E]!').apply()
        self.assertEqual(r'Testing [char block] [(AVOIDANCE)]!', result)

    def test_quote_avoid_with_right_square_bracket_first(self):
        """Test that quote backrefs are ignored in character groups that have a right square bracket as first char."""

        result = bre.SearchTemplate(r'Testing [^]\Qchar\E block] []\Q(AVOIDANCE)\E]!').apply()
        self.assertEqual(r'Testing [^]char block] [](AVOIDANCE)]!', result)

    def test_extraneous_end_char(self):
        r"""Test that stray '\E's get removed."""

        result = bre.SearchTemplate(r'Testing \Eextraneous end char\E!').apply()
        self.assertEqual(r'Testing extraneous end char!', result)

    def test_escaped_backrefs(self):
        """Ensure escaped backrefs don't get processed."""

        result = bre.SearchTemplate(r'\\cTesting\\C \\lescaped\\L \\Qbackrefs\\E!').apply()
        self.assertEqual(r'\cTesting\C \lescaped\L \Qbackrefs\E!', result)

    def test_escaped_escaped_backrefs(self):
        """Ensure escaping escaped backrefs do get processed."""

        result = bre.SearchTemplate(r'Testing escaped escaped \\\Qbackrefs\\\E!').apply()
        self.assertEqual(r'Testing escaped escaped \backrefs\\!', result)

    def test_escaped_escaped_escaped_backrefs(self):
        """Ensure escaping escaped escaped backrefs don't get processed."""

        result = bre.SearchTemplate(r'Testing escaped escaped \\\\Qbackrefs\\\\E!').apply()
        self.assertEqual(r'Testing escaped escaped \\Qbackrefs\\E!', result)

    def test_escaped_escaped_escaped_escaped_backrefs(self):
        """
        Ensure escaping escaped escaped escaped backrefs do get processed.

        This is far enough to prove out that we are handeling them well enough.
        """

        result = bre.SearchTemplate(r'Testing escaped escaped \\\\\Qbackrefs\\\\\E!').apply()
        self.assertEqual(r'Testing escaped escaped \\backrefs\\\\!', result)

    def test_normal_escaping(self):
        """Normal escaping should be unaltered."""

        result = bre.SearchTemplate(r'\n \\n \\\n \\\\n \\\\\n').apply()
        self.assertEqual(r'\n \\n \\\n \\\\n \\\\\n', result)

    def test_normal_escaping2(self):
        """Normal escaping should be unaltered part2."""

        result = bre.SearchTemplate(r'\e \\e \\\e \\\\e \\\\\e').apply()
        self.assertEqual(r'\e \\e \\\e \\\\e \\\\\e', result)

    def test_unicode_shorthand_properties_capital(self):
        """
        Excercising that unicode properties are built correctly by testing shorthand lower and upper.

        We want to test uppercase and make sure things make sense,
        and then test lower case later.  Not extensive, just making sure its genrally working.
        """

        pattern = bre.compile_search(r'EX\cMPLE', re.UNICODE)
        m = pattern.match(r'EXÁMPLE')
        self.assertTrue(m is not None)
        m = pattern.match(r'exámple')
        self.assertTrue(m is None)

    def test_unicode_shorthand_properties_lower(self):
        """Exercise the unicode shorthand properties for lower case."""

        pattern = bre.compile_search(r'ex\lmple', re.UNICODE)
        m = pattern.match('exámple')
        self.assertTrue(m is not None)
        m = pattern.match('EXÁMPLE')
        self.assertTrue(m is None)

    def test_unicode_shorthand_properties_in_char_group(self):
        """Exercise the unicode shorthand properties inside a char group."""

        pattern = bre.compile_search(r'ex[\l\c]mple', re.UNICODE)
        m = pattern.match('exámple')
        self.assertTrue(m is not None)
        m = pattern.match('exÁmple')
        self.assertTrue(m is not None)

    def test_unicode_shorthand_ascii_only(self):
        """Ensure that when the unicode flag is not used, only ascii properties are used."""

        pattern = bre.compile_search(r'ex\lmple')
        m = pattern.match('exámple')
        self.assertTrue(m is None)
        m = pattern.match('example')
        self.assertTrue(m is not None)

    def test_unicode_properties_capital(self):
        """
        Excercising that unicode properties are built correctly.

        We want to test uppercase and make sure things make sense,
        and then test lower case later.  Not extensive, just making sure its genrally working.
        """

        pattern = bre.compile_search(r'EX\p{Lu}MPLE', re.UNICODE)
        m = pattern.match(r'EXÁMPLE')
        self.assertTrue(m is not None)
        m = pattern.match(r'exámple')
        self.assertTrue(m is None)

    def test_unicode_properties_lower(self):
        """Exercise the unicode properties for lower case."""

        pattern = bre.compile_search(r'ex\p{Ll}mple', re.UNICODE)
        m = pattern.match('exámple')
        self.assertTrue(m is not None)
        m = pattern.match('EXÁMPLE')
        self.assertTrue(m is None)

    def test_unicode_properties_in_char_group(self):
        """Exercise the unicode properties inside a char group."""

        pattern = bre.compile_search(r'ex[\p{Ll}\p{Lu}]mple', re.UNICODE)
        m = pattern.match('exámple')
        self.assertTrue(m is not None)
        m = pattern.match('exÁmple')
        self.assertTrue(m is not None)

    def test_unicode_properties_names(self):
        """Test unicode group friendly names."""

        pattern = bre.compile_search(r'ex[\p{Letter}]mple', re.UNICODE)
        m = pattern.match('exámple')
        self.assertTrue(m is not None)
        m = pattern.match('exÁmple')
        self.assertTrue(m is not None)

    def test_unicode_properties_inverse(self):
        """Excercising inverse unicode properties."""

        pattern = bre.compile_search(r'\P{Po}', re.UNICODE)
        m = pattern.match(r'⁋')
        self.assertTrue(m is None)
        m = pattern.match(r'P')
        self.assertTrue(m is not None)

    def test_negated_unicode_properties_inverse(self):
        """Excercising negated inverse unicode properties."""

        pattern = bre.compile_search(r'[^\P{Po}]', re.UNICODE)
        m = pattern.match(r'⁋')
        self.assertTrue(m is not None)
        m = pattern.match(r'P')
        self.assertTrue(m is None)

    def test_binary_unicode_ignore(self):
        r"""Binary patterns should not process \p references."""

        pattern = bre.compile_search(br'EX\p{Lu}MPLE')
        m = pattern.match(br'EXp{Lu}MPLE')
        self.assertTrue(m is not None)

    def test_detect_verbose_string_flag(self):
        """Test verbose string flag (?x)."""

        pattern = bre.compile_search(
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

    def test_detect_complex_verbose_string_flag(self):
        """Test complex verbose string flag (?x)."""

        pattern = bre.compile_search(
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

    def test_verbose_comment_no_nl(self):
        """Test verbose comment with no newline."""

        pattern = bre.compile_search(
            '(?x)This is a # comment with no new line'
        )

        self.assertEqual(
            pattern.pattern,
            '(?x)This is a # comment with no new line'
        )

    def test_detect_verbose(self):
        """Test verbose."""

        pattern = bre.compile_search(
            r'''
            This is a # \Qcomment\E
            This is not a \# \Qcomment\E
            This is not a [#\ ] \Qcomment\E
            This is not a [\#] \Qcomment\E
            This\ is\ a # \Qcomment\E
            ''',
            re.VERBOSE
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

        pattern = bre.compile_search(
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

    def test_other_backrefs(self):
        """Test that other backrefs make it through."""

        pattern = bre.compile_search(
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

    def test_re_pattern_input(self):
        """Test that search pattern input can be a compiled re pattern."""

        pattern1 = re.compile("(test)")
        pattern2 = bre.compile_search(pattern1)
        m = pattern2.match('test')
        self.assertTrue(m is not None)


class TestReplaceTemplate(unittest.TestCase):

    """Test replace template."""

    def test_get_replace_template_string(self):
        """Test retrieval of the replace template original string."""

        pattern = re.compile(r"(some)(.*?)(pattern)(!)")
        template = bre.ReplaceTemplate(pattern, r'\c\1\2\C\3\E\4')

        self.assertEqual(r'\c\1\2\C\3\E\4', template.get_base_template())

    def test_uppercase(self):
        """Test uppercase."""

        text = "This is a test for uppercase!"
        pattern = re.compile(r"(.*?)(uppercase)(!)")
        expand = bre.compile_replace(pattern, r'\1\c\2\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a test for Uppercase!', results)

    def test_lowercase(self):
        """Test lowercase."""

        text = "This is a test for LOWERCASE!"
        pattern = re.compile(r"(.*?)(LOWERCASE)(!)")
        expand = bre.compile_replace(pattern, r'\1\l\2\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a test for lOWERCASE!', results)

    def test_span_uppercase(self):
        """Test span uppercase."""

        text = "This is a test for uppercase!"
        pattern = re.compile(r"(.*?)(uppercase)(!)")
        expand = bre.compile_replace(pattern, r'\1\C\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a test for UPPERCASE!', results)

    def test_span_lowercase(self):
        """Test span lowercase."""

        text = "This is a test for LOWERCASE!"
        pattern = re.compile(r"(.*?)(LOWERCASE)(!)")
        expand = bre.compile_replace(pattern, r'\1\L\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a test for lowercase!', results)

    def test_extraneous_end_char(self):
        """Test for extraneous end characters."""

        text = "This is a test for extraneous \\E chars!"
        pattern = re.compile(r"(.*?)(extraneous)(.*)")
        expand = bre.compile_replace(pattern, r'\1\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a test for extraneous \\E chars!', results)

    def test_normal_backrefs(self):
        """Test for normal backrefs."""

        text = "This is a test for normal backrefs!"
        pattern = re.compile(r"(.*?)(normal)(.*)")
        expand = bre.compile_replace(pattern, '\\1\\2\t\\3 \u0067\147\v\f\n')
        results = expand(pattern.match(text))

        self.assertEqual('This is a test for normal\t backrefs! gg\v\f\n', results)

    def test_span_case_no_end(self):
        r"""Test case where no \E is defined."""

        text = "This is a test for uppercase with no end!"
        pattern = re.compile(r"(.*?)(uppercase)(.*)")
        expand = bre.compile_replace(pattern, r'\1\C\2\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a test for UPPERCASE WITH NO END!', results)

    def test_span_upper_after_upper(self):
        """Test uppercase followed by uppercase span."""

        text = "This is a complex uppercase test!"
        pattern = re.compile(r"(.*?)(uppercase)(.*)")
        expand = bre.compile_replace(pattern, r'\1\c\C\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a complex UPPERCASE test!', results)

    def test_span_lower_after_lower(self):
        """Test lowercase followed by lowercase span."""

        text = "This is a complex LOWERCASE test!"
        pattern = re.compile(r"(.*?)(LOWERCASE)(.*)")
        expand = bre.compile_replace(pattern, r'\1\l\L\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a complex lowercase test!', results)

    def test_span_upper_around_upper(self):
        """Test uppercase span around an uppercase."""

        text = "This is a complex uppercase test!"
        pattern = re.compile(r"(.*?)(uppercase)(.*)")
        expand = bre.compile_replace(pattern, r'\1\C\c\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a complex UPPERCASE test!', results)

    def test_span_lower_around_lower(self):
        """Test lowercase span around an lowercase."""

        text = "This is a complex LOWERCASE test!"
        pattern = re.compile(r"(.*?)(LOWERCASE)(.*)")
        expand = bre.compile_replace(pattern, r'\1\L\l\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a complex lowercase test!', results)

    def test_upper_after_upper(self):
        """Test uppercase after uppercase."""

        text = "This is a complex uppercase test!"
        pattern = re.compile(r"(.*?)(uppercase)(.*)")
        expand = bre.compile_replace(pattern, r'\1\c\c\2\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a complex Uppercase test!', results)

    def test_upper_span_inside_upper_span(self):
        """Test uppercase span inside uppercase span."""

        text = "This is a complex uppercase test!"
        pattern = re.compile(r"(.*?)(uppercase)(.*)")
        expand = bre.compile_replace(pattern, r'\1\C\C\2\E\3\E')
        results = expand(pattern.match(text))

        self.assertEqual('This is a complex UPPERCASE TEST!', results)

    def test_lower_after_lower(self):
        """Test lowercase after lowercase."""

        text = "This is a complex LOWERCASE test!"
        pattern = re.compile(r"(.*?)(LOWERCASE)(.*)")
        expand = bre.compile_replace(pattern, r'\1\l\l\2\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a complex lOWERCASE test!', results)

    def test_lower_span_inside_lower_span(self):
        """Test lowercase span inside lowercase span."""

        text = "This is a complex LOWERCASE TEST!"
        pattern = re.compile(r"(.*?)(LOWERCASE)(.*)")
        expand = bre.compile_replace(pattern, r'\1\L\L\2\E\3\E')
        results = expand(pattern.match(text))

        self.assertEqual('This is a complex lowercase test!', results)

    def test_span_upper_after_lower(self):
        """Test lowercase followed by uppercase span."""

        text = "This is a complex uppercase test!"
        pattern = re.compile(r"(.*?)(uppercase)(.*)")
        expand = bre.compile_replace(pattern, r'\1\l\C\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a complex uPPERCASE test!', results)

    def test_span_lower_after_upper(self):
        """Test uppercase followed by lowercase span."""

        text = "This is a complex LOWERCASE test!"
        pattern = re.compile(r"(.*?)(LOWERCASE)(.*)")
        expand = bre.compile_replace(pattern, r'\1\c\L\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a complex Lowercase test!', results)

    def test_span_upper_around_lower(self):
        """Test uppercase span around a lowercase."""

        text = "This is a complex uppercase test!"
        pattern = re.compile(r"(.*?)(uppercase)(.*)")
        expand = bre.compile_replace(pattern, r'\1\C\l\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a complex uPPERCASE test!', results)

    def test_span_lower_around_upper(self):
        """Test lowercase span around an uppercase."""

        text = "This is a complex LOWERCASE test!"
        pattern = re.compile(r"(.*?)(LOWERCASE)(.*)")
        expand = bre.compile_replace(pattern, r'\1\L\c\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a complex Lowercase test!', results)

    def test_end_after_single_case(self):
        r"""Test that \E after a single case such as \l is handled proper."""

        text = "This is a single case end test!"
        pattern = re.compile(r"(.*?)(case)(.*)")
        expand = bre.compile_replace(pattern, r'\1\l\E\2\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a single case end test!', results)

    def test_end_after_single_case_nested(self):
        r"""Test that \E after a single case such as \l is handled proper inside a span."""

        text = "This is a nested single case end test!"
        pattern = re.compile(r"(.*?)(case)(.*)")
        expand = bre.compile_replace(pattern, r'\1\C\2\c\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a nested single CASE end test!', results)

    def test_single_case_at_end(self):
        """Test when a single case backref is the final char."""

        text = "This is a single case at end test!"
        pattern = re.compile(r"(.*?)(case)(.*)")
        expand = bre.compile_replace(pattern, r'\1\2\3\c')
        results = expand(pattern.match(text))

        self.assertEqual('This is a single case at end test!', results)

    def test_single_case_not_on_group(self):
        """Test single case when not applied to a group."""

        text = "This is a single case test that is not on a group!"
        pattern = re.compile(r"(.*)")
        expand = bre.compile_replace(pattern, r'\cstill works!')
        results = expand(pattern.match(text))

        self.assertEqual('Still works!', results)

    def test_case_span_not_on_group(self):
        """Test case span when not applied to a group."""

        text = "This is a case test that is not on a group!"
        pattern = re.compile(r"(.*)")
        expand = bre.compile_replace(pattern, r'\Cstill\E works!')
        results = expand(pattern.match(text))

        self.assertEqual('STILL works!', results)

    def test_escaped_backrefs(self):
        """Test escaped backrefs."""

        text = "This is a test of escaped backrefs!"
        pattern = re.compile(r"(.*)")
        expand = bre.compile_replace(pattern, r'\\\\l\\c\1')
        results = expand(pattern.match(text))

        self.assertEqual(r'\\l\cThis is a test of escaped backrefs!', results)

    def test_escaped_slash_before_backref(self):
        """Test deepeer escaped slash."""

        text = "this is a test of escaped slash backrefs!"
        pattern = re.compile(r"(.*)")
        expand = bre.compile_replace(pattern, r'\\\\\lTest: \\\c\1')
        results = expand(pattern.match(text))

        self.assertEqual(r'\\test: \This is a test of escaped slash backrefs!', results)

    def test_normal_escaping(self):
        """Test normal escaped slash."""

        text = "This is a test of normal escaping!"
        pattern = re.compile(r"(.*)")
        repl_pattern = r'\e \\e \\\e \\\\e \\\\\e'
        expand = bre.compile_replace(pattern, repl_pattern)
        m = pattern.match(text)
        results = expand(m)
        results2 = pattern.sub(repl_pattern, text)

        self.assertEqual(results2, results)
        self.assertEqual('\e \\e \\\e \\\\e \\\\\e', results)

    def test_escaped_slash_at_eol(self):
        """Test escaped slash at end of line."""

        text = "This is a test of eol escaping!"
        pattern = re.compile(r"(.*)")
        expand = bre.compile_replace(pattern, r'\\\\')
        results = expand(pattern.match(text))

        self.assertEqual(r'\\\\', results)

    def test_unrecognized_backrefs(self):
        """Test unrecognized backrefs, or literal backslash before a char."""

        text = "This is a test of unrecognized backrefs!"
        pattern = re.compile(r"(.*)")
        expand = bre.compile_replace(pattern, r'\k\1')
        results = expand(pattern.match(text))

        self.assertEqual(r'\kThis is a test of unrecognized backrefs!', results)

    def test_ignore_group(self):
        """Test that backrefs inserted by matching groups are passed over."""

        text = r"This is a test to see if \Cbackre\Efs in gr\coups get ig\Lnor\led proper!"
        pattern = re.compile(r"(This is a test to see if \\Cbackre\\Efs )(.*?)(ig\\Lnor\\led )(proper)(!)")
        expand = bre.compile_replace(pattern, r'Here is the first \C\1\Ethe second \c\2third \L\3\E\4\5')
        results = expand(pattern.match(text))

        self.assertEqual(
            r'Here is the first THIS IS A TEST TO SEE IF \CBACKRE\EFS the second In gr\coups get third '
            r'ig\lnor\led proper!',
            results
        )

    def test_mixed_groups1(self):
        """Test mix of upper and lower case with named groups and a string replace pattern."""

        text = "this is a test for named capture groups!"
        text_pattern = r"(?P<first>this )(?P<second>.*?)(?P<third>named capture )(?P<fourth>groups)(!)"
        pattern = re.compile(text_pattern)

        # Will fail with AttributeError because non-compiled patterns can't be used to resolve
        # group names in replace template.
        expand = bre.compile_replace(text_pattern, r'\l\C\g<first>\l\g<second>\L\c\g<third>\E\g<fourth>\E\5')
        results = expand(pattern.match(text))
        self.assertEqual('tHIS iS A TEST FOR Named capture GROUPS!', results)

    def test_mixed_groups2(self):
        """Test mix of upper and lower case with group indexes and a string replace pattern."""

        text = "this is a test for named capture groups!"
        text_pattern = r"(?P<first>this )(?P<second>.*?)(?P<third>named capture )(?P<fourth>groups)(!)"
        pattern = re.compile(text_pattern)

        # This will pass because we do not need to resolve named groups.
        expand = bre.compile_replace(text_pattern, r'\l\C\g<1>\l\g<2>\L\c\g<3>\E\g<4>\E\5')
        results = expand(pattern.match(text))
        self.assertEqual('tHIS iS A TEST FOR Named capture GROUPS!', results)

    def test_mixed_groups3(self):
        """Test mix of upper and lower case with named groups and a compiled replace pattern."""

        text = "this is a test for named capture groups!"
        text_pattern = r"(?P<first>this )(?P<second>.*?)(?P<third>named capture )(?P<fourth>groups)(!)"
        pattern = re.compile(text_pattern)

        # Now using compiled pattern, we can use named groups in replace template.
        expand = bre.compile_replace(pattern, r'\l\C\g<first>\l\g<second>\L\c\g<third>\E\g<fourth>\E\5')
        results = expand(pattern.match(text))
        self.assertEqual('tHIS iS A TEST FOR Named capture GROUPS!', results)

    def test_as_replace_function(self):
        """Test that replace can be used as a replace function."""

        text = "this will be fed into re.subn!  Here we go!  this will be fed into re.subn!  Here we go!"
        text_pattern = r"(?P<first>this )(?P<second>.*?)(!)"
        pattern = bre.compile_search(text_pattern)
        replace = bre.compile_replace(pattern, r'\c\g<first>is awesome\g<3>')
        result, count = pattern.subn(replace, text)

        self.assertEqual(result, "This is awesome!  Here we go!  This is awesome!  Here we go!")
        self.assertEqual(count, 2)

    def test_binary_replace(self):
        """Test that binary regex result is a binary string."""

        text = b"This is some binary text!"
        pattern = bre.compile_search(br"This is (some binary text)!")
        expand = bre.compile_replace(pattern, br'\C\1\E')
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
        pattern = bre.compile_search('(.*)')
        expand = bre.compile_replace(pattern, repl)

        m = pattern.match(text)
        result = expand(m)

        self.assertEqual('Success!', result)


class TestConvenienceFunctions(unittest.TestCase):

    """Test convenience functions."""

    def test_match(self):
        """Test that match works."""

        m = bre.match(r'This is a test for m[\l]+!', "This is a test for match!")
        self.assertTrue(m is not None)

    def test_search(self):
        """Test that search works."""

        m = bre.search(r'test', "This is a test for search!")
        self.assertTrue(m is not None)

    def test_split(self):
        """Test that split works."""

        self.assertEqual(
            bre.split(r'\W+', "This is a test for split!"),
            ["This", "is", "a", "test", "for", "split", ""]
        )

    def test_sub(self):
        """Test that sub works."""

        self.assertEqual(
            bre.sub(r'tset', 'test', r'This is a tset for sub!'),
            "This is a test for sub!"
        )

    def test_subn(self):
        """Test that subn works."""

        self.assertEqual(
            bre.subn(r'tset', 'test', r'This is a tset for subn! This is a tset for subn!'),
            ('This is a test for subn! This is a test for subn!', 2)
        )

    def test_findall(self):
        """Test that findall works."""

        self.assertEqual(
            bre.findall(r'\w+', 'This is a test for findall!'),
            ["This", "is", "a", "test", "for", "findall"]
        )

    def test_finditer(self):
        """Test that finditer works."""

        count = 0
        for m in bre.finditer(r'\w+', 'This is a test for finditer!'):
            count += 1

        self.assertEqual(count, 6)

    def test_expand(self):
        """Test that expand works."""

        m = bre.match(r'(This is a test for )(m[\l]+!)', "This is a test for match!")
        self.assertEqual(
            bre.expand(m, r'\1\C\2\E'),
            'This is a test for MATCH!'
        )
