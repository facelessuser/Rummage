"""
Generate a unicode prop table for Python narrow and wide builds.

Narrow builds will stop at 0xffff.
"""
from __future__ import unicode_literals
import sys
import struct
import unicodedata
import codecs

__version__ = '1.0.0'

# Compatibility
PY3 = sys.version_info >= (3, 0) and sys.version_info < (4, 0)
WIDE_RANGE = (0x0000, 0x10FFFF)
NARROW_RANGE = (0x0000, 0xFFFF)
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


def build_unicode_property_table(output):
    """Build and write out unicode property table."""

    with codecs.open(output, 'w', 'utf-8') as f:
        f.write(
            '"""Unicode Properties (autogen)."""\nfrom __future__ import unicode_literals\n'
            'import sys\n\n'
            'NARROW = sys.maxunicode == 0xFFFF\n\n'
        )

        f.write('if not NARROW:\n')
        gen_properties(f)
        f.write('else:\n')
        gen_properties(f, narrow=True)


def gen_posix(posix_table, table, all_chars, f):
    """Generate the posix table and write out to file."""

    xdigit = (
        0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39,  # Digit
        0x41, 0x42, 0x43, 0x44, 0x45, 0x46,                          # A-F
        0x61, 0x62, 0x63, 0x64, 0x65, 0x66                           # a-f
    )

    # Alnum: \p{L&}\p{Nd}
    s2 = set(table['L']['&'] + table['N']['d'])
    posix_table["Alnum"] = list(s2)
    posix_table["^Alnum"] = list(all_chars - s2)

    # Alpha \p{L&}
    s2 = set(table['L']['&'])
    posix_table["Alpha"] = list(s2)
    posix_table["^Alpha"] = list(all_chars - s2)

    # ASCII: \x00-\x7F
    s2 = set([x for x in range(0, 0x80)])
    posix_table["ASCII"] = list(s2)
    posix_table["^ASCII"] = list(all_chars - s2)

    # Blank: \p{Zs}\t
    s2 = set(table['Z']['s'] + [0x09])
    posix_table["Blank"] = list(s2)
    posix_table["^Blank"] = list(all_chars - s2)

    # Cntrl: \p{Cc}
    s2 = set(table['C']['c'])
    posix_table["Cntrl"] = list(s2)
    posix_table["^Cntrl"] = list(all_chars - s2)

    # Digit: \p{Nd}
    s2 = set(table['N']['d'])
    posix_table["Digit"] = list(s2)
    posix_table["^Digit"] = list(all_chars - s2)

    # Graph: [^\p{Z}\p{C}]
    s2 = set()
    for table_name in ('Z', 'C'):
        for sub_table_name in table[table_name]:
            if not sub_table_name.startswith('^'):
                s2 |= set(table[table_name][sub_table_name])
    posix_table["Graph"] = list(all_chars - s2)
    posix_table["^Graph"] = list(s2)

    # Lower: \p{Ll}
    s2 = set(table['L']['l'])
    posix_table["Lower"] = list(s2)
    posix_table["^Lower"] = list(all_chars - s2)

    # Print: \P{C}
    for table_name in ('C',):
        for sub_table_name in table[table_name]:
            if not sub_table_name.startswith('^'):
                s2 |= set(table[table_name][sub_table_name])
    posix_table["Print"] = list(all_chars - s2)
    posix_table["^Print"] = list(s2)

    # Punct: \p{P}\p{S}
    for table_name in ('P', 'S'):
        for sub_table_name in table[table_name]:
            if not sub_table_name.startswith('^'):
                s2 |= set(table[table_name][sub_table_name])
    posix_table["Punct"] = list(s2)
    posix_table["^Punct"] = list(all_chars - s2)

    # Space: \p{Z}\t\r\n\v\f
    s2 = set()
    for table_name in ('Z',):
        for sub_table_name in table[table_name]:
            if not sub_table_name.startswith('^'):
                s2 |= set(table[table_name][sub_table_name])
    s2 |= set([x for x in range(0x09, 0x0e)])
    posix_table["Space"] = list(s2)
    posix_table["^Space"] = list(all_chars - s2)

    # Upper: \p{Lu}
    s2 = set(table['L']['u'])
    posix_table["Upper"] = list(s2)
    posix_table["^Upper"] = list(all_chars - s2)

    # Graph: \p{L}\p{N}\p{Pc}
    s2 = set()
    for table_name in ('L', 'N'):
        for sub_table_name in table[table_name]:
            if not sub_table_name.startswith('^'):
                s2 |= set(table[table_name][sub_table_name])
    s2 |= set(table['P']['c'])
    posix_table["Word"] = list(s2)
    posix_table["^Word"] = list(all_chars - s2)

    # XDigit: A-Fa-f0-9
    s2 = set(xdigit)
    posix_table["XDigit"] = list(s2)
    posix_table["^XDigit"] = list(all_chars - s2)

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

    # L& won't be found in the table, so intialize it at the start.
    table = {'L': {'&': [], '^&': []}}
    posix_table = {}
    all_chars = set()
    p = None
    for i in range(unicode_range[0], unicode_range[1] + 1):
        all_chars.add(i)
        c = uchr(i)
        p = unicodedata.category(c)

        if p[0] not in table:
            table[p[0]] = {}
        if p[1] not in table[p[0]]:
            table[p[0]][p[1]] = []
            table[p[0]]['^' + p[1]] = []
        table[p[0]][p[1]].append(i)
        # Add L& which is a combo of Ll, Lu, and Lt
        if p[0] == 'L' and p[1] in ('l', 'u', 't'):
            table['L']['&'].append(i)

    # Create inverse of each category
    for k1, v1 in table.items():
        inverse_category = set()
        for k2, v2 in v1.items():
            if not k2.startswith('^'):
                s2 = set(v2)
                inverse_category |= s2
                table[k1]['^' + k2] = list(all_chars - s2)
        table[k1]['^'] = list(all_chars - inverse_category)

    # Generate posix table and write out to file.
    gen_posix(posix_table, table, all_chars, f)

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
