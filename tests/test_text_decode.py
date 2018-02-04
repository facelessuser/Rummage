"""Tests for text_decode.py."""
from __future__ import unicode_literals
import unittest
import mock
import codecs
from rummage.lib.rumcore import text_decode


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

    def test_10646_UC4_3412(self):
        """Test 10646_UC4_3412 BOM detection."""

        bom = text_decode.inspect_bom('tests/encodings/10646_UC4_3412.txt')
        self.assertEqual(bom.encode, 'bin')
        self.assertEqual(bom.bom, None)

    def test_10646_UC4_2143(self):
        """Test 10646_UC4_2143 BOM detection."""

        bom = text_decode.inspect_bom('tests/encodings/10646_UC4_2143.txt')
        self.assertEqual(bom.encode, 'bin')
        self.assertEqual(bom.bom, None)

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

    def test_html_guess(self):
        """Test HTML guess."""

        encoding = text_decode.guess('tests/encodings/no_encode.html')
        self.assertEqual(encoding.encode, 'ascii')
        self.assertEqual(encoding.bom, None)

        encoding = text_decode.guess('tests/encodings/encode.html')
        self.assertEqual(encoding.encode, 'ISO-8859-1')
        self.assertEqual(encoding.bom, None)

        encoding = text_decode.guess('tests/encodings/bad_encode.html')
        self.assertEqual(encoding.encode, 'ascii')
        self.assertEqual(encoding.bom, None)

        encoding = text_decode.guess('tests/encodings/xml_encode.xhtml')
        self.assertEqual(encoding.encode, 'ISO-8859-1')
        self.assertEqual(encoding.bom, None)

        encoding = text_decode.guess('tests/encodings/bad_xml_encode.xhtml')
        self.assertEqual(encoding.encode, 'ascii')
        self.assertEqual(encoding.bom, None)

    def test_xml_guess(self):
        """Test XML guess."""

        encoding = text_decode.guess('tests/encodings/no_encode.xml')
        self.assertEqual(encoding.encode, 'ascii')
        self.assertEqual(encoding.bom, None)

        encoding = text_decode.guess('tests/encodings/encode.xml')
        self.assertEqual(encoding.encode, 'ISO-8859-1')
        self.assertEqual(encoding.bom, None)

        encoding = text_decode.guess('tests/encodings/bad_encode.xml')
        self.assertEqual(encoding.encode, 'ascii')
        self.assertEqual(encoding.bom, None)

        encoding = text_decode.guess('tests/encodings/utf16_be.xml')
        self.assertEqual(encoding.encode, 'utf-16-be')
        self.assertEqual(encoding.bom, None)

        encoding = text_decode.guess('tests/encodings/utf16_le.xml')
        self.assertEqual(encoding.encode, 'utf-16-le')
        self.assertEqual(encoding.bom, None)

        encoding = text_decode.guess('tests/encodings/utf32_be.xml')
        self.assertEqual(encoding.encode, 'utf-32-be')
        self.assertEqual(encoding.bom, None)

        encoding = text_decode.guess('tests/encodings/utf32_le.xml')
        self.assertEqual(encoding.encode, 'utf-32-le')
        self.assertEqual(encoding.bom, None)

        encoding = text_decode.guess('tests/encodings/utf16_be_bad.xml')
        self.assertEqual(encoding.encode, 'bin')
        self.assertEqual(encoding.bom, None)

    def test_binary_ext_guess(self):
        """Test XML guess."""

        encoding = text_decode.guess('tests/encodings/binary.bin')
        self.assertEqual(encoding.encode, 'bin')
        self.assertEqual(encoding.bom, None)

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


class TestSizeSguess(unittest.TestCase):
    """Test Python file encoding based on special logic dependant on size."""

    def test_zero_size(self):
        """Test a file with zero size."""

        with open('tests/encodings/zero_size.txt', 'rb') as f:
            string = f.read()
        encoding = text_decode.sguess(string)
        self.assertEqual(encoding.encode, 'ascii')
        self.assertEqual(encoding.bom, None)

    @mock.patch('rummage.lib.rumcore.text_decode._is_very_large')
    def test_too_big(self, mock_size):
        """Test a file size 30MB or greater."""

        mock_size.return_value = True
        with open('tests/encodings/utf8.txt', 'rb') as f:
            string = f.read()
        encoding = text_decode.sguess(string)
        self.assertEqual(encoding.encode, 'bin')
        self.assertEqual(encoding.bom, None)

    def test_too_small_ascii(self):
        """Test a small ascii file."""

        with open('tests/encodings/ascii.txt', 'rb') as f:
            string = f.read()
        encoding = text_decode.sguess(string)
        self.assertEqual(encoding.encode, 'ascii')
        self.assertEqual(encoding.bom, None)

    def test_too_small_utf8(self):
        """Test a small utf-8 file."""

        with open('tests/encodings/utf8.txt', 'rb') as f:
            string = f.read()
        encoding = text_decode.sguess(string)
        self.assertEqual(encoding.encode, 'utf-8')
        self.assertEqual(encoding.bom, None)


