r"""
Backrefs.

Add the ability to use the following backrefs with re:

    * \c and \C...\E - Uppercase (search and replace)
    * \l and \L...\E - Lowercase (search and replace)
    * \Q and \Q...\E - Escape\quote (search)
    * \p{uL} and \p{Letter} and \p{Uppercase_Letter} - Unicode properties (search)

Compiling
=========
pattern = compile_search(r'somepattern', flags)
replace = compile_replace(pattern, r'\1 some replace pattern')

Usage
=========
text = pattern.sub(replace, 'sometext')

--or--

m = pattern.match('sometext')
if m:
    text = replace(m)  # similar to m.expand(template)

Licensed under MIT
Copyright (c) 2011 - 2015 Isaac Muse <isaacmuse@gmail.com>
"""
from __future__ import unicode_literals
import sre_parse
import functools
import re
import sys
import struct
import unicodedata
import os
try:
    import cpickle as pickle  # noqa
except Exception:
    import pickle

# Compatibility
PY3 = sys.version_info >= (3, 0) and sys.version_info < (4, 0)

if PY3:
    unichar = chr  # noqa
    string_type = str  # noqa
    binary_type = bytes  # noqa

    def iterstring(string):
        """Iterate through a string."""

        if isinstance(string, binary_type):
            for x in range(0, len(string)):
                yield string[x:x + 1]
        else:
            for c in string:
                yield c

    class Tokens(object):

        """Tokens base for PY3."""

        def iternext(self):
            """Common override method."""

        def __next__(self):
            """PY3 iterator compatible next."""

            return self.iternext()

else:
    unichar = unichr  # noqa
    string_type = basestring  # noqa
    binary_type = str  # noqa

    def iterstring(string):
        """Iterate through a string."""

        for c in string:
            yield c

    class Tokens(object):

        """Tokens base for PY2."""

        def iternext(self):
            """Common override method."""

        def next(self):
            """PY2 iterator compatible next."""

            return self.iternext()


def uchr(i):
    """Allow getting unicode character on narrow python builds."""

    try:
        return unichar(i)
    except ValueError:
        return struct.pack('i', i).decode('utf-32')


# Unicode variables
unicode_version = (1, 1, 0)
_unicode_range = (0x0000, 0x10FFFF)
_unicode_properties = None
_unicode_version = None
_loaded = False
_default_cache_name = "unicode_properties.cache"
if "_use_cache" not in globals():
    _use_cache = None


# Case upper or lower
UPPER = 0
LOWER = 1

# Mapping of friendly unicode category names to shorthand codes.
unicode_property_map = {
    # General
    "Control": "Cc",
    "Format": "Cf",
    "Surrogate": "Cs",
    "Private_Use": "Co",
    "Unassigned": "Cn",

    # Letters
    "Letter": "L",
    "Uppercase_Letter": "Lu",
    "Lowercase_Letter": "Ll",
    "Titlecase_Letter": "Lt",
    "Modifier_Letter": "Lm",
    "Other_Letter": "Lo",

    # Mark
    "Mark": "M",
    "Nonspacing_Mark": "Mc",
    "Spacing_Mark": "Me",
    "Enclosing_Mark": "Md",

    # Number
    "Number": "N",
    "Decimal_Number": "Nd",
    "Letter_Number": "Nl",
    "Other_Number": "No",

    # Punctuation
    "Punctuation": "P",
    "Connector_Punctuation": "Pc",
    "Dash_Punctuation": "Pd",
    "Open_Punctuation": "Ps",
    "Close_Punctuation": "Pe",
    "Initial_Punctuation": "Pi",
    "Final_Punctuation": "Pf",
    "Other_Punctuation": "Po",

    # Symbol
    "Symbol": "S",
    "Math_Symbol": "Sm",
    "Currency_Symbol": "Sc",
    "Modifier_Symbol": "Sk",
    "Other_Symbol": "So",

    # Separator
    "Separator": "Z",
    "Space_Separator": "Zs",
    "Line_Separator": "Zl",
    "Paragraph_Separator": "Zp"
}

