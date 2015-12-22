"""
Generate a unicode prop table for Python narrow and wide builds.

Narrow builds will stop at 0xffff.
"""
from __future__ import unicode_literals
import sys
import struct
import unicodedata
import codecs

__version__ = '2.0.0'

# Compatibility
PY3 = sys.version_info >= (3, 0) and sys.version_info[0:2] < (4, 0)
WIDE_RANGE = (0x0000, 0x10FFFF)
NARROW_RANGE = (0x0000, 0xFFFF)
if PY3:
    unichar = chr  # noqa
else:
    unichar = unichr  # noqa


narrow_unicode_blocks = [
    ("Basic Latin", (0x0000, 0x007F)),
    ("Latin-1 Supplement", (0x0080, 0x00FF)),
    ("Latin Extended-A", (0x0100, 0x017F)),
    ("Latin Extended-B", (0x0180, 0x024F)),
    ("IPA Extensions", (0x0250, 0x02AF)),
    ("Spacing Modifier Letters", (0x02B0, 0x02FF)),
    ("Combining Diacritical Marks", (0x0300, 0x036F)),
    ("Greek and Coptic", (0x0370, 0x03FF)),
    ("Cyrillic", (0x0400, 0x04FF)),
    ("Cyrillic Supplementary", (0x0500, 0x052F)),
    ("Armenian", (0x0530, 0x058F)),
    ("Hebrew", (0x0590, 0x05FF)),
    ("Arabic", (0x0600, 0x06FF)),
    ("Syriac", (0x0700, 0x074F)),
    ("Thaana", (0x0780, 0x07BF)),
    ("Devanagari", (0x0900, 0x097F)),
    ("Bengali", (0x0980, 0x09FF)),
    ("Gurmukhi", (0x0A00, 0x0A7F)),
    ("Gujarati", (0x0A80, 0x0AFF)),
    ("Oriya", (0x0B00, 0x0B7F)),
    ("Tamil", (0x0B80, 0x0BFF)),
    ("Telugu", (0x0C00, 0x0C7F)),
    ("Kannada", (0x0C80, 0x0CFF)),
    ("Malayalam", (0x0D00, 0x0D7F)),
    ("Sinhala", (0x0D80, 0x0DFF)),
    ("Thai", (0x0E00, 0x0E7F)),
    ("Lao", (0x0E80, 0x0EFF)),
    ("Tibetan", (0x0F00, 0x0FFF)),
    ("Myanmar", (0x1000, 0x109F)),
    ("Georgian", (0x10A0, 0x10FF)),
    ("Hangul Jamo", (0x1100, 0x11FF)),
    ("Ethiopic", (0x1200, 0x137F)),
    ("Cherokee", (0x13A0, 0x13FF)),
    ("Unified Canadian Aboriginal Syllabics", (0x1400, 0x167F)),
    ("Ogham", (0x1680, 0x169F)),
    ("Runic", (0x16A0, 0x16FF)),
    ("Tagalog", (0x1700, 0x171F)),
    ("Hanunoo", (0x1720, 0x173F)),
    ("Buhid", (0x1740, 0x175F)),
    ("Tagbanwa", (0x1760, 0x177F)),
    ("Khmer", (0x1780, 0x17FF)),
    ("Mongolian", (0x1800, 0x18AF)),
    ("Limbu", (0x1900, 0x194F)),
    ("Tai Le", (0x1950, 0x197F)),
    ("Khmer Symbols", (0x19E0, 0x19FF)),
    ("Phonetic Extensions", (0x1D00, 0x1D7F)),
    ("Latin Extended Additional", (0x1E00, 0x1EFF)),
    ("Greek Extended", (0x1F00, 0x1FFF)),
    ("General Punctuation", (0x2000, 0x206F)),
    ("Superscripts and Subscripts", (0x2070, 0x209F)),
    ("Currency Symbols", (0x20A0, 0x20CF)),
    ("Combining Diacritical Marks for Symbols", (0x20D0, 0x20FF)),
    ("Letterlike Symbols", (0x2100, 0x214F)),
    ("Number Forms", (0x2150, 0x218F)),
    ("Arrows", (0x2190, 0x21FF)),
    ("Mathematical Operators", (0x2200, 0x22FF)),
    ("Miscellaneous Technical", (0x2300, 0x23FF)),
    ("Control Pictures", (0x2400, 0x243F)),
    ("Optical Character Recognition", (0x2440, 0x245F)),
    ("Enclosed Alphanumerics", (0x2460, 0x24FF)),
    ("Box Drawing", (0x2500, 0x257F)),
    ("Block Elements", (0x2580, 0x259F)),
    ("Geometric Shapes", (0x25A0, 0x25FF)),
    ("Miscellaneous Symbols", (0x2600, 0x26FF)),
    ("Dingbats", (0x2700, 0x27BF)),
    ("Miscellaneous Mathematical Symbols-A", (0x27C0, 0x27EF)),
    ("Supplemental Arrows-A", (0x27F0, 0x27FF)),
    ("Braille Patterns", (0x2800, 0x28FF)),
    ("Supplemental Arrows-B", (0x2900, 0x297F)),
    ("Miscellaneous Mathematical Symbols-B", (0x2980, 0x29FF)),
    ("Supplemental Mathematical Operators", (0x2A00, 0x2AFF)),
    ("Miscellaneous Symbols and Arrows", (0x2B00, 0x2BFF)),
    ("CJK Radicals Supplement", (0x2E80, 0x2EFF)),
    ("Kangxi Radicals", (0x2F00, 0x2FDF)),
    ("Ideographic Description Characters", (0x2FF0, 0x2FFF)),
    ("CJK Symbols and Punctuation", (0x3000, 0x303F)),
    ("Hiragana", (0x3040, 0x309F)),
    ("Katakana", (0x30A0, 0x30FF)),
    ("Bopomofo", (0x3100, 0x312F)),
    ("Hangul Compatibility Jamo", (0x3130, 0x318F)),
    ("Kanbun", (0x3190, 0x319F)),
    ("Bopomofo Extended", (0x31A0, 0x31BF)),
    ("Katakana Phonetic Extensions", (0x31F0, 0x31FF)),
    ("Enclosed CJK Letters and Months", (0x3200, 0x32FF)),
    ("CJK Compatibility", (0x3300, 0x33FF)),
    ("CJK Unified Ideographs Extension A", (0x3400, 0x4DBF)),
    ("Yijing Hexagram Symbols", (0x4DC0, 0x4DFF)),
    ("CJK Unified Ideographs", (0x4E00, 0x9FFF)),
    ("Yi Syllables", (0xA000, 0xA48F)),
    ("Yi Radicals", (0xA490, 0xA4CF)),
    ("Hangul Syllables", (0xAC00, 0xD7AF)),
    ("High Surrogates", (0xD800, 0xDB7F)),
    ("High Private Use Surrogates", (0xDB80, 0xDBFF)),
    ("Low Surrogates", (0xDC00, 0xDFFF)),
    ("Private Use Area", (0xE000, 0xF8FF)),
    ("CJK Compatibility Ideographs", (0xF900, 0xFAFF)),
    ("Alphabetic Presentation Forms", (0xFB00, 0xFB4F)),
    ("Arabic Presentation Forms-A", (0xFB50, 0xFDFF)),
    ("Variation Selectors", (0xFE00, 0xFE0F)),
    ("Combining Half Marks", (0xFE20, 0xFE2F)),
    ("CJK Compatibility Forms", (0xFE30, 0xFE4F)),
    ("Small Form Variants", (0xFE50, 0xFE6F)),
    ("Arabic Presentation Forms-B", (0xFE70, 0xFEFF)),
    ("Halfwidth and Fullwidth Forms", (0xFF00, 0xFFEF)),
    ("Specials", (0xFFF0, 0xFFFF))
]

