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
UNIVERSION_INFO = tuple([int(x) for x in UNIVERSION.split('.')])
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


def format_name(text):
    """Format the name."""
    return text.strip().lower().replace(' ', '').replace('-', '').replace('_', '')


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
        if not isinstance(v1, (list, set)):
            char2range(v1, binary=binary)
        else:
            last = None
            first = None
            v2 = []
            for i in sorted(v1):
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
                name = format_name(data[1])
                f.write('\n    "%s": "%s-%s",' % (name, uniformat(block[0]), uniformat(block[1])))
                f.write('\n    "^%s": "%s",' % (name, ''.join(inverse_range)))
        f.write('\n}\n')


def gen_enum(all_chars, file_name, obj_name, f, field=1):
    """Generate generic enum."""

    obj = {}
    with open(os.path.join(HOME, 'unicodedata', UNIVERSION, file_name), 'r') as uf:
        for line in uf:
            if not line.startswith('#'):
                data = line.split('#')[0].split(';')
                if len(data) < 2:
                    continue
                span = create_span([int(i, 16) for i in data[0].strip().split('..')])
                if span is None:
                    continue
                name = format_name(data[field])

                if name not in obj:
                    obj[name] = []
                obj[name].extend(span)

    for name in list(obj.keys()):
        obj[name] = set(obj[name])
        obj['^' + name] = all_chars - obj[name]

    # Convert characters values to ranges
    char2range(obj)

    # Write out the unicode properties
    f.write('%s = {\n' % obj_name)
    count = len(obj) - 1
    i = 0
    for k1, v1 in sorted(obj.items()):
        f.write('    "%s": "%s"' % (k1, v1))
        if i == count:
            f.write('\n}\n')
        else:
            f.write(',\n')
        i += 1


def gen_age(all_chars, f):
    """Generate Age."""

    obj = {}
    with open(os.path.join(HOME, 'unicodedata', UNIVERSION, 'DerivedAge.txt'), 'r') as uf:
        for line in uf:
            if not line.startswith('#'):
                data = line.split('#')[0].split(';')
                if len(data) < 2:
                    continue
                span = create_span([int(i, 16) for i in data[0].strip().split('..')])
                if span is None:
                    continue
                name = format_name(data[1])

                if name not in obj:
                    obj[name] = []
                obj[name].extend(span)

    unassigned = set()
    for x in obj.values():
        unassigned.update(x)
    obj['na'] = all_chars - unassigned

    for name in list(obj.keys()):
        obj[name] = set(obj[name])
        obj['^' + name] = all_chars - obj[name]

    # Convert characters values to ranges
    char2range(obj)

    # Write out the unicode properties
    f.write('%s = {\n' % 'unicode_age')
    count = len(obj) - 1
    i = 0
    for k1, v1 in sorted(obj.items()):
        f.write('    "%s": "%s"' % (k1, v1))
        if i == count:
            f.write('\n}\n')
        else:
            f.write(',\n')
        i += 1


def gen_nf_quick_check(all_chars, f):
    """Generate binary properties."""

    categories = []
    nf = {}
    with open(os.path.join(HOME, 'unicodedata', UNIVERSION, 'DerivedNormalizationProps.txt'), 'r') as uf:
        for line in uf:
            if not line.startswith('#'):
                data = line.split('#')[0].split(';')
                if len(data) < 2:
                    continue
                if not data[1].strip().lower().endswith('_qc'):
                    continue
                span = create_span([int(i, 16) for i in data[0].strip().split('..')])
                if span is None:
                    continue
                name = format_name(data[1][:-3] + 'quickcheck')
                subvalue = format_name(data[2])

                if name not in nf:
                    nf[name] = {}
                    categories.append(name)
                if subvalue not in nf[name]:
                    nf[name][subvalue] = []
                nf[name][subvalue].extend(span)

    for k1, v1 in nf.items():
        temp = set()
        for k2 in list(v1.keys()):
            temp.update(v1[k2])
        v1['y'] = all_chars - temp

    for k1, v1 in nf.items():
        for name in list(v1.keys()):
            nf[k1][name] = set(nf[k1][name])
            nf[k1]['^' + name] = all_chars - nf[k1][name]

    # Convert characters values to ranges
    char2range(nf)

    for key, value in sorted(nf.items()):
        # Write out the unicode properties
        f.write('unicode_%s = {\n' % key.replace('quickcheck', '_quick_check'))
        count = len(value) - 1
        i = 0
        for k1, v1 in sorted(value.items()):
            f.write('    "%s": "%s"' % (k1, v1))
            if i == count:
                f.write('\n}\n')
            else:
                f.write(',\n')
            i += 1

    return categories