# Regex pattern for unicode properties
UPROP = r'''
p\{
(?:
    C(?:c|f|s|o|n)?|L(?:u|l|t|m|o|n)?|M(?:n|c|e|d)?|N(?:d|l|o|c|d)?|
    P(?:c|d|s|e|i|f|o)?|S(?:c|m|k|o)?|Z(?:p|s|l)?|
    Letter|Uppercase_Letter|Lowercase_Letter|Titlecase_Letter|Modifier_Letter|Other_Letter|
    Mark|Nonspacing_Mark|Spacing_Mark|Enclosing_Mark|
    Number|Decimal_Number|Letter_Number|Other_Number|
    Punctuation|Connector_Punctuation|Dash_Punctuation|Open_Punctuation|Close_Punctuation|
    Initial_Punctuation|Final_Punctuation|Other_Punctuation|
    Symbol|Math_Symbol|Currency_Symbol|Modifier_Symbol|Other_Symbol|
    Separator|Space_Separator|Line_Separator|Paragraph_Separator|
    Control|Format|Surrogate|Private_Use|Unassigned
)
\}
'''

# Reference indexes
# Keep a list of unicode references and binary and index into them so
# we don't have to translate the strings or waste time searching in a dict.
DEF_BACK_REF = 0
REPLACE_TOKENS = 1
SEARCH_TOKENS = 2
VERBOSE_TOKENS = 3
EMPTY = 4
LS_BRACKET = 5
RS_BRACKET = 6
B_SLASH = 7
ESC_END = 8
END = 9
QUOTE = 10
LC = 11
LC_SPAN = 12
UC = 13
UC_SPAN = 14
HASHTAG = 15
NL = 16
UNI_PROP = 17
ASCII_LOW_PROPS = 18
ASCII_UPPER_PROPS = 19
VERBOSE_FLAG = 20
RE_SEARCH_REF = 21
RE_SEARCH_REF_VERBOSE = 22
RE_REPLACE_REF = 23
RE_IS_VERBOSE = 24

# Unicode string related references
utokens = (
    set("abfnrtvAbBdDsSwWZuxg"),     # DEF_BACK_REF
    set("cCElL"),                    # REPLACE_TOKENS
    set("cCElLpQ"),                  # SEARCH_TOKENS
    set("# "),                       # VERBOSE_TOKENS
    "",                              # EMPTY
    "[",                             # LS_BRACKET
    "]",                             # RS_BRACKET
    "\\",                            # B_SLASH
    "\\E",                           # ESC_END
    "E",                             # END
    "Q",                             # QUOTE
    "l",                             # LC
    "L",                             # LC_SPAN
    "c",                             # UC
    "C",                             # UC_SPAN
    '#',                             # HASHTAG
    '\n',                            # NL
    "p",                             # UNI_PROP
    'a-z',                           # ASCII_LOW_PROPS
    'A-Z',                           # ASCII_UPPER_PROPS
    'x',                             # VERBOSE_FLAG
    re.compile(                      # RE_SEARCH_REF
        r'''(?x)
        (\\)+
        (
            [lLcCEQ] |
            %(uni_prop)s
        )? |
        (
            [lLcCEQ] |
            %(uni_prop)s
        )
        ''' % {"uni_prop": UPROP}
    ),
    re.compile(                       # RE_SEARCH_REF_VERBOSE
        r'''(?x)
        (\\)+
        (
            [lLcCEQ#] |
            %(uni_prop)s
        )? |
        (
            [lLcCEQ#] |
            %(uni_prop)s
        )
        ''' % {"uni_prop": UPROP}
    ),
    re.compile(                       # RE_REPLACE_REF
        r'''(?x)
        (\\)+
        (
            [cClLE]
        )? |
        (
            [cClLE]
        )
        '''
    ),
    re.compile(r'\(\?([iLmsux])\)')   # RE_IS_VERBOSE
)