wide_unicode_blocks = [
    ("Linear B Syllabary", (0x10000, 0x1007F)),
    ("Linear B Ideograms", (0x10080, 0x100FF)),
    ("Aegean Numbers", (0x10100, 0x1013F)),
    ("Ancient Greek Numbers", (0x10140, 0x1018F)),
    ("Ancient Symbols", (0x10190, 0x101CF)),
    ("Phaistos Disc", (0x101D0, 0x101FF)),
    ("Lycian", (0x10280, 0x1029F)),
    ("Carian", (0x102A0, 0x102DF)),
    ("Coptic Epact Numbers", (0x102E0, 0x102FF)),
    ("Old Italic", (0x10300, 0x1032F)),
    ("Gothic", (0x10330, 0x1034F)),
    ("Old Permic", (0x10350, 0x1037F)),
    ("Ugaritic", (0x10380, 0x1039F)),
    ("Old Persian", (0x103A0, 0x103DF)),
    ("Deseret", (0x10400, 0x1044F)),
    ("Shavian", (0x10450, 0x1047F)),
    ("Osmanya", (0x10480, 0x104AF)),
    ("Elbasan", (0x10500, 0x1052F)),
    ("Caucasian Albanian", (0x10530, 0x1056F)),
    ("Linear A", (0x10600, 0x1077F)),
    ("Cypriot Syllabary", (0x10800, 0x1083F)),
    ("Imperial Aramaic", (0x10840, 0x1085F)),
    ("Palmyrene", (0x10860, 0x1087F)),
    ("Nabataean", (0x10880, 0x108AF)),
    ("Hatran", (0x108E0, 0x108FF)),
    ("Phoenician", (0x10900, 0x1091F)),
    ("Lydian", (0x10920, 0x1093F)),
    ("Meroitic Hieroglyphs", (0x10980, 0x1099F)),
    ("Meroitic Cursive", (0x109A0, 0x109FF)),
    ("Kharoshthi", (0x10A00, 0x10A5F)),
    ("Old South Arabian", (0x10A60, 0x10A7F)),
    ("Old North Arabian", (0x10A80, 0x10A9F)),
    ("Manichaean", (0x10AC0, 0x10AFF)),
    ("Avestan", (0x10B00, 0x10B3F)),
    ("Inscriptional Parthian", (0x10B40, 0x10B5F)),
    ("Inscriptional Pahlavi", (0x10B60, 0x10B7F)),
    ("Psalter Pahlavi", (0x10B80, 0x10BAF)),
    ("Old Turkic", (0x10C00, 0x10C4F)),
    ("Old Hungarian", (0x10C80, 0x10CFF)),
    ("Rumi Numeral Symbols", (0x10E60, 0x10E7F)),
    ("Brahmi", (0x11000, 0x1107F)),
    ("Kaithi", (0x11080, 0x110CF)),
    ("Sora Sompeng", (0x110D0, 0x110FF)),
    ("Chakma", (0x11100, 0x1114F)),
    ("Mahajani", (0x11150, 0x1117F)),
    ("Sharada", (0x11180, 0x111DF)),
    ("Sinhala Archaic Numbers", (0x111E0, 0x111FF)),
    ("Khojki", (0x11200, 0x1124F)),
    ("Multani", (0x11280, 0x112AF)),
    ("Khudawadi", (0x112B0, 0x112FF)),
    ("Grantha", (0x11300, 0x1137F)),
    ("Tirhuta", (0x11480, 0x114DF)),
    ("Siddham", (0x11580, 0x115FF)),
    ("Modi", (0x11600, 0x1165F)),
    ("Takri", (0x11680, 0x116CF)),
    ("Ahom", (0x11700, 0x1173F)),
    ("Warang Citi", (0x118A0, 0x118FF)),
    ("Pau Cin Hau", (0x11AC0, 0x11AFF)),
    ("Cuneiform", (0x12000, 0x123FF)),
    ("Cuneiform Numbers and Punctuation", (0x12400, 0x1247F)),
    ("Early Dynastic Cuneiform", (0x12480, 0x1254F)),
    ("Egyptian Hieroglyphs", (0x13000, 0x1342F)),
    ("Anatolian Hieroglyphs", (0x14400, 0x1467F)),
    ("Bamum Supplement", (0x16800, 0x16A3F)),
    ("Mro", (0x16A40, 0x16A6F)),
    ("Bassa Vah", (0x16AD0, 0x16AFF)),
    ("Pahawh Hmong", (0x16B00, 0x16B8F)),
    ("Miao", (0x16F00, 0x16F9F)),
    ("Kana Supplement", (0x1B000, 0x1B0FF)),
    ("Duployan", (0x1BC00, 0x1BC9F)),
    ("Shorthand Format Controls", (0x1BCA0, 0x1BCAF)),
    ("Byzantine Musical Symbols", (0x1D000, 0x1D0FF)),
    ("Musical Symbols", (0x1D100, 0x1D1FF)),
    ("Ancient Greek Musical Notation", (0x1D200, 0x1D24F)),
    ("Tai Xuan Jing Symbols", (0x1D300, 0x1D35F)),
    ("Counting Rod Numerals", (0x1D360, 0x1D37F)),
    ("Mathematical Alphanumeric Symbols", (0x1D400, 0x1D7FF)),
    ("Sutton SignWriting", (0x1D800, 0x1DAAF)),
    ("Mende Kikakui", (0x1E800, 0x1E8DF)),
    ("Arabic Mathematical Alphabetic Symbols", (0x1EE00, 0x1EEFF)),
    ("Mahjong Tiles", (0x1F000, 0x1F02F)),
    ("Domino Tiles", (0x1F030, 0x1F09F)),
    ("Playing Cards", (0x1F0A0, 0x1F0FF)),
    ("Enclosed Alphanumeric Supplement", (0x1F100, 0x1F1FF)),
    ("Enclosed Ideographic Supplement", (0x1F200, 0x1F2FF)),
    ("Miscellaneous Symbols and Pictographs", (0x1F300, 0x1F5FF)),
    ("Emoticons", (0x1F600, 0x1F64F)),
    ("Ornamental Dingbats", (0x1F650, 0x1F67F)),
    ("Transport and Map Symbols", (0x1F680, 0x1F6FF)),
    ("Alchemical Symbols", (0x1F700, 0x1F77F)),
    ("Geometric Shapes Extended", (0x1F780, 0x1F7FF)),
    ("Supplemental Arrows-C", (0x1F800, 0x1F8FF)),
    ("Supplemental Symbols and Pictographs", (0x1F900, 0x1F9FF)),
    ("CJK Unified Ideographs Extension B", (0x20000, 0x2A6DF)),
    ("CJK Unified Ideographs Extension C", (0x2A700, 0x2B73F)),
    ("CJK Unified Ideographs Extension D", (0x2B740, 0x2B81F)),
    ("CJK Unified Ideographs Extension E", (0x2B820, 0x2CEAF)),
    ("CJK Compatibility Ideographs Supplement", (0x2F800, 0x2FA1F)),
    ("Tags", (0xE0000, 0xE007F)),
    ("Variation Selectors Supplement", (0xE0100, 0xE01EF)),
    ("Supplementary Private Use Area-A", (0xF0000, 0xFFFFF)),
    ("Supplementary Private Use Area-B", (0x100000, 0x10FFFF))
]