def gen_binary(table, all_chars, f):
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
                    name = format_name(data[1])

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
        binary[name] = set(binary[name])
        binary['^' + name] = all_chars - binary[name]

    gen_uposix(table, binary, all_chars)

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
        bidi_class[name] = set(bidi_class[name])
        bidi_class['^' + name] = all_chars - bidi_class[name]

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
    s = set([x for x in range(0x30, 0x39 + 1)])
    s.update([x for x in range(0x41, 0x5a + 1)])
    s.update([x for x in range(0x61, 0x7a + 1)])
    posix_table["alnum"] = s
    posix_table["^alnum"] = all_chars - s

    # Alpha: [a-zA-Z]
    s = set([x for x in range(0x41, 0x5a)])
    s.update([x for x in range(0x61, 0x7a)])
    posix_table["alpha"] = s
    posix_table["^alpha"] = all_chars - s

    # ASCII: [\x00-\x7F]
    posix_table["ascii"] = set([x for x in range(0, 0x7F + 1)])
    posix_table["^ascii"] = all_chars - posix_table["ascii"]

    # Blank: [ \t]
    posix_table["blank"] = set([0x20, 0x09])
    posix_table["^blank"] = all_chars - posix_table["blank"]

    # Cntrl: [\x00-\x1F\x7F]
    posix_table["cntrl"] = set([x for x in range(0, 0x1F + 1)] + [0x7F])
    posix_table["^cntrl"] = all_chars - posix_table["cntrl"]

    # Digit: [0-9]
    posix_table["digit"] = set([x for x in range(0x30, 0x39 + 1)])
    posix_table["^digit"] = all_chars - posix_table["digit"]

    # Graph: [\x21-\x7E]
    posix_table["graph"] = set([x for x in range(0x21, 0x7E + 1)])
    posix_table["^graph"] = all_chars - posix_table["graph"]

    # Lower: [a-z]
    posix_table["lower"] = set([x for x in range(0x61, 0x7a + 1)])
    posix_table["^lower"] = all_chars - posix_table["lower"]

    # Print: [\x20-\x7E]
    posix_table["print"] = set([x for x in range(0x20, 0x7E + 1)])
    posix_table["^print"] = all_chars - posix_table["print"]

    # Punct: [!\"\#$%&'()*+,\-./:;<=>?@\[\\\]^_`{|}~]
    s = set([x for x in range(0x21, 0x2f + 1)])
    s.update([x for x in range(0x3a, 0x40 + 1)])
    s.update([x for x in range(0x5b, 0x60 + 1)])
    s.update([x for x in range(0x7b, 0x7e + 1)])
    posix_table["punct"] = s
    posix_table["^punct"] = all_chars - s

    # Space: [ \t\r\n\v\f]
    posix_table["space"] = set([x for x in range(0x09, 0x0d + 1)] + [0x20])
    posix_table["^space"] = all_chars - posix_table["space"]

    # Upper: [A-Z]
    posix_table["upper"] = set([x for x in range(0x41, 0x5a + 1)])
    posix_table["^upper"] = all_chars - posix_table["upper"]

    # XDigit: [A-Fa-f0-9]
    s = set([x for x in range(0x30, 0x39 + 1)])
    s.update([x for x in range(0x41, 0x46 + 1)])
    s.update([x for x in range(0x61, 0x66 + 1)])
    posix_table["xdigit"] = s
    posix_table["^xdigit"] = all_chars - s

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