# Byte string related references
btokens = (
    set(                             # DEF_BACK_REF
        [
            b"a", b"b", b"f", b"n", b"r",
            b"t", b"v", b"A", b"b", b"B",
            b"d", b"D", b"s", b"S", b"w",
            b"W", b"Z", b"u", b"x", b"g"
        ]
    ),
    set(                              # REPLACE_TOKENS
        [b"c", b"C", b"E", b"l", b"L"]
    ),
    set(                              # SEARCH_TOKENS
        [b"c", b"C", b"E", b"l", b"L", b"Q"]
    ),
    set([b"#", b" "]),                # VERBOSE_TOKENS
    b"",                              # EMPTY
    b"[",                             # LS_BRACKET
    b"]",                             # RS_BRACKET
    b"\\",                            # B_SLASH
    b"\\E",                           # ESC_END
    b"E",                             # END
    b"Q",                             # QUOTE
    b"l",                             # LC
    b"L",                             # LC_SPAN
    b"c",                             # UC
    b"C",                             # UC_SPAN
    b'#',                             # HASHTAG
    b'\n',                            # NL
    b"p",                             # UNI_PROP
    b'a-z',                           # ASCII_LOW_PROPS
    b'A-Z',                           # ASCII_UPPER_PROPS
    b'x',                             # VERBOSE_FLAG
    re.compile(                       # RE_SEARCH_REF
        br'''(?x)
        (\\)+
        (
            [lLcCEQ]
        )? |
        (
            [lLcCEQ]
        )
        '''
    ),
    re.compile(                       # RE_SEARCH_REF_VERBOSE
        br'''(?x)
        (\\)+
        (
            [lLcCEQ#]
        )? |
        (
            [lLcCEQ#]
        )
        '''
    ),
    re.compile(                       # RE_REPLACE_REF
        br'''(?x)
        (\\)+
        (
            [cClLE]
        )? |
        (
            [cClLE]
        )
        '''
    ),
    re.compile(br'\(\?([iLmsux])\)')  # RE_IS_VERBOSE
)


# Unicode property table functions
def set_cache_directory(pth, name=None):  # pragma: no cover
    """Set cache path."""

    if name is None:
        name = _default_cache_name

    global _use_cache
    if os.path.exists(pth):
        _use_cache = os.path.join(pth, name)


def _build_unicode_property_table(unicode_range):
    """Build property table for unicode range."""

    table = {}
    p = None
    for i in range(*unicode_range):
        c = uchr(i)
        p = unicodedata.category(c)

        if p[0] not in table:
            table[p[0]] = {}
        if p[1] not in table[p[0]]:
            table[p[0]][p[1]] = []
        table[p[0]][p[1]].append(c)

    # Join as one string
    for v1 in table.values():
        for k2, v2 in v1.items():
            v1[k2] = ''.join(v2)

    return table


def get_unicode_category(prop):
    """Retrieve the unicode category from the table."""

    p1, p2 = (prop[0], prop[1]) if len(prop) > 1 else (prop[0], None)
    return ''.join(
        [x for x in _unicode_properties.get(p1, {}).values()]
    ) if p2 is None else _unicode_properties.get(p1, {}).get(p2, '')


def write_unicode_props(cache_file):  # pragma: no cover
    """Write unicode properties out."""

    global _unicode_properties
    global _unicode_version
    global _loaded

    _unicode_properties = _build_unicode_property_table(_unicode_range)

    try:
        with open(cache_file, 'wb') as f:
            pickle.dump(unicode_version, f)
            pickle.dump(_unicode_properties, f)
    except Exception:
        # Let's not fail on attempt to remove
        try:
            if os.path.exists(cache_file):
                os.unlink(cache_file)
        except Exception:
            pass
    _unicode_version = unicode_version
    _loaded = True


def read_unicode_props(cache_file):  # pragma: no cover
    """Read the unicode props."""

    global _unicode_properties
    global _loaded

    update = False

    try:
        with open(_use_cache, 'rb') as f:
            _unicode_version = pickle.load(f)
            if _unicode_version == unicode_version:
                _unicode_properties = pickle.load(f)
            else:
                update = True
        if update:
            write_unicode_props(cache_file)
        else:
            _loaded = True
    except Exception:
        # Let's not fail on attempt to remove
        try:
            if os.path.exists(_use_cache):
                os.unlink(_use_cache)
        except Exception:
            pass
        _unicode_properties = _build_unicode_property_table(_unicode_range)
        _unicode_version = unicode_version
        _loaded = True


