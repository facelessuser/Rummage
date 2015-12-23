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
import re

__version__ = '2.0.0'

UNIVERSION = unicodedata.unidata_version
HOME = os.path.dirname(os.path.abspath(__file__))
MAXUNICODE = sys.maxunicode
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

HEADER = '''\
"""Unicode Properties (autogen)."""
from __future__ import unicode_literals
import sys
PY3 = sys.version_info >= (3, 0) and sys.version_info[0:2] < (4, 0)
if PY3:
    binary_type = bytes  # noqa
else:
    binary_type = str  # noqa

NARROW = sys.maxunicode == 0xFFFF
'''


ACCESSORS = '''

def get_posix_property(value, uni=False):
    """Retrieve the posix category."""

    if isinstance(value, binary_type):
        return bposix_properties[value.decode('utf-8')]
    elif uni:
        return posix_unicode_properties[value]
    else:
        return posix_properties[value]


def get_uposix_property(value):
    """"Get unicode posix property (aliases allowed)."""

    if value.startswith('^'):
        negated = value[1:]
        value = '^' + unicode_alias['posix'].get(negated, negated)
    else:
        value = unicode_alias['posix'].get(value, value)

    return posix_unicode_properties[value]


def get_gc_property(value):
    """Get GC property."""

    if value.startswith('^'):
        negate = True
        value = value[1:]
    else:
        negate = False

    value = unicode_alias['gc'].get(value, value)

    assert 1 <= len(value) <= 2, 'Invalid property!'

    if not negate:
        p1, p2 = (value[0], value[1]) if len(value) > 1 else (value[0], None)
        return ''.join(
            [v for k, v in unicode_properties.get(p1, {}).items() if not k.startswith('^')]
        ) if p2 is None else unicode_properties.get(p1, {}).get(p2, '')
    else:
        p1, p2 = (value[0], value[1]) if len(value) > 1 else (value[0], '')
        return unicode_properties.get(p1, {}).get('^' + p2, '')


def get_binary_property(value):
    """"Get BINARY property."""

    if value.startswith('^'):
        negated = value[1:]
        value = '^' + unicode_alias['binary'].get(negated, negated)
    else:
        value = unicode_alias['binary'].get(value, value)

    return unicode_binary[value]


def get_script_property(value):
    """"Get SC property."""

    if value.startswith('^'):
        negated = value[1:]
        value = '^' + unicode_alias['sc'].get(negated, negated)
    else:
        value = unicode_alias['sc'].get(value, value)

    return unicode_scripts[value]


def get_block_property(value):
    """"Get BLK property."""

    if value.startswith('^'):
        negated = value[1:]
        value = '^' + unicode_alias['blk'].get(negated, negated)
    else:
        value = unicode_alias['blk'].get(value, value)

    return unicode_blocks[value]


def get_bidi_property(value):
    """"Get BC property."""

    if value.startswith('^'):
        negated = value[1:]
        value = '^' + unicode_alias['bc'].get(negated, negated)
    else:
        value = unicode_alias['bc'].get(value, value)

    return unicode_bidi_classes[value]


def get_unicode_property(value, prop=None):
    """Retrieve the unicode category from the table."""

    if prop is not None:
        try:
            if prop in ('gc', 'generalcategory'):
                return get_gc_property(value)
            if prop in ('sc', 'script'):
                return get_script_property(value)
            if prop in ('blk', 'block'):
                return get_block_property(value)
            if prop in ('bc', 'bidiclass'):
                return get_bidi_property(value)
        except Exception:
            raise ValueError('Invalid Unicode property!')

    if value.startswith('^'):
        temp = value[1:]
        negate = '^'
    else:
        temp = value
        negate = ''

    try:
        return get_gc_property(value)
    except Exception:
        pass

    if temp.startswith('is'):
        try:
            return get_script_property(negate + temp[2:])
        except Exception:
            pass
    try:
        return get_script_property(value)
    except Exception:
        pass
    if temp.startswith('in'):
        try:
            return get_block_property(negate + temp[2:])
        except Exception:
            pass
    try:
        return get_block_property(value)
    except Exception:
        pass
    try:
        return get_binary_property(value)
    except Exception:
        pass
    try:
        return get_uposix_property(value)
    except Exception:
        pass

    raise ValueError('Invalid Unicode property!')
'''


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


def create_span(unirange):
    """Clamp the unicode range."""
    if len(unirange) < 2:
        unirange.append(unirange[0])
    if NARROW:
        if unirange[0] > MAXUNICODE:
            return None
        if unirange[1] > MAXUNICODE:
            unirange[1] = MAXUNICODE
    return [x for x in range(unirange[0], unirange[1] + 1)]