def uchr(i):
    """Allow getting unicode character on narrow python builds."""

    try:
        return unichar(i)
    except ValueError:
        return struct.pack('i', i).decode('utf-32')


def uniformat(value):
    """Convert a unicode char."""

    # Escape #^-\]
    # We include # in case we are using (?x)
    if value in (0x23, 0x55, 0x5c, 0x5d):
        c = "\\u%04x\\u%04x" % (0x5c, value)
    elif value <= 0xFFFF:
        c = "\\u%04x" % value
    else:
        c = "\\U%08x" % value
    return c


def binaryformat(value):
    """Convert a binary value."""

    # Escape #^-\]
    # We include # in case we are using (?x)
    if value in (0x23, 0x55, 0x5c, 0x5d):
        c = "\\x%02x\\x%02x" % (0x5c, value)
    else:
        c = "\\x%02x" % value
    return c


def build_unicode_property_table(output):
    """Build and write out unicode property table."""

    with codecs.open(output, 'w', 'utf-8') as f:
        f.write(
            '"""Unicode Properties (autogen)."""\nfrom __future__ import unicode_literals\n'
            'import sys\n\n'
            'NARROW = sys.maxunicode == 0xFFFF\n\n'
        )

        gen_bposix(f)
        f.write('if not NARROW:\n')
        gen_properties(f)
        f.write('else:\n')
        gen_properties(f, narrow=True)


