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

    if value <= 0xFFFF:
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


def gen_properties(f, narrow=False):
    """Generate the property table and dump it to the provided file."""

    if not narrow:
        unicode_range = WIDE_RANGE
    else:
        unicode_range = NARROW_RANGE

    # L& won't be found in the table, so intialize it at the start.
    table = {'L': {'&': [], '^&': []}}
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
                    first = None
                    last = None
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
