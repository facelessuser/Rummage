"""Tests for text_decode.py."""
from __future__ import unicode_literals
import unittest
from rummage.rummage.rumcore import text_decode
import codecs


class TestBom(unittest.TestCase):

    """Test BOM detection."""

    def test_utf8(self):
        """Test UTF8 BOM detection."""

        bom = text_decode.inspect_bom('tests/encodings/utf8_bom.txt')
        self.assertEqual(bom.encode, 'utf-8')
        self.assertEqual(bom.bom, codecs.BOM_UTF8)

    def test_utf16be(self):
        """Test UTF16BE BOM detection."""

        bom = text_decode.inspect_bom('tests/encodings/utf16_be_bom.txt')
        self.assertEqual(bom.encode, 'utf-16-be')
        self.assertEqual(bom.bom, codecs.BOM_UTF16_BE)

    def test_utf16le(self):
        """Test UTF16LE BOM detection."""

        bom = text_decode.inspect_bom('tests/encodings/utf16_le_bom.txt')
        self.assertEqual(bom.encode, 'utf-16-le')
        self.assertEqual(bom.bom, codecs.BOM_UTF16_LE)

    def test_utf32be(self):
        """Test UTF32BE BOM detection."""

        bom = text_decode.inspect_bom('tests/encodings/utf32_be_bom.txt')
        self.assertEqual(bom.encode, 'utf-32-be')
        self.assertEqual(bom.bom, codecs.BOM_UTF32_BE)

    def test_utf32le(self):
        """Test UTF32LE BOM detection."""

        bom = text_decode.inspect_bom('tests/encodings/utf32_le_bom.txt')
        self.assertEqual(bom.encode, 'utf-32-le')
        self.assertEqual(bom.bom, codecs.BOM_UTF32_LE)

    def test_no_bom(self):
        """Test that files with no BOM return as None."""

        bom = text_decode.inspect_bom('tests/encodings/utf8.txt')
        self.assertTrue(bom is None)


class TestValidateEncoding(unittest.TestCase):

    """Test Encoding validation."""

    def test_encoding_okay(self):
        """Test validation success."""

        with open('tests/encodings/utf32_be_bom.txt', 'rb') as f:
            self.assertTrue(text_decode.verify_encode(f, 'utf-32-be'))

    def test_encoding_block_limit_okay(self):
        """Test validation block limit success."""

        with open('tests/encodings/utf32_be_bom.txt', 'rb') as f:
            self.assertTrue(text_decode.verify_encode(f, 'utf-32-be', chunk_size=4))

    def test_encoding_fail(self):
        """Test validation fail."""

        with open('tests/encodings/utf32_be_bom.txt', 'rb') as f:
            self.assertFalse(text_decode.verify_encode(f, 'utf-32-le'))

    def test_encoding_block_limit_fail(self):
        """Test validation block limit fail."""

        with open('tests/encodings/utf32_be_bom.txt', 'rb') as f:
            self.assertFalse(text_decode.verify_encode(f, 'utf-32-le', chunk_size=4))