def init_unicode():
    """Prepare unicode property tables and key pattern."""

    global _loaded
    global _unicode_properties
    if _use_cache is not None:  # pragma: no cover
        if not os.path.exists(_use_cache):
            write_unicode_props(_use_cache)
        else:
            read_unicode_props(_use_cache)
    else:
        _unicode_properties = _build_unicode_property_table(_unicode_range)

    _loaded = True


# Break apart template patterns into char tokens
class ReplaceTokens(Tokens):

    """Tokens."""

    def __init__(self, string, boundaries):
        """Initialize."""

        if isinstance(string, binary_type):
            tokens = btokens
        else:
            tokens = utokens

        self.string = string
        self.b_slash = tokens[B_SLASH]
        self.re_replace_ref = tokens[RE_REPLACE_REF]
        self.max_index = len(string) - 1
        self.index = 0
        self.last = 0
        self.current = None
        self.boundaries = boundaries
        self.boundary = self.boundaries.pop(0) if boundaries else (self.max_index + 1, self.max_index + 1)

    def _in_boundary(self, index):
        """Check if index is in current boundary."""

        return self.boundary is not None and index >= self.boundary[0] and index < self.boundary[1]

    def in_boundary(self):
        """Check if last/current index is in current boundary (public)."""
        return self._in_boundary(self.last)

    def _update_boundary(self):
        """Update to next boundary."""
        if self.boundaries:
            self.boundary = self.boundaries.pop(0)
        else:
            self.boundary = (self.max_index + 1, self.max_index + 1)

    def _out_of_boundary(self, index):
        """Return if the index has exceeded the right boundary."""

        return self.boundary is not None and index >= self.boundary[1]

    def __iter__(self):
        """Iterate."""

        return self

    def iternext(self):
        """
        Iterate through characters of the string.

        Count escaped l, L, c, C, E and backslash as a single char.
        """

        if self.index > self.max_index:
            raise StopIteration

        if self._out_of_boundary(self.index):
            self._update_boundary()

        if not self._in_boundary(self.index):
            char = self.string[self.index:self.index + 1]
            print(self.string)
            if char == self.b_slash:
                print(self.string[self.index + 1:self.boundary[0]])
                m = self.re_replace_ref.match(self.string[self.index + 1:self.boundary[0]])
                if m:
                    if m.group(1):
                        if m.group(2):
                            self.index += 1
                    else:
                        char += m.group(3)
        else:
            char = self.string[self.boundary[0]:self.boundary[1]]

        self.last = self.index
        self.index += len(char)
        self.current = char
        print('---results----')
        print(self.current)
        return self.current


class SearchTokens(Tokens):

    """Tokens."""

    def __init__(self, string, verbose):
        """Initialize."""

        if isinstance(string, binary_type):
            tokens = btokens
        else:
            tokens = utokens

        self.string = string
        if verbose:
            self.re_search_ref = tokens[RE_SEARCH_REF_VERBOSE]
        else:
            self.re_search_ref = tokens[RE_SEARCH_REF]
        self.b_slash = tokens[B_SLASH]
        self.max_index = len(string) - 1
        self.index = 0
        self.current = None

    def __iter__(self):
        """Iterate."""

        return self

    def iternext(self):
        """
        Iterate through characters of the string.

        Count escaped l, L, c, C, E and backslash as a single char.
        """

        if self.index > self.max_index:
            raise StopIteration

        char = self.string[self.index:self.index + 1]
        if char == self.b_slash:
            m = self.re_search_ref.match(self.string[self.index + 1:])
            if m:
                if m.group(1):
                    if m.group(2):
                        self.index += 1
                    else:
                        char += self.b_slash
                else:
                    char += m.group(3)

        self.index += len(char)
        self.current = char
        return self.current


