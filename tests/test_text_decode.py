"""Tests for `text_decode.py`."""
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest
import mock
import shutil
import os
import textwrap
import codecs
from rummage.lib.rumcore import text_decode
from . import util


class _Encoding(unittest.TestCase):
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

    def inspect_bom(self, *parts, content=b''):
        """Inspect BOM."""

        self.mktemp(*parts, content=content)
        return text_decode.inspect_bom(self.norm(*parts))

    def verify_encode(self, *parts, content=b'', encoding=None, chunk_size=4096, result=False):
        """Verify encoding."""

        self.mktemp(*parts, content=content)
        with open(self.norm(*parts), 'rb') as f:
            print(f.read())
            f.seek(0)
            self.assertEqual(text_decode.verify_encode(f, encoding, chunk_size=chunk_size), result)

    def guess(self, *parts, content=b'', encoding=None, bom=None, options=None):
        """Guess."""

        self.mktemp(*parts, content=content)
        enc = text_decode.guess(self.norm(*parts), encoding_options=options)
        self.assertEqual(enc.encode, encoding)
        self.assertEqual(enc.bom, bom)

    def sguess(self, string, encoding=None, bom=None, options=None):
        """String guess."""

        enc = text_decode.sguess(string, encoding_options=options)
        self.assertEqual(enc.encode, encoding)
        self.assertEqual(enc.bom, bom)


class TestBom(_Encoding):
    """Test BOM detection."""

    def test_utf8(self):
        """Test `UTF8` BOM detection."""

        bom = self.inspect_bom('utf8_bom.txt', content='UTF8 file with BOM'.encode('utf-8-sig'))
        self.assertEqual(bom.encode, 'utf-8')
        self.assertEqual(bom.bom, codecs.BOM_UTF8)

    def test_utf16be(self):
        """Test `UTF16BE` BOM detection."""

        bom = self.inspect_bom(
            'utf16_be_bom.txt',
            content=codecs.BOM_UTF16_BE + 'UTF16BE file with BOM'.encode('utf-16-be')
        )
        self.assertEqual(bom.encode, 'utf-16-be')
        self.assertEqual(bom.bom, codecs.BOM_UTF16_BE)

    def test_utf16le(self):
        """Test `UTF16LE` BOM detection."""

        bom = self.inspect_bom(
            'utf16_le_bom.txt',
            content=codecs.BOM_UTF16_LE + 'UTF16LE file with BOM'.encode('utf-16-le')
        )
        self.assertEqual(bom.encode, 'utf-16-le')
        self.assertEqual(bom.bom, codecs.BOM_UTF16_LE)

    def test_utf32be(self):
        """Test `UTF32BE` BOM detection."""

        bom = self.inspect_bom(
            'utf32_be_bom.txt',
            content=codecs.BOM_UTF32_BE + 'UTF32BE file with BOM'.encode('utf-32-be')
        )
        self.assertEqual(bom.encode, 'utf-32-be')
        self.assertEqual(bom.bom, codecs.BOM_UTF32_BE)

    def test_utf32le(self):
        """Test `UTF32LE` BOM detection."""

        bom = self.inspect_bom(
            'utf32_le_bom.txt',
            content=codecs.BOM_UTF32_LE + 'UTF32LE file with BOM'.encode('utf-32-le')
        )
        self.assertEqual(bom.encode, 'utf-32-le')
        self.assertEqual(bom.bom, codecs.BOM_UTF32_LE)

    def test_10646_UC4_3412(self):
        """Test `10646_UC4_3412` BOM detection."""

        bom = self.inspect_bom('10646_UC4_3412.txt', content=b'\xfe\xff\x00\x00')
        self.assertEqual(bom.encode, 'bin')
        self.assertEqual(bom.bom, None)

    def test_10646_UC4_2143(self):
        """Test `10646_UC4_2143` BOM detection."""

        bom = self.inspect_bom('10646_UC4_2143.txt', content=b'\x00\x00\xff\xfe')
        self.assertEqual(bom.encode, 'bin')
        self.assertEqual(bom.bom, None)

    def test_no_bom(self):
        """Test that files with no BOM return as None."""

        bom = text_decode.inspect_bom('utf8.txt')
        self.assertTrue(bom is None)