def char2range(d, binary=False):
    """Convert the characters in the dict to a range in string form."""

    fmt = binaryformat if binary else uniformat

    for k1, v1 in d.items():
        if not isinstance(v1, list):
            char2range(v1, binary=binary)
        else:
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

    with open(os.path.join(HOME, 'unicodedata', UNIVERSION, 'Blocks.txt'), 'r') as uf:
        for line in uf:
            if not line.startswith('#'):
                data = line.split(';')
                if len(data) < 2:
                    continue
                block = [int(i, 16) for i in data[0].strip().split('..')]
                if NARROW and block[0] > MAXUNICODE:
                    break
                inverse_range = []
                if block[0] > 0:
                    inverse_range.append("%s-%s" % (uniformat(0), uniformat(block[0] - 1)))
                if block[1] < MAXUNICODE:
                    inverse_range.append("%s-%s" % (uniformat(block[1] + 1), uniformat(MAXUNICODE)))
                name = data[1].strip().lower().replace(' ', '').replace('-', '').replace('_', '')
                f.write('\n    "%s": "%s-%s",' % (name, uniformat(block[0]), uniformat(block[1])))
                f.write('\n    "^%s": "%s",' % (name, ''.join(inverse_range)))
        f.write('\n}\n')


def gen_scripts(all_chars, f):
    """Generate Unicode scripts."""

    scripts = {}
    with open(os.path.join(HOME, 'unicodedata', UNIVERSION, 'Scripts.txt'), 'r') as uf:
        for line in uf:
            if not line.startswith('#'):
                data = line.split('#')[0].split(';')
                if len(data) < 2:
                    continue
                span = create_span([int(i, 16) for i in data[0].strip().split('..')])
                if span is None:
                    continue
                name = data[1].strip().lower().replace(' ', '').replace('-', '').replace('_', '')

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


def gen_binary(all_chars, f):
    """Generate binary properties."""

    categories = []
    binary_props = (
        ('DerivedCoreProperties.txt', None),
        ('PropList.txt', None),
        ('DerivedNormalizationProps.txt', ('Changes_When_NFKC_Casefolded', 'Full_Composition_Exclusion'))
    )
    binary = {}
    for filename, include in binary_props:
        with open(os.path.join(HOME, 'unicodedata', UNIVERSION, filename), 'r') as uf:
            for line in uf:
                if not line.startswith('#'):
                    data = line.split('#')[0].split(';')
                    if len(data) < 2:
                        continue
                    if include and data[1].strip() not in include:
                        continue
                    span = create_span([int(i, 16) for i in data[0].strip().split('..')])
                    if span is None:
                        continue
                    name = data[1].strip().lower().replace(' ', '').replace('-', '').replace('_', '')

                    if name not in binary:
                        binary[name] = []
                        categories.append(name)
                    binary[name].extend(span)

    with open(os.path.join(HOME, 'unicodedata', UNIVERSION, 'CompositionExclusions.txt'), 'r') as uf:
        name = 'compositionexclusion'
        for line in uf:
            if not line.startswith('#'):
                data = [x.strip() for x in line.split('#')[0] if x.strip()]
                if not data:
                    continue
                span = create_span([int(data[0], 16)])
                if span is None:
                    continue

                if name not in binary:
                    binary[name] = []
                    categories.append(name)
                binary[name].extend(span)
                binary['full' + name].extend(span)

    with open(os.path.join(HOME, 'unicodedata', UNIVERSION, 'UnicodeData.txt'), 'r') as uf:
        name = 'bidimirrored'
        for line in uf:
            data = line.strip().split(';')
            if data:
                if data[9].strip().lower() != 'y':
                    continue
                span = create_span([int(data[0].strip(), 16)])
                if span is None:
                    continue

                if name not in binary:
                    binary[name] = []
                    categories.append(name)
                binary[name].extend(span)

    for name in list(binary.keys()):
        s = set(binary[name])
        binary[name] = sorted(s)
        binary['^' + name] = sorted(all_chars - s)

    # Convert characters values to ranges
    char2range(binary)

    # Write out the unicode properties
    f.write('unicode_binary = {\n')
    count = len(binary) - 1
    i = 0
    for k1, v1 in sorted(binary.items()):
        f.write('    "%s": "%s"' % (k1, v1))
        if i == count:
            f.write('\n}\n')
        else:
            f.write(',\n')
        i += 1

    return categories[:]