def gen_blocks(blocks, all_chars, f, narrow):
    """Generate Unicode blocks."""

    f.write('    unicode_blocks = {\n')
    max_unicode = 0xffff if narrow else 0x10FFFF

    for block in blocks:
        name = block[0].lower().replace(' ', '').replace('-', '').replace('_', '')
        f.write('        "%s": "%s-%s",\n' % (name, uniformat(block[1][0]), uniformat(block[1][1])))

    count = len(blocks) - 1
    i = 0
    for block in blocks:
        name = '^' + block[0].lower().replace(' ', '').replace('-', '').replace('_', '')
        char_range = block[1]
        inverse_range = []
        if char_range[0] > 0:
            inverse_range.append("%s-%s" % (uniformat(0), uniformat(char_range[0] - 1)))
        if char_range[1] < max_unicode:
            inverse_range.append("%s-%s" % (uniformat(char_range[1] + 1), uniformat(max_unicode)))
        f.write('        "%s": "%s"' % (name, ''.join(inverse_range)))
        if i == count:
            f.write('\n    }\n')
        else:
            f.write(',\n')
        i += 1


def gen_bposix(f):
    """Generate the binary posix table and write out to file."""

    all_chars = set([x for x in range(0, 0xff + 1)])
    posix_table = {}

    # Alnum: [a-zA-Z0-9]
    s2 = set([x for x in range(0x30, 0x39 + 1)])
    s2 |= set([x for x in range(0x41, 0x5a + 1)])
    s2 |= set([x for x in range(0x61, 0x7a + 1)])
    posix_table["alnum"] = list(s2)
    posix_table["^alnum"] = list(all_chars - s2)

    # Alpha: [a-zA-Z]
    s2 = set([x for x in range(0x41, 0x5a)])
    s2 |= set([x for x in range(0x61, 0x7a)])
    posix_table["alpha"] = list(s2)
    posix_table["^alpha"] = list(all_chars - s2)

    # ASCII: [\x00-\x7F]
    s2 = set([x for x in range(0, 0x7F + 1)])
    posix_table["ascii"] = list(s2)
    posix_table["^ascii"] = list(all_chars - s2)

    # Blank: [ \t]
    s2 = set([0x20, 0x09])
    posix_table["blank"] = list(s2)
    posix_table["^blank"] = list(all_chars - s2)

    # Cntrl: [\x00-\x1F\x7F]
    s2 = set([x for x in range(0, 0x1F + 1)] + [0x7F])
    posix_table["cntrl"] = list(s2)
    posix_table["^cntrl"] = list(all_chars - s2)

    # Digit: [0-9]
    s2 = set([x for x in range(0x30, 0x39 + 1)])
    posix_table["digit"] = list(s2)
    posix_table["^digit"] = list(all_chars - s2)

    # Graph: [\x21-\x7E]
    s2 = set([x for x in range(0x21, 0x7E + 1)])
    posix_table["graph"] = list(s2)
    posix_table["^graph"] = list(all_chars - s2)

    s2 = set([x for x in range(0x61, 0x7a + 1)])
    posix_table["lower"] = list(s2)
    posix_table["^lower"] = list(all_chars - s2)

    # Print: [\x20-\x7E]
    s2 = set([x for x in range(0x20, 0x7E + 1)])
    posix_table["print"] = list(s2)
    posix_table["^print"] = list(all_chars - s2)

    # Punct: [!\"\#$%&'()*+,\-./:;<=>?@\[\\\]^_`{|}~]
    s2 = set([x for x in range(0x21, 0x2f + 1)])
    s2 |= set([x for x in range(0x3a, 0x40 + 1)])
    s2 |= set([x for x in range(0x5b, 0x60 + 1)])
    s2 |= set([x for x in range(0x7b, 0x7e + 1)])
    posix_table["punct"] = list(s2)
    posix_table["^punct"] = list(all_chars - s2)

    # Space: [ \t\r\n\v\f]
    s2 = set([x for x in range(0x09, 0x0d + 1)] + [0x20])
    posix_table["space"] = list(s2)
    posix_table["^space"] = list(all_chars - s2)

    # Upper: [A-Z]
    s2 = set([x for x in range(0x41, 0x5a + 1)])
    posix_table["upper"] = list(s2)
    posix_table["^upper"] = list(all_chars - s2)

    # Word: [A-Za-z0-9_]
    s2 = set([x for x in range(0x30, 0x39 + 1)])
    s2 |= set([x for x in range(0x41, 0x5a + 1)])
    s2 |= set([x for x in range(0x61, 0x7a + 1)] + [0x5f])
    posix_table["word"] = list(s2)
    posix_table["^word"] = list(all_chars - s2)

    # XDigit: [A-Fa-f0-9]
    s2 = set([x for x in range(0x30, 0x39 + 1)])
    s2 |= set([x for x in range(0x41, 0x46 + 1)])
    s2 |= set([x for x in range(0x61, 0x66 + 1)])
    posix_table["xdigit"] = list(s2)
    posix_table["^xdigit"] = list(all_chars - s2)

    # Convert characters values to ranges
    for k1, v1 in posix_table.items():
        v1.sort()
        last = None
        first = None
        v2 = []
        for i in v1:
            if first is None:
                first = i
                last = i
            elif i == last + 1:
                last = i
            elif first is not None:
                if first == last:
                    v2.append(binaryformat(first))
                else:
                    v2.append("%s-%s" % (binaryformat(first), binaryformat(last)))
                first = i
                last = i
        if first is not None:
            if first == last:
                v2.append(binaryformat(first))
            else:
                v2.append("%s-%s" % (binaryformat(first), binaryformat(last)))
            first = None
            last = None
        posix_table[k1] = ''.join(v2)

    # Write out the unicode properties
    f.write('bposix_properties = {\n')
    count = len(posix_table) - 1
    i = 0
    for k1, v1 in sorted(posix_table.items()):
        f.write('    "%s": b"%s"' % (k1, v1))
        if i == count:
            f.write('\n}\n')
        else:
            f.write(',\n')
        i += 1