class TestValidateEncoding(_Encoding):
    """Test Encoding validation."""

    def test_encoding_okay(self):
        """Test validation success."""

        self.verify_encode(
            'utf32_be_bom.txt',
            content=codecs.BOM_UTF32_BE + 'UTF32BE file with BOM'.encode('utf-32-be'),
            encoding='utf-32-be',
            result=True
        )

    def test_encoding_block_limit_okay(self):
        """Test validation block limit success."""

        self.verify_encode(
            'utf32_be_bom.txt',
            content=codecs.BOM_UTF32_BE + 'UTF32BE file with BOM'.encode('utf-32-be'),
            encoding='utf-32-be',
            chunk_size=4,
            result=True
        )

    def test_encoding_fail(self):
        """Test validation fail."""

        self.verify_encode(
            'utf32_be_bom.txt',
            content=codecs.BOM_UTF32_BE + 'UTF32BE file with BOM'.encode('utf-32-be'),
            encoding='utf-32-le',
            result=False
        )

    def test_encoding_block_limit_fail(self):
        """Test validation block limit fail."""

        self.verify_encode(
            'utf32_be_bom.txt',
            content=codecs.BOM_UTF32_BE + 'UTF32BE file with BOM'.encode('utf-32-be'),
            encoding='utf-32-le',
            chunk_size=4,
            result=False
        )


class TestPyEncodingGuess(_Encoding):
    """Test Python file encoding guess."""

    def test_html_guess(self):
        """Test HTML guess."""

        self.guess(
            'no_encode.html',
            encoding='ascii',
        )

        self.guess(
            'encode.html',
            content=self.dedent(
                '''
                <head>
                   <meta http-equiv="Content-Type" content="text/html;charset=ISO-8859-1">
                </head>
                <body>
                    html text
                </body>
                '''
            ).encode('ISO-8859-1'),
            encoding='ISO-8859-1',
        )

        self.guess(
            'bad_encode.html',
            content=self.dedent(
                '''
                <head>
                    <meta http-equiv="Content-Type" content="text/html;charset=bad">
                </head>
                <body>
                    html text
                </body>
                '''
            ).encode('ascii'),
            encoding='ascii',
        )

        self.guess(
            'xml_encode.xhtml',
            content=self.dedent(
                '''
                <?xml version="1.0" encoding="ISO-8859-1"?>
                <head>
                </head>
                <body>
                    html text
                </body>
                '''
            ).encode('ISO-8859-1'),
            encoding='ISO-8859-1',
        )

        self.guess(
            'bad_xml_encode.xhtml',
            content=self.dedent(
                '''
                <?xml version="1.0" encoding="bad"?>
                <head>
                </head>
                <body>
                    html text
                </body>
                '''
            ).encode('ascii'),
            encoding='ascii',
        )

    def test_xml_guess(self):
        """Test XML guess."""

        self.guess(
            'no_encode.xml',
            encoding='ascii'
        )

        self.guess(
            'encode.xml',
            content=self.dedent(
                '''
                <?xml version="1.0" encoding="ISO-8859-1"?>
                '''
            ).encode('ISO-8859-1'),
            encoding='ISO-8859-1'
        )

        self.guess(
            'bad_encode.xml',
            content=self.dedent(
                '''
                <?xml version="1.0" encoding="bad"?>
                '''
            ).encode('ascii'),
            encoding='ascii'
        )

        self.guess(
            'utf16_be.xml',
            content=self.dedent(
                '''
                <?xml version="1.0" encoding="utf-16-be"?>
                '''
            ).encode('utf-16-be'),
            encoding='utf-16-be'
        )

        self.guess(
            'utf16_le.xml',
            content=self.dedent(
                '''
                <?xml version="1.0" encoding="utf-16-le"?>
                '''
            ).encode('utf-16-le'),
            encoding='utf-16-le'
        )

        self.guess(
            'utf32_be.xml',
            content=self.dedent(
                '''
                <?xml version="1.0" encoding="utf-32-be"?>
                '''
            ).encode('utf-32-be'),
            encoding='utf-32-be'
        )

        self.guess(
            'utf32_le.xml',
            content=self.dedent(
                '''
                <?xml version="1.0" encoding="utf-32-le"?>
                '''
            ).encode('utf-32-le'),
            encoding='utf-32-le'
        )

        self.guess(
            'utf16_be_bad.xml',
            content=self.dedent(
                '''
                <?xml version="1.0" encoding="bad"?>
                '''
            ).encode('utf-16-be'),
            encoding='bin'
        )

    def test_binary_ext_guess(self):
        """Test XML guess."""

        self.guess(
            'binary.bin',
            encoding='bin'
        )

    def test_py_default_ascii_file(self):
        """Test default Python file."""

        # Python 3 default is `UTF-8`.
        self.guess(
            'ascii.py',
            content=self.dedent(
                '''
                """Python test file example without utf8 chars."""
                '''
            ).encode('ascii'),
            encoding='utf-8'
        )

    def test_py_with_encode_string(self):
        """Test Python file with encoding string."""

        self.guess(
            'encode_string.py',
            content=self.dedent(
                '''
                # -*- coding: utf-8 -*-
                """Python test file exámple with utf8 chars."""
                '''
            ).encode('utf-8'),
            encoding='utf-8'
        )

    def test_py_with_second_line_encode_string(self):
        """Test Python file with second line encoding string."""

        self.guess(
            'second_line_encode_string.py',
            content=self.dedent(
                '''
                #!/usr/bin/env python
                # -*- coding: utf-8 -*-
                """Python test file exámple with utf8 chars."""
                '''
            ).encode('utf-8'),
            encoding='utf-8'
        )

    def test_py_with_no_encode_string(self):
        """Test Python file with no encode string, but not the default encoding either."""

        self.guess(
            'no_encode_string.py',
            content=self.dedent(
                '''
                """Python test file exámple with utf8 chárs."""
                '''
            ).encode('cp1252'),
            encoding='bin'
        )

    def test_py_with_wrong_encode_string(self):
        """Test Python file with wrong encode string."""

        self.guess(
            'wrong_encode_string.py',
            content=self.dedent(
                '''
                # -*- coding: utf-32-le -*-
                """Python test file exámple with utf8 chárs."""
                '''
            ).encode('utf-8'),
            encoding='bin'
        )

    def test_py_with_bad_encode_string(self):
        """Test Python file with bad encode string."""

        # Should fallback to the default `UTF-8`
        self.guess(
            'bad_encoding.py',
            content=self.dedent(
                '''
                # -*- coding: utf-fake -*-
                """Python test file with bad encode string."""
                '''
            ).encode('cp1252'),
            encoding='utf-8'
        )


