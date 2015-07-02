"""Tests for text_decode.py."""
from __future__ import unicode_literals
import unittest
from rummage.rummage.rumcore import text_decode
import codecs
import mock


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


class TestPyEncodingGuess(unittest.TestCase):

    """Test Python file encoding guess."""

    def test_py_default_ascii_file(self):
        """Test default Python file."""

        encoding = text_decode.guess('tests/encodings/ascii.py')
        self.assertEqual(encoding.encode, 'ascii')
        self.assertEqual(encoding.bom, None)

    def test_py_with_encode_string(self):
        """Test Python file with encoding string."""

        encoding = text_decode.guess('tests/encodings/encode_string.py')
        self.assertEqual(encoding.encode, 'utf-8')
        self.assertEqual(encoding.bom, None)

    def test_py_with_second_line_encode_string(self):
        """Test Python file with second line encoding string."""

        encoding = text_decode.guess('tests/encodings/second_line_encode_string.py')
        self.assertEqual(encoding.encode, 'utf-8')
        self.assertEqual(encoding.bom, None)

    def test_py_with_no_encode_string(self):
        """Test Python file with no encode string, but non ASCII encoding."""

        encoding = text_decode.guess('tests/encodings/no_encode_string.py')
        self.assertEqual(encoding.encode, 'bin')
        self.assertEqual(encoding.bom, None)

    def test_py_with_wrong_encode_string(self):
        """Test Python file with wrong encode string."""

        encoding = text_decode.guess('tests/encodings/wrong_encode_string.py')
        self.assertEqual(encoding.encode, 'bin')
        self.assertEqual(encoding.bom, None)

    def test_py_with_bad_encode_string(self):
        """Test Python file with bad encode string."""

        encoding = text_decode.guess('tests/encodings/bad_encoding.py')
        self.assertEqual(encoding.encode, 'ascii')
        self.assertEqual(encoding.bom, None)


class TestSizeGuess(unittest.TestCase):

    """Test Python file encoding based on special logic dependant on size."""

    def test_zero_size(self):
        """Test a file with zero size."""

        encoding = text_decode.guess('tests/encodings/zero_size.txt')
        self.assertEqual(encoding.encode, 'ascii')
        self.assertEqual(encoding.bom, None)


class TestChardetGuess(unittest.TestCase):

    """Test guessing with chardet."""

    @mock.patch('rummage.rummage.rumcore.text_decode.DetectEncoding')
    def test_confidence_pass_guess(self, mock_detect):
        """Test result with an encoding with acceptable confidence."""

        instance = mock_detect.return_value
        instance.close.return_value = {"encoding": "utf-8", "confidence": 1.0}
        encoding = text_decode.guess('tests/encodings/utf8.txt')
        self.assertEqual(encoding.encode, 'utf-8')
        self.assertEqual(encoding.bom, None)

    @mock.patch('rummage.rummage.rumcore.text_decode.DetectEncoding')
    def test_confidence_fail_guess(self, mock_detect):
        """Test result with an encoding with unacceptable confidence."""

        instance = mock_detect.return_value
        instance.close.return_value = {"encoding": "utf-8", "confidence": 0.4}
        encoding = text_decode.guess('tests/encodings/utf8.txt')
        self.assertEqual(encoding.encode, 'bin')
        self.assertEqual(encoding.bom, None)

    @mock.patch('rummage.rummage.rumcore.text_decode.DetectEncoding')
    def test_none_encoding_guess(self, mock_detect):
        """Test result with an encoding that is None confidence."""

        instance = mock_detect.return_value
        instance.close.return_value = {"encoding": None, "confidence": 0.4}
        encoding = text_decode.guess('tests/encodings/utf8.txt')
        self.assertEqual(encoding.encode, 'bin')
        self.assertEqual(encoding.bom, None)

    @mock.patch('rummage.rummage.rumcore.text_decode.DetectEncoding')
    def test_none_guess(self, mock_detect):
        """Test result with no encoding match."""

        instance = mock_detect.return_value
        instance.close.return_value = None
        encoding = text_decode.guess('tests/encodings/utf8.txt')
        self.assertEqual(encoding.encode, 'bin')
        self.assertEqual(encoding.bom, None)