def gen_posix(all_chars, f):
    """Generate the posix table and write out to file."""

    posix_table = {}

    # Alnum: [a-zA-Z0-9]
    s2 = set([x for x in range(0x30, 0x39 + 1)])
    s2 |= set([x for x in range(0x41, 0x5a + 1)])
    s2 |= set([x for x in range(0x61, 0x7a + 1)])
    posix_table["alnum"] = list(s2)
    posix_table["^alnum"] = list(all_chars - s2)

    # Alpha: [a-zA-Z]
    s2 = set([x for x in range(0x41, 0x5a)])
    s2 |= set([x for x in range(0x61, 0x7a)])
    posix_table["alpha"] = list(s2)
    posix_table["^alpha"] = list(all_chars - s2)

    # ASCII: [\x00-\x7F]
    s2 = set([x for x in range(0, 0x7F + 1)])
    posix_table["ascii"] = list(s2)
    posix_table["^ascii"] = list(all_chars - s2)

    # Blank: [ \t]
    s2 = set([0x20, 0x09])
    posix_table["blank"] = list(s2)
    posix_table["^blank"] = list(all_chars - s2)

    # Cntrl: [\x00-\x1F\x7F]
    s2 = set([x for x in range(0, 0x1F + 1)] + [0x7F])
    posix_table["cntrl"] = list(s2)
    posix_table["^cntrl"] = list(all_chars - s2)

    # Digit: [0-9]
    s2 = set([x for x in range(0x30, 0x39 + 1)])
    posix_table["digit"] = list(s2)
    posix_table["^digit"] = list(all_chars - s2)

    # Graph: [\x21-\x7E]
    s2 = set([x for x in range(0x21, 0x7E + 1)])
    posix_table["graph"] = list(s2)
    posix_table["^graph"] = list(all_chars - s2)

    s2 = set([x for x in range(0x61, 0x7a + 1)])
    posix_table["lower"] = list(s2)
    posix_table["^lower"] = list(all_chars - s2)

    # Print: [\x20-\x7E]
    s2 = set([x for x in range(0x20, 0x7E + 1)])
    posix_table["print"] = list(s2)
    posix_table["^print"] = list(all_chars - s2)

    # Punct: [!\"\#$%&'()*+,\-./:;<=>?@\[\\\]^_`{|}~]
    s2 = set([x for x in range(0x21, 0x2f + 1)])
    s2 |= set([x for x in range(0x3a, 0x40 + 1)])
    s2 |= set([x for x in range(0x5b, 0x60 + 1)])
    s2 |= set([x for x in range(0x7b, 0x7e + 1)])
    posix_table["punct"] = list(s2)
    posix_table["^punct"] = list(all_chars - s2)

    # Space: [ \t\r\n\v\f]
    s2 = set([x for x in range(0x09, 0x0d + 1)] + [0x20])
    posix_table["space"] = list(s2)
    posix_table["^space"] = list(all_chars - s2)

    # Upper: [A-Z]
    s2 = set([x for x in range(0x41, 0x5a + 1)])
    posix_table["upper"] = list(s2)
    posix_table["^upper"] = list(all_chars - s2)

    # Word: [A-Za-z0-9_]
    s2 = set([x for x in range(0x30, 0x39 + 1)])
    s2 |= set([x for x in range(0x41, 0x5a + 1)])
    s2 |= set([x for x in range(0x61, 0x7a + 1)] + [0x5f])
    posix_table["word"] = list(s2)
    posix_table["^word"] = list(all_chars - s2)

    # XDigit: [A-Fa-f0-9]
    s2 = set([x for x in range(0x30, 0x39 + 1)])
    s2 |= set([x for x in range(0x41, 0x46 + 1)])
    s2 |= set([x for x in range(0x61, 0x66 + 1)])
    posix_table["xdigit"] = list(s2)
    posix_table["^xdigit"] = list(all_chars - s2)

    # Convert characters values to ranges
    for k1, v1 in posix_table.items():
        v1.sort()
        last = None
        first = None
        v2 = []
        for i in v1:
            if first is None:
                first = i
                last = i
            elif i == last + 1:
                last = i
            elif first is not None:
                if first == last:
                    v2.append(uniformat(first))
                else:
                    v2.append("%s-%s" % (uniformat(first), uniformat(last)))
                first = i
                last = i
        if first is not None:
            if first == last:
                v2.append(uniformat(first))
            else:
                v2.append("%s-%s" % (uniformat(first), uniformat(last)))
            first = None
            last = None
        posix_table[k1] = ''.join(v2)

    # Write out the unicode properties
    f.write('    posix_properties = {\n')
    count = len(posix_table) - 1
    i = 0
    for k1, v1 in sorted(posix_table.items()):
        f.write('        "%s": "%s"' % (k1, v1))
        if i == count:
            f.write('\n    }\n')
        else:
            f.write(',\n')
        i += 1