# Templates
class ReplaceTemplate(object):

    """Replace template."""

    def __init__(self, pattern, template):
        """Initialize."""

        if isinstance(template, binary_type):
            self.binary = True
            tokens = btokens
        else:
            self.binary = False
            tokens = utokens
        self.__original = template
        self.__back_ref = set()
        self.b_slash = tokens[B_SLASH]
        self.def_back_ref = tokens[DEF_BACK_REF]
        self.empty = tokens[EMPTY]
        self.__add_back_references(tokens[REPLACE_TOKENS])
        self.__template = self.__escape_template(template)
        self.groups, self.literals = sre_parse.parse_template(self.__template, pattern)

    def get_base_template(self):
        """Return the unmodified template before expansion."""

        return self.__original

    def __escape_template(self, template):
        """
        Escape backreferences.

        Because the new backreferences are recognized by python
        we need to escape them so they come out okay.
        """

        new_template = []
        slash_count = 0
        for c in iterstring(template):
            if c == self.b_slash:
                slash_count += 1
            elif c != self.b_slash:
                if slash_count > 1 and c in self.__back_ref:
                    new_template.append(self.b_slash * (slash_count - 1))
                slash_count = 0
            new_template.append(c)
        if slash_count > 1:
            # End of line slash
            new_template.append(self.b_slash * (slash_count))
            slash_count = 0
        return self.empty.join(new_template)

    def __add_back_references(self, args):
        """
        Add new backreferences.

        Only add if they don't interfere with existing ones.
        """

        for arg in args:
            if isinstance(arg, binary_type if self.binary else string_type) and len(arg) == 1:
                if arg not in self.def_back_ref and arg not in self.__back_ref:
                    self.__back_ref.add(arg)

    def get_group_index(self, index):
        """Find and return the appropriate group index."""

        g_index = None
        for group in self.groups:
            if group[0] == index:
                g_index = group[1]
                break
        return g_index