class TestSizeGuess(_Encoding):
    """Test Python file encoding based on special logic dependent on size."""

    def test_zero_size(self):
        """Test a file with zero size."""

        self.guess(
            'zero_size.txt',
            content=b'',
            encoding='ascii'
        )

    @mock.patch('rummage.lib.rumcore.text_decode.os.path.getsize')
    def test_too_big(self, mock_size):
        """Test a file size 30MB or greater."""

        # Force a fake hit on file being too big
        mock_size.return_value = text_decode.MAX_GUESS_SIZE
        self.guess(
            'utf8.txt',
            content=self.dedent(
                '''
                exámple
                '''
            ).encode('utf-8'),
            encoding='bin'
        )

    def test_too_small_ascii(self):
        """Test a small ASCII file."""

        self.guess(
            'ascii.txt',
            content=self.dedent(
                '''
                This is a plain ASCII file.
                '''
            ).encode('ascii'),
            encoding='ascii'
        )

    def test_too_small_utf8(self):
        """Test a small `UTF-8` file."""

        self.guess(
            'utf8.txt',
            content=self.dedent(
                '''
                exámple
                '''
            ).encode('utf-8'),
            encoding='utf-8'
        )


class TestChardetGuess(_Encoding):
    """
    Test guessing with `chardet`.

    Force small file detection to ensure picking an encoding early.
    """

    @mock.patch('rummage.lib.rumcore.text_decode._is_very_small')
    @mock.patch('rummage.lib.rumcore.text_decode.DetectEncoding')
    def test_confidence_pass_guess(self, mock_detect, mock_small):
        """Test result with an encoding with acceptable confidence."""

        instance = mock_detect.return_value
        instance.result = {"encoding": "utf-8", "confidence": 1.0}
        mock_small.return_value = False
        self.guess(
            'utf8.txt',
            content=self.dedent(
                '''
                exámple
                '''
            ).encode('utf-8'),
            encoding='utf-8'
        )

    @mock.patch('rummage.lib.rumcore.text_decode._is_very_small')
    @mock.patch('rummage.lib.rumcore.text_decode.CDetect')
    def test_confidence_pass_guess_chardet(self, mock_detect, mock_small):
        """Test result with an encoding with acceptable confidence."""

        instance = mock_detect.return_value
        instance.result = {"encoding": "utf-8", "confidence": 1.0}
        mock_small.return_value = False
        self.guess(
            'utf8.txt',
            content=self.dedent(
                '''
                exámple
                '''
            ).encode('utf-8'),
            encoding='utf-8',
            options={'chardet_mode': text_decode.CHARDET_PYTHON}
        )

    @mock.patch('rummage.lib.rumcore.text_decode._is_very_small')
    @mock.patch('rummage.lib.rumcore.text_decode.CCDetect')
    def test_confidence_pass_guess_cchardet(self, mock_detect, mock_small):
        """Test result with an encoding with acceptable confidence."""

        instance = mock_detect.return_value
        instance.result = {"encoding": "utf-8", "confidence": 1.0}
        mock_small.return_value = False
        self.guess(
            'utf8.txt',
            content=self.dedent(
                '''
                exámple
                '''
            ).encode('utf-8'),
            encoding='utf-8',
            options={'chardet_mode': text_decode.CHARDET_CLIB}
        )

    @mock.patch('rummage.lib.rumcore.text_decode._is_very_small')
    @mock.patch('rummage.lib.rumcore.text_decode.DetectEncoding')
    def test_confidence_fail_guess(self, mock_detect, mock_small):
        """Test result with an encoding with unacceptable confidence."""

        instance = mock_detect.return_value
        instance.result = {"encoding": "utf-8", "confidence": 0.4}
        mock_small.return_value = False
        self.guess(
            'utf8.txt',
            content=self.dedent(
                '''
                exámple
                '''
            ).encode('utf-8'),
            encoding='bin'
        )

    @mock.patch('rummage.lib.rumcore.text_decode._is_very_small')
    @mock.patch('rummage.lib.rumcore.text_decode.DetectEncoding')
    def test_none_encoding_guess(self, mock_detect, mock_small):
        """Test result with an encoding that is None confidence."""

        instance = mock_detect.return_value
        instance.result = {"encoding": None, "confidence": 0.4}
        mock_small.return_value = False
        self.guess(
            'utf8.txt',
            content=self.dedent(
                '''
                exámple
                '''
            ).encode('utf-8'),
            encoding='bin'
        )

    @mock.patch('rummage.lib.rumcore.text_decode._is_very_small')
    @mock.patch('rummage.lib.rumcore.text_decode.DetectEncoding')
    def test_none_guess(self, mock_detect, mock_small):
        """Test result with no encoding match."""

        instance = mock_detect.return_value
        instance.result = None
        mock_small.return_value = False
        self.guess(
            'utf8.txt',
            content=self.dedent(
                '''
                exámple
                '''
            ).encode('utf-8'),
            encoding='bin'
        )

    def test_binary_guess(self):
        """Test result with no encoding match."""

        self.guess(
            'binary.txt',
            content=b'This is a \x00\x00\x00binary test.\n',
            encoding='bin'
        )


