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
