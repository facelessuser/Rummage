"""
Generate a unicode prop table for Python narrow and wide builds.

Narrow builds will stop at 0xffff.
"""
from __future__ import unicode_literals
import sys
import struct
import unicodedata
import codecs
import os

__version__ = '2.0.0'

UNIVERSION = unicodedata.unidata_version
HOME = os.path.dirname(os.path.abspath(__file__))
NARROW = sys.maxunicode == 0xFFFF

# Compatibility
PY3 = sys.version_info >= (3, 0) and sys.version_info[0:2] < (4, 0)
if NARROW:
    UNICODE_RANGE = (0x0000, 0xFFFF)
else:
    UNICODE_RANGE = (0x0000, 0x10FFFF)
if PY3:
    unichar = chr  # noqa
else:
    unichar = unichr  # noqa


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

        gen_posix(set([x for x in range(0, 0xff + 1)]), f, binary=True)
        gen_properties(f)


def char2range(d, double=False, binary=False):
    """Convert the characters in the dict to a range in string form."""

    fmt = binaryformat if binary else uniformat

    if double:
        # Convert characters values to ranges
        for k1, v1 in d.items():
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
                            v3.append(fmt(first))
                        else:
                            v3.append("%s-%s" % (fmt(first), fmt(last)))
                        first = i
                        last = i
                if first is not None:
                    if first == last:
                        v3.append(fmt(first))
                    else:
                        v3.append("%s-%s" % (fmt(first), fmt(last)))
                    first = None
                    last = None
                d[k1][k2] = ''.join(v3)
    else:
        for k1, v1 in d.items():
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
                        v2.append(fmt(first))
                    else:
                        v2.append("%s-%s" % (fmt(first), fmt(last)))
                    first = i
                    last = i
            if first is not None:
                if first == last:
                    v2.append(fmt(first))
                else:
                    v2.append("%s-%s" % (fmt(first), fmt(last)))
                first = None
                last = None
            d[k1] = ''.join(v2)


def gen_blocks(all_chars, f):
    """Generate Unicode blocks."""

    f.write('unicode_blocks = {')
    max_unicode = 0xffff if NARROW else 0x10FFFF

    with open(os.path.join(HOME, 'unicodedata', UNIVERSION, 'Blocks.txt'), 'r') as uf:
        for line in uf:
            if not line.startswith('#'):
                data = line.split(';')
                if len(data) < 2:
                    continue
                block = [int(i, 16) for i in data[0].strip().split('..')]
                if NARROW and block[0] > max_unicode:
                    break
                inverse_range = []
                if block[0] > 0:
                    inverse_range.append("%s-%s" % (uniformat(0), uniformat(block[0] - 1)))
                if block[1] < max_unicode:
                    inverse_range.append("%s-%s" % (uniformat(block[1] + 1), uniformat(max_unicode)))
                name = data[1].strip().lower().replace(' ', '').replace('-', '').replace('_', '')
                f.write('\n    "%s": "%s-%s",' % (name, uniformat(block[0]), uniformat(block[1])))
                f.write('\n    "^%s": "%s",' % (name, ''.join(inverse_range)))
        f.write('\n}\n')


def gen_scripts(all_chars, f):
    """Generate Unicode scripts."""

    max_unicode = 0xffff if NARROW else 0x10FFFF

    def create_span(unirange):
        """Clamp the unicode range."""
        if len(unirange) < 2:
            unirange.append(unirange[0])
        if NARROW:
            if unirange[0] > max_unicode:
                return None
            if unirange[1] > max_unicode:
                unirange[1] = max_unicode
        return [x for x in range(unirange[0], unirange[1] + 1)]

    scripts = {}
    with open(os.path.join(HOME, 'unicodedata', UNIVERSION, 'Scripts.txt'), 'r') as uf:
        for line in uf:
            if not line.startswith('#'):
                data = line.split(';')
                if len(data) < 2:
                    continue
                span = create_span([int(i, 16) for i in data[0].strip().split('..')])
                if span is None:
                    continue
                name = data[1].split('#')[0].strip().lower().replace(' ', '').replace('-', '').replace('_', '')

                if name not in scripts:
                    scripts[name] = []
                scripts[name].extend(span)

    for name in list(scripts.keys()):
        s = set(scripts[name])
        scripts[name] = sorted(s)
        scripts['^' + name] = sorted(all_chars - s)

    # Convert characters values to ranges
    char2range(scripts)

    # Write out the unicode properties
    f.write('unicode_scripts = {\n')
    count = len(scripts) - 1
    i = 0
    for k1, v1 in sorted(scripts.items()):
        f.write('    "%s": "%s"' % (k1, v1))
        if i == count:
            f.write('\n}\n')
        else:
            f.write(',\n')
        i += 1