class SearchTemplate(object):

    """Search Template."""

    def __init__(self, search, verbose=False):
        """Initialize."""

        if isinstance(search, binary_type):
            self.binary = True
            tokens = btokens
        else:
            self.binary = False
            tokens = utokens

        self.re_is_verbose = tokens[RE_IS_VERBOSE]
        self.verbose_flag = tokens[VERBOSE_FLAG]
        self.verbose = self.is_verbose(search, verbose)
        self.empty = tokens[EMPTY]
        self.b_slash = tokens[B_SLASH]
        self.ls_bracket = tokens[LS_BRACKET]
        self.rs_bracket = tokens[RS_BRACKET]
        self.esc_end = tokens[ESC_END]
        self.end = tokens[END]
        self.uni_prop = tokens[UNI_PROP]
        self.ascii_low_props = tokens[ASCII_LOW_PROPS]
        self.ascii_upper_props = tokens[ASCII_UPPER_PROPS]
        self.lc = tokens[LC]
        self.lc_span = tokens[LC_SPAN]
        self.uc = tokens[UC]
        self.uc_span = tokens[UC_SPAN]
        self.quote = tokens[QUOTE]
        self.nl = tokens[NL]
        self.hashtag = tokens[HASHTAG]
        if self.verbose:
            self.verbose_tokens = tokens[VERBOSE_TOKENS]
            self.search_tokens = tokens[SEARCH_TOKENS] | self.verbose_tokens
        else:
            self.verbose_tokens = tuple()
            self.search_tokens = tokens[SEARCH_TOKENS]
        self.search = search
        self.extended = []
        self.escaped = False
        self.groups = []

    def is_verbose(self, string, verbose):
        """Check if regex pattern is verbose."""

        v = verbose
        if not v:
            m = self.re_is_verbose.match(string.lstrip())
            if m and m.group(1) == self.verbose_flag:
                v = True
        return v

    def find_char_groups(self, s):
        """Find character groups."""

        pos = 0
        groups = []
        escaped = False
        found = False
        first = None
        for c in iterstring(s):
            if c == self.b_slash:
                escaped = not escaped
            elif escaped:
                escaped = False
            elif c == self.ls_bracket and not found:
                found = True
                first = pos
            elif c == self.rs_bracket and found and (pos != first + 1):
                groups.append((first, pos))
                found = False
            pos += 1
        return groups

    def unicode_props(self, i, props):
        """Insert unicode properties."""

        if not _loaded:
            init_unicode()

        if len(props) > 2:
            props = unicode_property_map.get(props, None)

        properties = []
        if props is not None:
            v = get_unicode_category(props)
            if v is not None:
                if not self.in_group(i.index - 1):
                    v = self.ls_bracket + v + self.rs_bracket
                properties = [v]
        return properties

    def ascii_props(self, i, case):
        """Insert ascii (or unicode) case properties."""

        if self.binary:
            v = self.ascii_upper_props if case == UPPER else self.ascii_low_props
            if not self.in_group(i.index - 1):
                v = self.ls_bracket + v + self.rs_bracket
            return [v]
        else:
            return self.unicode_props(i, 'Lu' if case == UPPER else 'Ll')

    def comments(self, i):
        """Handle comments in verbose patterns."""

        parts = []
        try:
            t = next(i)
            while t != self.nl:
                parts.append(t)
                t = next(i)
            parts.append(self.nl)
        except StopIteration:
            pass
        return parts

    def quoted(self, i):
        r"""Handle quoted block."""

        quoted = []
        raw = []
        if not self.in_group(i.index - 1):
            try:
                t = next(i)
                while t != self.esc_end:
                    raw.append(t)
                    t = next(i)
            except StopIteration:
                pass
            if len(raw):
                quoted.extend([re.escape(self.empty.join(raw))])
        return quoted

    def in_group(self, index):
        """Check if last index was in a char group."""

        inside = False
        for g in self.groups:
            if g[0] <= index <= g[1]:
                inside = True
                break
        return inside

    def apply(self):
        """Apply search template."""

        self.groups = self.find_char_groups(self.search)

        i = SearchTokens(self.search, self.verbose)
        iter(i)

        for t in i:
            if len(t) > 1:
                # handle our stuff

                c = t[1:]

                if c.startswith(self.uni_prop):
                    self.extended.extend(self.unicode_props(i, c[2:-1]))
                elif c == self.lc:
                    self.extended.extend(self.ascii_props(i, LOWER))
                elif c == self.lc_span:
                    self.extended.extend(self.ascii_props(i, UPPER))
                elif c == self.uc:
                    self.extended.extend(self.ascii_props(i, UPPER))
                elif c == self.uc_span:
                    self.extended.extend(self.ascii_props(i, LOWER))
                elif c[0:1] in self.verbose_tokens:
                    self.extended.append(t)
                elif c == self.quote:
                    self.extended.extend(self.quoted(i))
                elif c != self.end:
                    self.extended.append(t)
            elif self.verbose and t == self.hashtag and not self.in_group(i.index - 1):
                self.extended.append(t)
                self.extended.extend(self.comments(i))
            else:
                self.extended.append(t)

        return self.empty.join(self.extended)