class TestSizeGuess(unittest.TestCase):
    """Test Python file encoding based on special logic dependant on size."""

    def test_zero_size(self):
        """Test a file with zero size."""

        encoding = text_decode.guess('tests/encodings/zero_size.txt')
        self.assertEqual(encoding.encode, 'ascii')
        self.assertEqual(encoding.bom, None)

    @mock.patch('rummage.lib.rumcore.text_decode.os.path.getsize')
    def test_too_big(self, mock_size):
        """Test a file size 30MB or greater."""

        mock_size.return_value = text_decode.MAX_GUESS_SIZE
        encoding = text_decode.guess('tests/encodings/utf8.txt')
        self.assertEqual(encoding.encode, 'bin')
        self.assertEqual(encoding.bom, None)

    def test_too_small_ascii(self):
        """Test a small ascii file."""

        encoding = text_decode.guess('tests/encodings/ascii.txt')
        self.assertEqual(encoding.encode, 'ascii')
        self.assertEqual(encoding.bom, None)

    def test_too_small_utf8(self):
        """Test a small utf-8 file."""

        encoding = text_decode.guess('tests/encodings/utf8.txt')
        self.assertEqual(encoding.encode, 'utf-8')
        self.assertEqual(encoding.bom, None)


class TestChardetSguess(unittest.TestCase):
    """
    Test guessing with chardet.

    Force small file detection to ensure picking an encoding early.
    """

    @mock.patch('rummage.lib.rumcore.text_decode._is_very_small')
    @mock.patch('rummage.lib.rumcore.text_decode.DetectEncoding')
    def test_confidence_pass_guess_default(self, mock_detect, mock_small):
        """Test result with an encoding with acceptable confidence with the default detector."""

        instance = mock_detect.return_value
        instance.result = {"encoding": "utf-8", "confidence": 1.0}
        mock_small.return_value = False
        with open('tests/encodings/utf8.txt', 'rb') as f:
            string = f.read()
        encoding = text_decode.sguess(string)
        self.assertEqual(encoding.encode, 'utf-8')
        self.assertEqual(encoding.bom, None)

    @mock.patch('rummage.lib.rumcore.text_decode._is_very_small')
    @mock.patch('rummage.lib.rumcore.text_decode.CDetect')
    def test_confidence_pass_guess_chardet(self, mock_detect, mock_small):
        """Test result with an encoding with acceptable confidence with chardet."""

        instance = mock_detect.return_value
        instance.result = {"encoding": "utf-8", "confidence": 1.0}
        mock_small.return_value = False
        with open('tests/encodings/utf8.txt', 'rb') as f:
            string = f.read()
        encoding = text_decode.sguess(string, encoding_options={'chardet_mode': text_decode.CHARDET_PYTHON})
        self.assertEqual(encoding.encode, 'utf-8')
        self.assertEqual(encoding.bom, None)

    @mock.patch('rummage.lib.rumcore.text_decode._is_very_small')
    @mock.patch('rummage.lib.rumcore.text_decode.CCDetect')
    def test_confidence_pass_guess_cchardet(self, mock_detect, mock_small):
        """Test result with an encoding with acceptable confidence with cchardet."""

        instance = mock_detect.return_value
        instance.result = {"encoding": "utf-8", "confidence": 1.0}
        mock_small.return_value = False
        with open('tests/encodings/utf8.txt', 'rb') as f:
            string = f.read()
        encoding = text_decode.sguess(string, encoding_options={'chardet_mode': text_decode.CHARDET_CLIB})
        self.assertEqual(encoding.encode, 'utf-8')
        self.assertEqual(encoding.bom, None)

    @mock.patch('rummage.lib.rumcore.text_decode._is_very_small')
    @mock.patch('rummage.lib.rumcore.text_decode.DetectEncoding')
    def test_confidence_fail_guess(self, mock_detect, mock_small):
        """Test result with an encoding with unacceptable confidence."""

        instance = mock_detect.return_value
        instance.result = {"encoding": "utf-8", "confidence": 0.4}
        mock_small.return_value = False
        with open('tests/encodings/utf8.txt', 'rb') as f:
            string = f.read()
        encoding = text_decode.sguess(string)
        self.assertEqual(encoding.encode, 'bin')
        self.assertEqual(encoding.bom, None)

    @mock.patch('rummage.lib.rumcore.text_decode._is_very_small')
    @mock.patch('rummage.lib.rumcore.text_decode.DetectEncoding')
    def test_none_encoding_guess(self, mock_detect, mock_small):
        """Test result with an encoding that is None confidence."""

        instance = mock_detect.return_value
        instance.result = {"encoding": None, "confidence": 0.4}
        mock_small.return_value = False
        with open('tests/encodings/utf8.txt', 'rb') as f:
            string = f.read()
        encoding = text_decode.sguess(string)
        self.assertEqual(encoding.encode, 'bin')
        self.assertEqual(encoding.bom, None)

    @mock.patch('rummage.lib.rumcore.text_decode._is_very_small')
    @mock.patch('rummage.lib.rumcore.text_decode.DetectEncoding')
    def test_none_guess(self, mock_detect, mock_small):
        """Test result with no encoding match."""

        instance = mock_detect.return_value
        instance.result = None
        mock_small.return_value = False
        with open('tests/encodings/utf8.txt', 'rb') as f:
            string = f.read()
        encoding = text_decode.sguess(string)
        self.assertEqual(encoding.encode, 'bin')
        self.assertEqual(encoding.bom, None)

    def test_binary_guess(self):
        """Test result with no encoding match."""

        with open('tests/encodings/binary.txt', 'rb') as f:
            string = f.read()
        encoding = text_decode.sguess(string)
        self.assertEqual(encoding.encode, 'bin')
        self.assertEqual(encoding.bom, None)


