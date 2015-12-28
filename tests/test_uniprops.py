"""Test uniprops."""
from __future__ import unicode_literals
import unittest
import sys
from rummage.rummage.rumcore.backrefs import uniprops

PY3 = (3, 0) <= sys.version_info < (4, 0)

if PY3:
    binary_type = bytes  # noqa
else:
    binary_type = str  # noqa


class TestUniprops(unittest.TestCase):
    """Test Uniprops."""

    def test_gc(self):
        """Test General Category."""

        result = uniprops.get_unicode_property('lu', 'gc')
        self.assertEqual(result, uniprops.unidata.unicode_properties['l']['u'])

    def test_inverse_gc(self):
        """Test inverse General Category."""

        result = uniprops.get_unicode_property('^lu', 'gc')
        self.assertEqual(result, uniprops.unidata.unicode_properties['l']['^u'])

    def test_block(self):
        """Test Block Category."""

        result = uniprops.get_unicode_property('basiclatin', 'blk')
        self.assertEqual(result, uniprops.unidata.unicode_blocks['basiclatin'])

    def test_inverse_block(self):
        """Test inverse Block Category."""

        result = uniprops.get_unicode_property('^basiclatin', 'blk')
        self.assertEqual(result, uniprops.unidata.unicode_blocks['^basiclatin'])

    def test_script(self):
        """Test script Category."""

        result = uniprops.get_unicode_property('latin', 'sc')
        self.assertEqual(result, uniprops.unidata.unicode_scripts['latin'])

    def test_inverse_script(self):
        """Test inverse script Category."""

        result = uniprops.get_unicode_property('^latin', 'sc')
        self.assertEqual(result, uniprops.unidata.unicode_scripts['^latin'])

    def test_bidi(self):
        """Test bidi class Category."""

        result = uniprops.get_unicode_property('en', 'bc')
        self.assertEqual(result, uniprops.unidata.unicode_bidi_classes['en'])

    def test_inverse_bidi(self):
        """Test inverse bidi class Category."""

        result = uniprops.get_unicode_property('^en', 'bc')
        self.assertEqual(result, uniprops.unidata.unicode_bidi_classes['^en'])

    def test_decompostion(self):
        """Test decomposition type Category."""

        result = uniprops.get_unicode_property('small', 'dt')
        self.assertEqual(result, uniprops.unidata.unicode_decomposition_type['small'])

    def test_inverse_decompostion(self):
        """Test inverse decomposition type Category."""

        result = uniprops.get_unicode_property('^small', 'dt')
        self.assertEqual(result, uniprops.unidata.unicode_decomposition_type['^small'])

    def test_canonical(self):
        """Test canonical combining class type Category."""

        result = uniprops.get_unicode_property('200', 'ccc')
        self.assertEqual(result, uniprops.unidata.uniocde_canonical_combining_class['200'])

    def test_inverse_canonical(self):
        """Test inverse canonical combining class type Category."""

        result = uniprops.get_unicode_property('^200', 'ccc')
        self.assertEqual(result, uniprops.unidata.uniocde_canonical_combining_class['^200'])

    def test_eastasianwidth(self):
        """Test east asian width Category."""

        result = uniprops.get_unicode_property('f', 'ea')
        self.assertEqual(result, uniprops.unidata.unicode_east_asian_width['f'])

    def test_inverse_eastasianwidth(self):
        """Test inverse east asian width Category."""

        result = uniprops.get_unicode_property('^f', 'ea')
        self.assertEqual(result, uniprops.unidata.unicode_east_asian_width['^f'])

    def test_hangulsyllabletype(self):
        """Test hangul syllable type type Category."""

        result = uniprops.get_unicode_property('l', 'hst')
        self.assertEqual(result, uniprops.unidata.unicode_hangul_syllable_type['l'])

    def test_inverse_hangulsyllabletype(self):
        """Test inverse hangul syllable type Category."""

        result = uniprops.get_unicode_property('^l', 'hst')
        self.assertEqual(result, uniprops.unidata.unicode_hangul_syllable_type['^l'])

    def test_age(self):
        """Test age Category."""

        result = uniprops.get_unicode_property('5.0', 'age')
        self.assertEqual(result, uniprops.unidata.unicode_age['5.0'])

    def test_inverse_age(self):
        """Test inverse age Category."""

        result = uniprops.get_unicode_property('^5.0', 'age')
        self.assertEqual(result, uniprops.unidata.unicode_age['^5.0'])

    def test_numerictype(self):
        """Test numeric type Category."""

        result = uniprops.get_unicode_property('decimal', 'nt')
        self.assertEqual(result, uniprops.unidata.unicode_numeric_type['decimal'])

    def test_inverse_numerictype(self):
        """Test inverse numeric type Category."""

        result = uniprops.get_unicode_property('^decimal', 'nt')
        self.assertEqual(result, uniprops.unidata.unicode_numeric_type['^decimal'])

    def test_numericvalue(self):
        """Test numeric value Category."""

        result = uniprops.get_unicode_property('1/10', 'nv')
        self.assertEqual(result, uniprops.unidata.unicode_numeric_values['1/10'])

    def test_inverse_numericvalue(self):
        """Test inverse numeric value Category."""

        result = uniprops.get_unicode_property('^1/10', 'nv')
        self.assertEqual(result, uniprops.unidata.unicode_numeric_values['^1/10'])

    def test_joiningtype(self):
        """Test joining type Category."""

        result = uniprops.get_unicode_property('c', 'jt')
        self.assertEqual(result, uniprops.unidata.unicode_joining_type['c'])

    def test_inverse_joiningtype(self):
        """Test inverse joining type Category."""

        result = uniprops.get_unicode_property('^c', 'jt')
        self.assertEqual(result, uniprops.unidata.unicode_joining_type['^c'])

    def test_joininggroup(self):
        """Test joining group Category."""

        result = uniprops.get_unicode_property('e', 'jg')
        self.assertEqual(result, uniprops.unidata.unicode_joining_group['e'])

    def test_inverse_joininggroup(self):
        """Test inverse joining group Category."""

        result = uniprops.get_unicode_property('^e', 'jg')
        self.assertEqual(result, uniprops.unidata.unicode_joining_group['^e'])

    def test_linebreak(self):
        """Test line break Category."""

        result = uniprops.get_unicode_property('jl', 'lb')
        self.assertEqual(result, uniprops.unidata.unicode_line_break['jl'])

    def test_inverse_linebreak(self):
        """Test inverse line break Category."""

        result = uniprops.get_unicode_property('^jl', 'lb')
        self.assertEqual(result, uniprops.unidata.unicode_line_break['^jl'])

    def test_sentencebreak(self):
        """Test sentence break Category."""

        result = uniprops.get_unicode_property('cr', 'sb')
        self.assertEqual(result, uniprops.unidata.unicode_sentence_break['cr'])

    def test_inverse_sentencebreak(self):
        """Test inverse sentence break Category."""

        result = uniprops.get_unicode_property('^cr', 'sb')
        self.assertEqual(result, uniprops.unidata.unicode_sentence_break['^cr'])

    def test_wordbreak(self):
        """Test word break Category."""

        result = uniprops.get_unicode_property('lf', 'wb')
        self.assertEqual(result, uniprops.unidata.unicode_word_break['lf'])

    def test_inverse_wordbreak(self):
        """Test inverse word break Category."""

        result = uniprops.get_unicode_property('^lf', 'wb')
        self.assertEqual(result, uniprops.unidata.unicode_word_break['^lf'])

    def test_graphemeclusterbreak(self):
        """Test grapheme cluster break Category."""

        result = uniprops.get_unicode_property('control', 'gcb')
        self.assertEqual(result, uniprops.unidata.unicode_grapheme_cluster_break['control'])

    def test_inverse_graphemeclusterbreak(self):
        """Test inverse grapheme cluster break Category."""

        result = uniprops.get_unicode_property('^control', 'gcb')
        self.assertEqual(result, uniprops.unidata.unicode_grapheme_cluster_break['^control'])

    def test_nfcquickcheck(self):
        """Test nfc quick check Category."""

        result = uniprops.get_unicode_property('y', 'nfcqc')
        self.assertEqual(result, uniprops.unidata.unicode_nfc_quick_check['y'])

    def test_inverse_nfcquickcheck(self):
        """Test inverse nfc quick check Category."""

        result = uniprops.get_unicode_property('^y', 'nfcqc')
        self.assertEqual(result, uniprops.unidata.unicode_nfc_quick_check['^y'])

    def test_nfkcquickcheck(self):
        """Test nfkc quick check Category."""

        result = uniprops.get_unicode_property('y', 'nfkcqc')
        self.assertEqual(result, uniprops.unidata.unicode_nfkc_quick_check['y'])

    def test_inverse_nfkcquickcheck(self):
        """Test inverse nfkc quick check Category."""

        result = uniprops.get_unicode_property('^y', 'nfkcqc')
        self.assertEqual(result, uniprops.unidata.unicode_nfkc_quick_check['^y'])

    def test_nfdquickcheck(self):
        """Test nfd quick check Category."""

        result = uniprops.get_unicode_property('y', 'nfdqc')
        self.assertEqual(result, uniprops.unidata.unicode_nfd_quick_check['y'])

    def test_inverse_nfdquickcheck(self):
        """Test inverse nfd quick check Category."""

        result = uniprops.get_unicode_property('^y', 'nfdqc')
        self.assertEqual(result, uniprops.unidata.unicode_nfd_quick_check['^y'])

    def test_nfkdquickcheck(self):
        """Test nfkd quick check Category."""

        result = uniprops.get_unicode_property('y', 'nfkdqc')
        self.assertEqual(result, uniprops.unidata.unicode_nfkd_quick_check['y'])

    def test_inverse_nfkdquickcheck(self):
        """Test inverse nfkd quick check Category."""

        result = uniprops.get_unicode_property('^y', 'nfkdqc')
        self.assertEqual(result, uniprops.unidata.unicode_nfkd_quick_check['^y'])

    def test_gc_simple(self):
        """Test gc simple Category."""

        result = uniprops.get_unicode_property('lu')
        self.assertEqual(result, uniprops.unidata.unicode_properties['l']['u'])

    def test_inverse_gc_simple(self):
        """Test inverse gc simple Category."""

        result = uniprops.get_unicode_property('^lu')
        self.assertEqual(result, uniprops.unidata.unicode_properties['l']['^u'])

    def test_is_script(self):
        """Test isscript Category."""

        result = uniprops.get_unicode_property('islatin')
        self.assertEqual(result, uniprops.unidata.unicode_scripts['latin'])

    def test_inverse_is_script(self):
        """Test inverse isscript Category."""

        result = uniprops.get_unicode_property('^islatin')
        self.assertEqual(result, uniprops.unidata.unicode_scripts['^latin'])

    def test_script_simple(self):
        """Test script simple Category."""

        result = uniprops.get_unicode_property('latin')
        self.assertEqual(result, uniprops.unidata.unicode_scripts['latin'])

    def test_inverse_script_simple(self):
        """Test inverse script simple Category."""

        result = uniprops.get_unicode_property('^latin')
        self.assertEqual(result, uniprops.unidata.unicode_scripts['^latin'])

    def test_in_block(self):
        """Test inblock Category."""

        result = uniprops.get_unicode_property('inbasiclatin')
        self.assertEqual(result, uniprops.unidata.unicode_blocks['basiclatin'])

    def test_inverse_in_block(self):
        """Test inverse inblock Category."""

        result = uniprops.get_unicode_property('^inbasiclatin')
        self.assertEqual(result, uniprops.unidata.unicode_blocks['^basiclatin'])

    def test_block_simple(self):
        """Test block simple Category."""

        result = uniprops.get_unicode_property('basiclatin')
        self.assertEqual(result, uniprops.unidata.unicode_blocks['basiclatin'])

    def test_inverse_block_simple(self):
        """Test inverse block simple Category."""

        result = uniprops.get_unicode_property('^basiclatin')
        self.assertEqual(result, uniprops.unidata.unicode_blocks['^basiclatin'])

    def test_binary(self):
        """Test binary Category."""

        result = uniprops.get_unicode_property('alphabetic', 'binary')
        self.assertEqual(result, uniprops.unidata.unicode_binary['alphabetic'])

    def test_inverse_binary(self):
        """Test inverse binary Category."""

        result = uniprops.get_unicode_property('^alphabetic', 'binary')
        self.assertEqual(result, uniprops.unidata.unicode_binary['^alphabetic'])

    def test_binary_simple(self):
        """Test binary simple Category."""

        result = uniprops.get_unicode_property('alphabetic')
        self.assertEqual(result, uniprops.unidata.unicode_binary['alphabetic'])

    def test_inverse_binary_simple(self):
        """Test inverse binary simple Category."""

        result = uniprops.get_unicode_property('^alphabetic')
        self.assertEqual(result, uniprops.unidata.unicode_binary['^alphabetic'])

    def test_with_bad_category(self):
        """Test property with bad category."""

        with self.assertRaises(ValueError) as e:
            uniprops.get_unicode_property('^alphabetic', 'bad')

        self.assertTrue(str(e), 'Invalid Unicode property!')

    def test_bad_property_with_category(self):
        """Test bad property with category."""

        with self.assertRaises(ValueError) as e:
            uniprops.get_unicode_property('^bad', 'binary')

        self.assertTrue(str(e), 'Invalid Unicode property!')

    def test_bad_property(self):
        """Test bad property."""

        with self.assertRaises(ValueError) as e:
            uniprops.get_unicode_property('^bad')

        self.assertTrue(str(e), 'Invalid Unicode property!')

    def test_isbad_property(self):
        """Test isbad property."""

        with self.assertRaises(ValueError) as e:
            uniprops.get_unicode_property('^isbad')

        self.assertTrue(str(e), 'Invalid Unicode property!')

    def test_inbad_property(self):
        """Test isbad property."""

        with self.assertRaises(ValueError) as e:
            uniprops.get_unicode_property('^inbad')

        self.assertTrue(str(e), 'Invalid Unicode property!')

    def test_posix_binary(self):
        """Test binary posix Category."""

        result = uniprops.get_posix_property(b'punct')
        self.assertEqual(result, uniprops.unidata.bposix_properties['punct'])

    def test_inverse_posix_binary(self):
        """Test inverse binary posix Category."""

        result = uniprops.get_posix_property(b'^punct')
        self.assertEqual(result, uniprops.unidata.bposix_properties['^punct'])

    def test_posix(self):
        """Test posix Category."""

        result = uniprops.get_posix_property('punct')
        self.assertEqual(result, uniprops.unidata.posix_properties['punct'])

    def test_inverse_posix(self):
        """Test inverse posix Category."""

        result = uniprops.get_posix_property('^punct')
        self.assertEqual(result, uniprops.unidata.posix_properties['^punct'])

    def test_uposix(self):
        """Test unicode posix Category."""

        result = uniprops.get_posix_property('punct', uni=True)
        self.assertEqual(result, uniprops.unidata.unicode_binary['posixpunct'])

    def test_inverse_uposix(self):
        """Test inverse unicode posix Category."""

        result = uniprops.get_posix_property('^punct', uni=True)
        self.assertEqual(result, uniprops.unidata.unicode_binary['^posixpunct'])