def gen_unicode_posix(table, all_chars, f):
    """Generate the posix table and write out to file."""

    posix_table = {}

    # Alnum: [\p{L&}\p{Nd}]
    s2 = set(table['l']['c'] + table['n']['d'])
    posix_table["alnum"] = list(s2)
    posix_table["^alnum"] = list(all_chars - s2)

    # Alpha: [\p{L&}]
    s2 = set(table['l']['c'])
    posix_table["alpha"] = list(s2)
    posix_table["^alpha"] = list(all_chars - s2)

    # ASCII: [\x00-\x7F]
    s2 = set([x for x in range(0, 0x7F + 1)])
    posix_table["ascii"] = list(s2)
    posix_table["^ascii"] = list(all_chars - s2)

    # Blank: [\p{Zs}\t]
    s2 = set(table['z']['s'] + [0x09])
    posix_table["blank"] = list(s2)
    posix_table["^blank"] = list(all_chars - s2)

    # Cntrl: [\p{Cc}]
    s2 = set(table['c']['c'])
    posix_table["cntrl"] = list(s2)
    posix_table["^cntrl"] = list(all_chars - s2)

    # Digit: [\p{Nd}]
    s2 = set(table['n']['d'])
    posix_table["digit"] = list(s2)
    posix_table["^digit"] = list(all_chars - s2)

    # Graph: [^\p{Z}\p{C}]
    s2 = set()
    for table_name in ('z', 'c'):
        for sub_table_name in table[table_name]:
            if not sub_table_name.startswith('^'):
                s2 |= set(table[table_name][sub_table_name])
    posix_table["graph"] = list(all_chars - s2)
    posix_table["^graph"] = list(s2)

    # Lower: [\p{Ll}]
    s2 = set(table['l']['l'])
    posix_table["lower"] = list(s2)
    posix_table["^lower"] = list(all_chars - s2)

    # Print: [\P{C}]
    s2 = set()
    for table_name in ('c',):
        for sub_table_name in table[table_name]:
            if not sub_table_name.startswith('^'):
                s2 |= set(table[table_name][sub_table_name])
    posix_table["print"] = list(all_chars - s2)
    posix_table["^print"] = list(s2)

    # Punct: [\p{P}\p{S}]
    s2 = set()
    for table_name in ('p', 's'):
        for sub_table_name in table[table_name]:
            if not sub_table_name.startswith('^'):
                s2 |= set(table[table_name][sub_table_name])
    posix_table["punct"] = list(s2)
    posix_table["^punct"] = list(all_chars - s2)

    # Space: [\p{Z}\t\r\n\v\f]
    s2 = set()
    for table_name in ('z',):
        for sub_table_name in table[table_name]:
            if not sub_table_name.startswith('^'):
                s2 |= set(table[table_name][sub_table_name])
    s2 |= set([x for x in range(0x09, 0x0e)])
    posix_table["space"] = list(s2)
    posix_table["^space"] = list(all_chars - s2)

    # Upper: [\p{Lu}]
    s2 = set(table['l']['u'])
    posix_table["upper"] = list(s2)
    posix_table["^upper"] = list(all_chars - s2)

    # Word: [\p{L}\p{N}\p{Pc}]
    s2 = set()
    for table_name in ('l', 'n'):
        for sub_table_name in table[table_name]:
            if not sub_table_name.startswith('^'):
                s2 |= set(table[table_name][sub_table_name])
    s2 |= set(table['p']['c'])
    posix_table["word"] = list(s2)
    posix_table["^word"] = list(all_chars - s2)

    # XDigit: [A-Fa-f0-9]
    s2 = set([x for x in range(0x30, 0x39 + 1)])
    s2 |= set([x for x in range(0x41, 0x46 + 1)])
    s2 |= set([x for x in range(0x61, 0x66 + 1)])
    posix_table["xdigit"] = list(s2)
    posix_table["^xdigit"] = list(all_chars - s2)

    # Convert characters values to ranges
    for k1, v1 in posix_table.items():
        v1.sort()
        last = None
        first = None
        v2 = []
        for i in v1:
            if first is None:
                first = i
                last = i
            elif i == last + 1:
                last = i
            elif first is not None:
                if first == last:
                    v2.append(uniformat(first))
                else:
                    v2.append("%s-%s" % (uniformat(first), uniformat(last)))
                first = i
                last = i
        if first is not None:
            if first == last:
                v2.append(uniformat(first))
            else:
                v2.append("%s-%s" % (uniformat(first), uniformat(last)))
            first = None
            last = None
        posix_table[k1] = ''.join(v2)

    # Write out the unicode properties
    f.write('    posix_unicode_properties = {\n')
    count = len(posix_table) - 1
    i = 0
    for k1, v1 in sorted(posix_table.items()):
        f.write('        "%s": "%s"' % (k1, v1))
        if i == count:
            f.write('\n    }\n')
        else:
            f.write(',\n')
        i += 1