# Template expander
class ReplaceTemplateExpander(object):

    """Backrefereces."""

    def __init__(self, match, template):
        """Initialize."""

        if template.binary:
            tokens = btokens
        else:
            tokens = utokens

        self.template = template
        self.empty = tokens[EMPTY]
        self.esc_end = tokens[ESC_END]
        self.end = tokens[END]
        self.lc = tokens[LC]
        self.lc_span = tokens[LC_SPAN]
        self.uc = tokens[UC]
        self.uc_span = tokens[UC_SPAN]
        self.index = -1
        self.end_found = False
        self.parent_span = []
        self._expand_string(match)

    def span_case(self, i, case):
        """Uppercase or lowercase the next range of characters until end marker is found."""

        attr = "lower" if case == LOWER else "upper"
        parts = []
        try:
            t = next(i)
            in_boundary = i.in_boundary()
            while t != self.esc_end or in_boundary:
                if in_boundary:
                    parts.append(getattr(t, attr)())
                elif len(t) > 1:
                    c = t[1:]
                    if c == self.uc:
                        self.parent_span.append(case)
                        parts.extend(self.single_case(i, UPPER))
                        self.parent_span.pop()
                    elif c == self.lc:
                        self.parent_span.append(case)
                        parts.extend(self.single_case(i, LOWER))
                        self.parent_span.pop()
                    elif c == self.uc_span:
                        self.parent_span.append(case)
                        parts.extend(self.span_case(i, UPPER))
                        self.parent_span.pop()
                    elif c == self.lc_span:
                        self.parent_span.append(case)
                        parts.extend(self.span_case(i, LOWER))
                        self.parent_span.pop()
                else:
                    parts.append(getattr(t, attr)())
                if self.end_found:
                    self.end_found = False
                    break
                t = next(i)
                in_boundary = i.in_boundary()
        except StopIteration:
            pass
        return parts

    def single_case(self, i, case):
        """Uppercase or lowercase the next character."""

        attr = "lower" if case == LOWER else "upper"
        parts = []
        try:
            t = next(i)
            in_boundary = i.in_boundary()
            if in_boundary:
                # Because this is a group the parent hasn't seen it yet,
                # we need to first pass over it with the parent's conversion first
                # then follow up with the single.
                if self.parent_span:
                    t = getattr(t, "lower" if self.parent_span[-1] else "upper")()
                parts.append(getattr(t[0:1], attr)() + t[1:])
            elif len(t) > 1:
                # Escaped char; just append.
                c = t[1:]
                chars = []
                if c == self.uc:
                    chars = self.single_case(i, UPPER)
                elif c == self.lc:
                    chars = self.single_case(i, LOWER)
                elif c == self.uc_span:
                    chars = self.span_case(i, UPPER)
                elif c == self.lc_span:
                    chars = self.span_case(i, LOWER)
                elif c == self.end:
                    self.end_found = True
                if chars:
                    chars[0] = getattr(chars[0][0:1], attr)() + chars[0][1:]
                    parts.extend(chars)
            else:
                parts.append(getattr(t, attr)())
        except StopIteration:
            pass
        return parts

    def _expand_string(self, match):
        """
        Using the template, expand the string.

        Keep track of the match group boundaries for later.
        """

        self.sep = match.string[:0]
        self.text = []
        self.group_boundaries = []
        # Expand string
        char_index = 0
        for x in range(0, len(self.template.literals)):
            index = x
            l = self.template.literals[x]
            if l is None:
                g_index = self.template.get_group_index(index)
                l = match.group(g_index)
                start = char_index
                char_index += len(l)
                self.group_boundaries.append((start, char_index))
                self.text.append(l)
            else:
                start = char_index
                char_index += len(l)
                self.text.append(l)

    def expand(self):
        """
        Expand with backreferences.

        Walk the expanded template string and process
        the new added backreferences and apply the associated
        action.
        """

        # Handle backreferences
        i = ReplaceTokens(self.sep.join(self.text), self.group_boundaries)
        iter(i)
        result = []
        for t in i:
            in_boundary = i.in_boundary()

            # Backreference has been found
            # This is for the neutral state
            # (currently applying no title cases)

            if in_boundary:
                result.append(t)
            elif len(t) > 1:
                c = t[1:]
                if c == self.lc:
                    result.extend(self.single_case(i, LOWER))
                elif c == self.lc_span:
                    result.extend(self.span_case(i, LOWER))
                elif c == self.uc:
                    result.extend(self.single_case(i, UPPER))
                elif c == self.uc_span:
                    result.extend(self.span_case(i, UPPER))
                elif c == self.end:
                    # This is here just as a reminder that \E is ignored
                    pass
            else:
                result.append(t)

            # Handle extraneous end
            if self.end_found:
                self.end_found = False

        return self.sep.join(result)


def _expand(m, template=None):
    """Expand with either the ReplaceTemplate or the user function, else return nothing."""

    if template is not None:
        if isinstance(template, ReplaceTemplate):
            return ReplaceTemplateExpander(m, template).expand()
        elif hasattr(template, '__call__'):
            return template(m)


def compile_search(pattern, flags=0):
    """Compile with extended search references."""

    verbose = re.VERBOSE & flags
    temp = SearchTemplate(pattern, verbose).apply()
    return re.compile(temp, flags)


def compile_replace(pattern, repl):
    """Construct a method that can be used as a replace method for sub, subn, etc."""

    call = None
    if pattern is not None:
        if hasattr(repl, '__call__'):
            call = functools.partial(_expand, template=repl)
        else:
            template = ReplaceTemplate(pattern, repl)
            call = functools.partial(_expand, template=template)
    return _expand if call is None else call