def gen_uposix(table, posix_table, all_chars):
    """Generate the posix table and write out to file."""

    # Alnum: [\p{L&}\p{Nd}]
    posix_table["posixalnum"] = set(table['l']['c'] + table['n']['d'])
    posix_table["^posixalnum"] = all_chars - posix_table["posixalnum"]

    # Alpha: [\p{L&}]
    posix_table["posixalpha"] = set(table['l']['c'])
    posix_table["^posixalpha"] = all_chars - posix_table["posixalpha"]

    # ASCII: [\x00-\x7F]
    posix_table["posixascii"] = set([x for x in range(0, 0x7F + 1)])
    posix_table["^posixascii"] = all_chars - posix_table["posixascii"]

    # Blank: [\p{Zs}\t]
    posix_table["posixblank"] = set(table['z']['s'] + [0x09])
    posix_table["^posixblank"] = all_chars - posix_table["posixblank"]

    # Cntrl: [\p{Cc}]
    posix_table["posixcntrl"] = set(table['c']['c'])
    posix_table["^posixcntrl"] = all_chars - posix_table["posixcntrl"]

    # Digit: [\p{Nd}]
    posix_table["posixdigit"] = set(table['n']['d'])
    posix_table["^posixdigit"] = all_chars - posix_table["posixdigit"]

    # Graph: [^\p{Z}\p{C}]
    s = set()
    for table_name in ('z', 'c'):
        for sub_table_name in table[table_name]:
            if not sub_table_name.startswith('^'):
                s.update(table[table_name][sub_table_name])
    posix_table["posixgraph"] = all_chars - s
    posix_table["^posixgraph"] = s

    # Lower: [\p{Ll}]
    posix_table["posixlower"] = set(table['l']['l'])
    posix_table["^posixlower"] = all_chars - posix_table["posixlower"]

    # Print: [\P{C}]
    s = set()
    for table_name in ('c',):
        for sub_table_name in table[table_name]:
            if not sub_table_name.startswith('^'):
                s.update(table[table_name][sub_table_name])
    posix_table["posixprint"] = all_chars - s
    posix_table["^posixprint"] = s

    # Punct: [\p{P}\p{S}]
    s = set()
    for table_name in ('p', 's'):
        for sub_table_name in table[table_name]:
            if not sub_table_name.startswith('^'):
                s.update(table[table_name][sub_table_name])
    posix_table["posixpunct"] = s
    posix_table["^posixpunct"] = all_chars - s

    # Space: [\p{Z}\t\r\n\v\f]
    s = set()
    for table_name in ('z',):
        for sub_table_name in table[table_name]:
            if not sub_table_name.startswith('^'):
                s.update(table[table_name][sub_table_name])
    s.update([x for x in range(0x09, 0x0e)])
    posix_table["posixspace"] = s
    posix_table["^posixspace"] = all_chars - s

    # Upper: [\p{Lu}]
    posix_table["posixupper"] = set(table['l']['u'])
    posix_table["^posixupper"] = all_chars - posix_table["posixupper"]

    # XDigit: [A-Fa-f0-9]
    s = set([x for x in range(0x30, 0x39 + 1)])
    s.update([x for x in range(0x41, 0x46 + 1)])
    s.update([x for x in range(0x61, 0x66 + 1)])
    posix_table["posixxdigit"] = s
    posix_table["^posixxdigit"] = all_chars - s