def gen_properties(f, narrow=False):
    """Generate the property table and dump it to the provided file."""

    if not narrow:
        unicode_range = WIDE_RANGE
    else:
        unicode_range = NARROW_RANGE

    # L& or Lc won't be found in the table,
    # so intialize 'c' at the start. & will have to be converted to 'c'
    # before sending it through.
    table = {'l': {'c': [], '^c': []}}
    all_chars = set()
    p = None
    for i in range(unicode_range[0], unicode_range[1] + 1):
        all_chars.add(i)
        c = uchr(i)
        p = [x.lower() for x in unicodedata.category(c)]

        if p[0] not in table:
            table[p[0]] = {}
        if p[1] not in table[p[0]]:
            table[p[0]][p[1]] = []
            table[p[0]]['^' + p[1]] = []
        table[p[0]][p[1]].append(i)
        # Add L& which is a combo of Ll, Lu, and Lt
        if p[0] == 'l' and p[1] in ('l', 'u', 't'):
            table['l']['c'].append(i)

    # Create inverse of each category
    for k1, v1 in table.items():
        inverse_category = set()
        for k2, v2 in v1.items():
            if not k2.startswith('^'):
                s2 = set(v2)
                inverse_category |= s2
                table[k1]['^' + k2] = list(all_chars - s2)
        table[k1]['^'] = list(all_chars - inverse_category)

    # Generate Unicode blocks
    gen_blocks(
        (narrow_unicode_blocks if narrow else (narrow_unicode_blocks + wide_unicode_blocks)),
        all_chars, f,
        narrow
    )

    # Generate posix table and write out to file.
    gen_posix(all_chars, f)
    gen_unicode_posix(table, all_chars, f)

    # Convert characters values to ranges
    for k1, v1 in table.items():
        for k2, v2 in v1.items():
            v2.sort()
            last = None
            first = None
            v3 = []
            for i in v2:
                if first is None:
                    first = i
                    last = i
                elif i == last + 1:
                    last = i
                elif first is not None:
                    if first == last:
                        v3.append(uniformat(first))
                    else:
                        v3.append("%s-%s" % (uniformat(first), uniformat(last)))
                    first = i
                    last = i
            if first is not None:
                if first == last:
                    v3.append(uniformat(first))
                else:
                    v3.append("%s-%s" % (uniformat(first), uniformat(last)))
                first = None
                last = None
            table[k1][k2] = ''.join(v3)

    # Write out the unicode properties
    f.write('    unicode_properties = {\n')
    count = len(table) - 1
    i = 0
    for k1, v1 in sorted(table.items()):
        f.write('        "%s": {\n' % k1)
        count2 = len(v1) - 1
        j = 0
        for k2, v2 in sorted(v1.items()):
            f.write('            "%s": "%s"' % (k2, v2))
            if j == count2:
                f.write('\n        }')
            else:
                f.write(',\n')
            j += 1
        if i == count:
            f.write('\n    }\n')
        else:
            f.write(',\n')
        i += 1


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(prog='unipropgen', description='Generate a unicode property table.')
    parser.add_argument('--version', action='version', version="%(prog)s " + __version__)
    parser.add_argument('output', default=None, help='Output file.')
    args = parser.parse_args()

    build_unicode_property_table(args.output)