def gen_bidi(all_chars, f):
    """Generate bidi class properties."""

    bidi_class = {}
    with open(os.path.join(HOME, 'unicodedata', UNIVERSION, 'UnicodeData.txt'), 'r') as uf:
        for line in uf:
            data = line.strip().split(';')
            if data:
                bidi = data[4].strip().lower()
                if not bidi:
                    continue
                value = int(data[0].strip(), 16)
                if value > MAXUNICODE:
                    continue

                if bidi not in bidi_class:
                    bidi_class[bidi] = []
                bidi_class[bidi].append(value)

    for name in list(bidi_class.keys()):
        s = set(bidi_class[name])
        bidi_class[name] = sorted(s)
        bidi_class['^' + name] = sorted(all_chars - s)

    # Convert characters values to ranges
    char2range(bidi_class)

    f.write('unicode_bidi_classes = {\n')
    count = len(bidi_class) - 1
    i = 0
    for k1, v1 in sorted(bidi_class.items()):
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


def gen_alias(categories, f):
    """Generate alias."""

    alias_re = re.compile(r'^#\s+(\w+)\s+\((\w+)\)\s*$')

    def format_name(text):
        """Format the name."""
        return text.strip().lower().replace(' ', '').replace('-', '').replace('_', '')

    alias = {}
    gather = False
    current_category = None
    line_re = None
    with open(os.path.join(HOME, 'unicodedata', UNIVERSION, 'PropertyValueAliases.txt'), 'r') as uf:
        for line in uf:
            m = alias_re.match(line)
            if m:
                original_name = format_name(m.group(1))
                gather = original_name in categories
                current_category = format_name(m.group(2))
                line_re = re.compile(r'%s\s*;' % current_category, re.I)
            if gather and line_re.match(line):
                data = [format_name(x) for x in line.split('#')[0].split(';')]
                if current_category in ('sc', 'blk'):
                    data[1], data[2] = data[2], data[1]
                if len(data) == 5 and data[2] in ('yes', 'no') and data[1] in ('n', 'y'):
                    if 'binary' not in alias:
                        alias['binary'] = {}
                    alias['binary'][data[0]] = original_name
                else:
                    if current_category not in alias:
                        alias[current_category] = {}
                    for a in data[2:]:
                        if a == 'n/a':
                            continue
                        alias[current_category][a] = data[1]

    alias['posix'] = {
        'posixalnum': 'alnum',
        'posixalpha': 'alpha',
        'posixascii': 'ascii',
        'posixblank': 'blank',
        'posixcntrl': 'cntrl',
        'posixdigit': 'digit',
        'posixgraph': 'graph',
        'posixlower': 'lower',
        'posixprint': 'print',
        'posixspace': 'space',
        'posixupper': 'upper',
        'posixxdigit': 'xdigit'
    }

    f.write('unicode_alias = {\n')
    count = len(alias) - 1
    i = 0
    for k1, v1 in sorted(alias.items()):
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


def gen_properties(f):
    """Generate the property table and dump it to the provided file."""

    # L& or Lc won't be found in the table,
    # so intialize 'c' at the start. & will have to be converted to 'c'
    # before sending it through.
    categories = ['generalcategory', 'script', 'block', 'bidiclass']
    print('Building: General Category')
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
                # Add LC which is a combo of Ll, Lu, and Lt
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
    print('Building: Blocks')
    gen_blocks(all_chars, f)

    # Generate Unicode scripts
    print('Building: Scripts')
    gen_scripts(all_chars, f)

    # Generate Unicode bidi classes
    print('Building: Bidi Classes')
    gen_bidi(all_chars, f)

    # Generate Unicode binary
    print('Building: Binary')
    categories.extend(gen_binary(all_chars, f))

    # Generate posix table and write out to file.
    print('Building: Posix')
    gen_posix(set([x for x in range(0, 0xff + 1)]), f, binary=True)
    gen_posix(all_chars, f)
    gen_uposix(table, all_chars, f)

    # Gen gc mapping.
    print('Builiding: Aliases')
    gen_alias(categories, f)

    # Convert char values to string ranges.
    char2range(table)

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


def build_unicode_property_table(output):
    """Build and write out unicode property table."""

    with codecs.open(output, 'w', 'utf-8') as f:
        f.write(HEADER)
        gen_properties(f)
        f.write(ACCESSORS)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(prog='unipropgen', description='Generate a unicode property table.')
    parser.add_argument('--version', action='version', version="%(prog)s " + __version__)
    parser.add_argument('output', default=None, help='Output file.')
    args = parser.parse_args()

    build_unicode_property_table(args.output)