def gen_alias(enum, binary, f):
    """Generate alias."""

    alias_re = re.compile(r'^#\s+(\w+)\s+\((\w+)\)\s*$')

    categories = enum + binary
    alias = {}
    gather = False
    current_category = None
    line_re = None
    alias_header_re = re.compile(r'^#\s+(\w+)\s+Properties\s*$')
    divider_re = re.compile(r'#\s*=+\s*$')
    posix_props = ('alnum', 'blank', 'graph', 'print', 'xdigit')
    toplevel = (
        'catalog', 'enumerated', 'numeric', 'eastasianwidth',
        'linebreak', 'hangulsyllabletype', 'decompositiontype',
        'wordbreak', 'sentencebreak', 'graphemeclusterbreak',
        'joiningtype', 'joininggroup', 'numerictype',
        'numericvalue', 'canonicalcombiningclass', 'age',
        'nfcquickcheck', 'nfdquickcheck', 'nfkcquickcheck', 'nfkdquickcheck'
    )

    with open(os.path.join(HOME, 'unicodedata', UNIVERSION, 'PropertyAliases.txt'), 'r') as uf:
        div = False
        capture = False
        name = None
        for line in uf:
            if div:
                m = alias_header_re.match(line)
                if m:
                    name = format_name(m.group(1))
                    if name in toplevel:
                        capture = True
                        name = '_'
                    elif name in ('binary',):
                        capture = True
                    else:
                        capture = False
                    continue
                div = False
            elif divider_re.match(line):
                div = True
                continue
            elif line.startswith('#') or not line.strip():
                continue
            if capture:
                should_add = False
                data = [format_name(x) for x in line.split('#')[0].split(';')]
                index = 0
                for d in data:
                    if d in categories:
                        should_add = True
                        break
                    index += 1
                if should_add:
                    data[0], data[index] = data[index], data[0]
                    if name not in alias:
                        alias[name] = {}
                    for d in data[1:]:
                        alias[name][d] = data[0]

    with open(os.path.join(HOME, 'unicodedata', UNIVERSION, 'PropertyValueAliases.txt'), 'r') as uf:
        for line in uf:
            m = alias_re.match(line)
            if m:
                original_name = format_name(m.group(1))
                gather = original_name in categories
                current_category = format_name(m.group(2))
                line_re = re.compile(r'%s\s*;' % m.group(2), re.I)
            if gather and line_re.match(line):
                data = [format_name(x) for x in line.split('#')[0].split(';')]
                if current_category in ('sc', 'blk'):
                    data[1], data[2] = data[2], data[1]
                elif current_category == 'age' and UNIVERSION_INFO < (6, 1, 0):
                    if data[2] == 'unassigned':
                        data[1] = 'na'
                    else:
                        data[1], data[2] = data[2], 'V' + data[2].replace('.', '_')
                if len(data) == 5 and data[2] in ('yes', 'no') and data[1] in ('n', 'y'):
                    data = ['binary', original_name, data[0]]
                else:
                    data[0] = alias['_'].get(data[0], data[0])
                if data[0] not in alias:
                    alias[data[0]] = {}
                for a in data[2:]:
                    if a == 'n/a':
                        continue
                    if a not in alias[data[0]] and a != data[1]:
                        alias[data[0]][a] = data[1]

    for prop in posix_props:
        alias['binary'][prop] = 'posix' + prop

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

    cat = set(enum)
    for k in alias['_'].keys():
        cat.add(k)

    f.write('enum_names = {\n')
    count = len(cat) - 1
    i = 0
    for name in sorted(cat):
        f.write('    "%s"' % name)
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
    categories = [
        'generalcategory', 'script', 'block',
        'bidiclass', 'eastasianwidth', 'linebreak',
        'hangulsyllabletype', 'wordbreak', 'sentencebreak',
        'graphemeclusterbreak', 'decompositiontype', 'joiningtype',
        'joininggroup', 'numerictype', 'numericvalue',
        'canonicalcombiningclass', 'age'
    ]
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
                s = set(v2)
                inverse_category |= s
                table[k1]['^' + k2] = all_chars - s
        table[k1]['^'] = all_chars - inverse_category

    # Generate Unicode blocks
    print('Building: Blocks')
    gen_blocks(all_chars, f)

    # Generate Unicode scripts
    print('Building: Scripts')
    gen_enum(all_chars, 'Scripts.txt', 'unicode_scripts', f)

    # Generate Unicode bidi classes
    print('Building: Bidi Classes')
    gen_bidi(all_chars, f)

    # Generate Unicode binary
    print('Building: Binary')
    binary = gen_binary(table, all_chars, f)

    # Generate posix table and write out to file.
    print('Building: Posix')
    gen_posix(set([x for x in range(0, 0xff + 1)]), f, binary=True)
    gen_posix(all_chars, f)

    print('Building: Age')
    gen_age(all_chars, f)

    print('Building: East Asian Width')
    gen_enum(all_chars, 'EastAsianWidth.txt', 'unicode_east_asian_width', f)

    print('Building: Grapheme Cluster Break')
    gen_enum(all_chars, 'GraphemeBreakProperty.txt', 'unicode_grapheme_cluster_break', f)

    print('Building: Line Break')
    gen_enum(all_chars, 'LineBreak.txt', 'unicode_line_break', f)

    print('Building: Sentence Break')
    gen_enum(all_chars, 'SentenceBreakProperty.txt', 'unicode_sentence_break', f)

    print('Building: Word Break')
    gen_enum(all_chars, 'WordBreakProperty.txt', 'unicode_word_break', f)

    print('Building: Hangul Syllable Type')
    gen_enum(all_chars, 'HangulSyllableType.txt', 'unicode_hangul_syllable_type', f)

    print('Building: Decomposition Type')
    gen_enum(all_chars, 'DerivedDecompositionType.txt', 'unicode_decomposition_type', f)

    print('Building: Joining Type')
    gen_enum(all_chars, 'DerivedJoiningType.txt', 'unicode_joining_type', f)

    print('Building: Joining Group')
    gen_enum(all_chars, 'DerivedJoiningGroup.txt', 'unicode_joining_group', f)

    print('Building: Numeric Type')
    gen_enum(all_chars, 'DerivedNumericType.txt', 'unicode_numeric_type', f)

    print('Building: Numeric Value')
    gen_enum(all_chars, 'DerivedNumericValues.txt', 'unicode_numeric_values', f, field=3)

    print('Building: Canonical Combining Class')
    gen_enum(all_chars, 'DerivedCombiningClass.txt', 'uniocde_canonical_combining_class', f)

    print('Building: NF* Quick Check')
    categories.extend(gen_nf_quick_check(all_chars, f))

    print('Building: Aliases')
    gen_alias(categories, binary, f)

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


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(prog='unipropgen', description='Generate a unicode property table.')
    parser.add_argument('--version', action='version', version="%(prog)s " + __version__)
    parser.add_argument('output', default=None, help='Output file.')
    args = parser.parse_args()

    build_unicode_property_table(args.output)