def gen_posix(all_chars, f, binary=False):
    """Generate the binary posix table and write out to file."""

    posix_table = {}

    prefix = 'b' if binary else ''

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

    # Lower: [a-z]
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

    # XDigit: [A-Fa-f0-9]
    s2 = set([x for x in range(0x30, 0x39 + 1)])
    s2 |= set([x for x in range(0x41, 0x46 + 1)])
    s2 |= set([x for x in range(0x61, 0x66 + 1)])
    posix_table["xdigit"] = list(s2)
    posix_table["^xdigit"] = list(all_chars - s2)

    # Convert characters values to ranges
    char2range(posix_table, binary=binary)

    # Write out the unicode properties
    f.write('%sposix_properties = {\n' % prefix)
    count = len(posix_table) - 1
    i = 0
    for k1, v1 in sorted(posix_table.items()):
        f.write('    "%s": %s"%s"' % (k1, prefix, v1))
        if i == count:
            f.write('\n}\n')
        else:
            f.write(',\n')
        i += 1


def gen_uposix(table, all_chars, f):
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

    # XDigit: [A-Fa-f0-9]
    s2 = set([x for x in range(0x30, 0x39 + 1)])
    s2 |= set([x for x in range(0x41, 0x46 + 1)])
    s2 |= set([x for x in range(0x61, 0x66 + 1)])
    posix_table["xdigit"] = list(s2)
    posix_table["^xdigit"] = list(all_chars - s2)

    # Convert characters values to ranges
    char2range(posix_table)

    # Write out the unicode properties
    f.write('posix_unicode_properties = {\n')
    count = len(posix_table) - 1
    i = 0
    for k1, v1 in sorted(posix_table.items()):
        f.write('    "%s": "%s"' % (k1, v1))
        if i == count:
            f.write('\n}\n')
        else:
            f.write(',\n')
        i += 1


def gen_gc_alias(f):
    """Generate the General Category alias."""

    def format_name(text):
        """Format the name."""
        return text.strip().lower().replace(' ', '').replace('-', '').replace('_', '')

    alias = {}
    with open(os.path.join(HOME, 'unicodedata', UNIVERSION, 'PropertyValueAliases.txt'), 'r') as uf:
        for line in uf:
            if line.startswith('gc ;'):
                data = [format_name(x) for x in line.split('#')[0].split(';')[1:]]
                alias[data[1]] = data[0]

    f.write('unicode_gc_alias = {\n')
    count = len(alias) - 1
    i = 0
    for k1, v1 in sorted(alias.items()):
        f.write('    "%s": "%s"' % (k1, v1))
        if i == count:
            f.write('\n}\n')
        else:
            f.write(',\n')
        i += 1


def gen_properties(f):
    """Generate the property table and dump it to the provided file."""

    # L& or Lc won't be found in the table,
    # so intialize 'c' at the start. & will have to be converted to 'c'
    # before sending it through.
    table = {'l': {'c': [], '^c': []}}
    all_chars = set([x for x in range(UNICODE_RANGE[0], UNICODE_RANGE[1] + 1)])
    with open(os.path.join(HOME, 'unicodedata', UNIVERSION, 'UnicodeData.txt'), 'r') as uf:
        for line in uf:
            data = line.strip().split(';')
            if data:
                i = int(data[0], 16)
                if NARROW and i > UNICODE_RANGE[1]:
                    continue
                p = data[2].lower()
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
    gen_blocks(all_chars, f)

    # Generate Unicode scripts
    gen_scripts(all_chars, f)

    # Generate posix table and write out to file.
    gen_posix(all_chars, f)
    gen_uposix(table, all_chars, f)

    # Gen gc mapping.
    gen_gc_alias(f)

    # Convert char values to string ranges.
    char2range(table, double=True)

    # Write out the unicode properties
    f.write('unicode_properties = {\n')
    count = len(table) - 1
    i = 0
    for k1, v1 in sorted(table.items()):
        f.write('    "%s": {\n' % k1)
        count2 = len(v1) - 1
        j = 0
        for k2, v2 in sorted(v1.items()):
            f.write('        "%s": "%s"' % (k2, v2))
            if j == count2:
                f.write('\n    }')
            else:
                f.write(',\n')
            j += 1
        if i == count:
            f.write('\n}\n')
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