class TestChardetGuess(unittest.TestCase):
    """
    Test guessing with chardet.

    Force small file detection to ensure picking an encoding early.
    """

    @mock.patch('rummage.lib.rumcore.text_decode._is_very_small')
    @mock.patch('rummage.lib.rumcore.text_decode.DetectEncoding')
    def test_confidence_pass_guess(self, mock_detect, mock_small):
        """Test result with an encoding with acceptable confidence."""

        instance = mock_detect.return_value
        instance.result = {"encoding": "utf-8", "confidence": 1.0}
        mock_small.return_value = False
        encoding = text_decode.guess('tests/encodings/utf8.txt')
        self.assertEqual(encoding.encode, 'utf-8')
        self.assertEqual(encoding.bom, None)

    @mock.patch('rummage.lib.rumcore.text_decode._is_very_small')
    @mock.patch('rummage.lib.rumcore.text_decode.CDetect')
    def test_confidence_pass_guess_chardet(self, mock_detect, mock_small):
        """Test result with an encoding with acceptable confidence."""

        instance = mock_detect.return_value
        instance.result = {"encoding": "utf-8", "confidence": 1.0}
        mock_small.return_value = False
        encoding = text_decode.guess(
            'tests/encodings/utf8.txt', encoding_options={'chardet_mode': text_decode.CHARDET_PYTHON}
        )
        self.assertEqual(encoding.encode, 'utf-8')
        self.assertEqual(encoding.bom, None)

    @mock.patch('rummage.lib.rumcore.text_decode._is_very_small')
    @mock.patch('rummage.lib.rumcore.text_decode.CCDetect')
    def test_confidence_pass_guess_cchardet(self, mock_detect, mock_small):
        """Test result with an encoding with acceptable confidence."""

        instance = mock_detect.return_value
        instance.result = {"encoding": "utf-8", "confidence": 1.0}
        mock_small.return_value = False
        encoding = text_decode.guess(
            'tests/encodings/utf8.txt', encoding_options={'chardet_mode': text_decode.CHARDET_CLIB}
        )
        self.assertEqual(encoding.encode, 'utf-8')
        self.assertEqual(encoding.bom, None)

    @mock.patch('rummage.lib.rumcore.text_decode._is_very_small')
    @mock.patch('rummage.lib.rumcore.text_decode.DetectEncoding')
    def test_confidence_fail_guess(self, mock_detect, mock_small):
        """Test result with an encoding with unacceptable confidence."""

        instance = mock_detect.return_value
        instance.result = {"encoding": "utf-8", "confidence": 0.4}
        mock_small.return_value = False
        encoding = text_decode.guess('tests/encodings/utf8.txt')
        self.assertEqual(encoding.encode, 'bin')
        self.assertEqual(encoding.bom, None)

    @mock.patch('rummage.lib.rumcore.text_decode._is_very_small')
    @mock.patch('rummage.lib.rumcore.text_decode.DetectEncoding')
    def test_none_encoding_guess(self, mock_detect, mock_small):
        """Test result with an encoding that is None confidence."""

        instance = mock_detect.return_value
        instance.result = {"encoding": None, "confidence": 0.4}
        mock_small.return_value = False
        encoding = text_decode.guess('tests/encodings/utf8.txt')
        self.assertEqual(encoding.encode, 'bin')
        self.assertEqual(encoding.bom, None)

    @mock.patch('rummage.lib.rumcore.text_decode._is_very_small')
    @mock.patch('rummage.lib.rumcore.text_decode.DetectEncoding')
    def test_none_guess(self, mock_detect, mock_small):
        """Test result with no encoding match."""

        instance = mock_detect.return_value
        instance.result = None
        mock_small.return_value = False
        encoding = text_decode.guess('tests/encodings/utf8.txt')
        self.assertEqual(encoding.encode, 'bin')
        self.assertEqual(encoding.bom, None)

    def test_binary_guess(self):
        """Test result with no encoding match."""

        encoding = text_decode.guess('tests/encodings/binary.txt')
        self.assertEqual(encoding.encode, 'bin')
        self.assertEqual(encoding.bom, None)