class TestSizeSguess(_Encoding):
    """Test Python file encoding based on special logic dependent on size."""

    def test_zero_size(self):
        """Test a file with zero size."""

        self.sguess(
            b'',
            encoding='ascii'
        )

    @mock.patch('rummage.lib.rumcore.text_decode._is_very_large')
    def test_too_big(self, mock_size):
        """Test a file size 30MB or greater."""

        mock_size.return_value = True
        self.sguess(
            self.dedent(
                '''
                exámple
                '''
            ).encode('utf-8'),
            encoding='bin'
        )

    def test_too_small_ascii(self):
        """Test a small ASCII file."""

        self.sguess(
            self.dedent(
                '''
                This is a plain ASCII file.
                '''
            ).encode('ascii'),
            encoding='ascii'
        )

    def test_too_small_utf8(self):
        """Test a small `UTF-8` file."""

        self.sguess(
            self.dedent(
                '''
                exámple
                '''
            ).encode('utf-8'),
            encoding='utf-8'
        )


class TestChardetSguess(_Encoding):
    """
    Test guessing with `chardet`.

    Force small file detection to ensure picking an encoding early.
    """

    @mock.patch('rummage.lib.rumcore.text_decode._is_very_small')
    @mock.patch('rummage.lib.rumcore.text_decode.DetectEncoding')
    def test_confidence_pass_guess_default(self, mock_detect, mock_small):
        """Test result with an encoding with acceptable confidence with the default detector."""

        instance = mock_detect.return_value
        instance.result = {"encoding": "utf-8", "confidence": 1.0}
        mock_small.return_value = False
        self.sguess(
            self.dedent(
                '''
                exámple
                '''
            ).encode('utf-8'),
            encoding='utf-8'
        )

    @mock.patch('rummage.lib.rumcore.text_decode._is_very_small')
    @mock.patch('rummage.lib.rumcore.text_decode.CDetect')
    def test_confidence_pass_guess_chardet(self, mock_detect, mock_small):
        """Test result with an encoding with acceptable confidence with `chardet`."""

        instance = mock_detect.return_value
        instance.result = {"encoding": "utf-8", "confidence": 1.0}
        mock_small.return_value = False
        self.sguess(
            self.dedent(
                '''
                exámple
                '''
            ).encode('utf-8'),
            encoding='utf-8',
            options={'chardet_mode': text_decode.CHARDET_PYTHON}
        )

    @mock.patch('rummage.lib.rumcore.text_decode._is_very_small')
    @mock.patch('rummage.lib.rumcore.text_decode.CCDetect')
    def test_confidence_pass_guess_cchardet(self, mock_detect, mock_small):
        """Test result with an encoding with acceptable confidence with `cchardet`."""

        instance = mock_detect.return_value
        instance.result = {"encoding": "utf-8", "confidence": 1.0}
        mock_small.return_value = False
        self.sguess(
            self.dedent(
                '''
                exámple
                '''
            ).encode('utf-8'),
            encoding='utf-8',
            options={'chardet_mode': text_decode.CHARDET_CLIB}
        )

    @mock.patch('rummage.lib.rumcore.text_decode._is_very_small')
    @mock.patch('rummage.lib.rumcore.text_decode.DetectEncoding')
    def test_confidence_fail_guess(self, mock_detect, mock_small):
        """Test result with an encoding with unacceptable confidence."""

        instance = mock_detect.return_value
        instance.result = {"encoding": "utf-8", "confidence": 0.4}
        mock_small.return_value = False
        self.sguess(
            self.dedent(
                '''
                exámple
                '''
            ).encode('utf-8'),
            encoding='bin'
        )

    @mock.patch('rummage.lib.rumcore.text_decode._is_very_small')
    @mock.patch('rummage.lib.rumcore.text_decode.DetectEncoding')
    def test_none_encoding_guess(self, mock_detect, mock_small):
        """Test result with an encoding that is None confidence."""

        instance = mock_detect.return_value
        instance.result = {"encoding": None, "confidence": 0.4}
        mock_small.return_value = False
        self.sguess(
            self.dedent(
                '''
                exámple
                '''
            ).encode('utf-8'),
            encoding='bin'
        )

    @mock.patch('rummage.lib.rumcore.text_decode._is_very_small')
    @mock.patch('rummage.lib.rumcore.text_decode.DetectEncoding')
    def test_none_guess(self, mock_detect, mock_small):
        """Test result with no encoding match."""

        instance = mock_detect.return_value
        instance.result = None
        mock_small.return_value = False
        self.sguess(
            self.dedent(
                '''
                exámple
                '''
            ).encode('utf-8'),
            encoding='bin'
        )

    def test_binary_guess(self):
        """Test result with no encoding match."""

        self.sguess(
            b'This is a \x00\x00\x00binary test.\n',
            encoding='bin'
        )
