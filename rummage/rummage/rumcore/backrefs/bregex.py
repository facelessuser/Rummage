r"""
Backrefs for the 'regex' module.

Only extends the replace if a compiled replace is used.

    * \c and \C...\E - Uppercase char or chars (replace)
    * \l and \L...\E - Lowercase char or chars (replace)

Compiling
=========
pattern = regex.compile(r'somepattern', flags)
replace = compile_replace(pattern, r'\1 some replace pattern')

Usage
=========
Recommended to use compiling.  Assuming the above compiling:

    text = pattern.sub(replace, 'sometext')

--or--

    m = pattern.match('sometext')
    if m:
        text = replace(m)  # similar to m.expand(template)

Licensed under MIT
Copyright (c) 2011 - 2015 Isaac Muse <isaacmuse@gmail.com>
"""
from __future__ import unicode_literals
import re
from . import bre
import functools
try:
    import regex
    REGEX_SUPPORT = True
except Exception:
    REGEX_SUPPORT = False

if REGEX_SUPPORT:
    # Expose some common re flags and methods to
    # save having to import re and backrefs libs
    D = regex.D
    DEBUG = regex.DEBUG
    A = regex.A
    ASCII = regex.ASCII
    B = regex.B
    BESTMATCH = regex.BESTMATCH
    E = regex.E
    ENHANCEMATCH = regex.ENHANCEMATCH
    F = regex.F
    FULLCASE = regex.FULLCASE
    I = regex.I
    IGNORECASE = regex.IGNORECASE
    L = regex.L
    LOCALE = regex.LOCALE
    M = regex.M
    MULTILINE = regex.MULTILINE
    R = regex.R
    REVERSE = regex.REVERSE
    S = regex.S
    DOTALL = regex.DOTALL
    U = regex.U
    UNICODE = regex.UNICODE
    X = regex.X
    VERBOSE = regex.VERBOSE
    V0 = regex.V0
    VERSION0 = regex.VERSION0
    V1 = regex.V1
    VERSION1 = regex.VERSION1
    W = regex.W
    WORD = regex.WORD
    escape = regex.escape
    purge = regex.purge
    REGEX_TYPE = type(regex.compile('', 0))

    _REGEX_FLAGS = 0
    _REGEX_SEARCH_REF = 1
    _REGEX_SEARCH_REF_VERBOSE = 2
    _V0 = 3
    _V1 = 4

    utokens = [
        re.compile(                       # _RE_FLAGS
            r'(?s)(\\.)|\(\?((?:[Laberux]|V0|V1|-?[imsfw])+)[):]|(.)'
        ),
        re.compile(                       # _REGEX_SEARCH_REF
            r'''(?x)
            (\\)+
            (
                [(EQ]
            )? |
            (
                [(EQ]
            )
            '''
        ),
        re.compile(                       # _REGEX_SEARCH_REF_VERBOSE
            r'''(?x)
            (\\)+
            (
                [(EQ#]
            )? |
            (
                [(EQ#]
            )
            '''
        ),
        'V0',                             # _V0
        'V1'                              # _V1
    ]

    btokens = [
        re.compile(                       # _RE_FLAGS
            br'(?s)(\\.)|\(\?((?:[Laberux]|V0|V1|-?[imsfw])+)[):]|(.)'
        ),
        re.compile(                       # _REGEX_SEARCH_REF
            br'''(?x)
            (\\)+
            (
                [EQ]
            )? |
            (
                [EQ]
            )
            '''
        ),
        re.compile(                       # _REGEX_SEARCH_REF_VERBOSE
            br'''(?x)
            (\\)+
            (
                [EQ#]
            )? |
            (
                [EQ#]
            )
            '''
        ),
        b'V0',                            # _V0
        b'V1'                             # _V1
    ]

    class RegexSearchTokens(bre.Tokens):

        """Tokens."""

        def __init__(self, string, verbose):
            """Initialize."""

            if isinstance(bre.string, bre.binary_type):
                tokens = bre.btokens
                local_tokens = btokens
            else:
                tokens = bre.utokens
                local_tokens = utokens

            self.string = string
            if verbose:
                self._re_search_ref = local_tokens[_REGEX_SEARCH_REF_VERBOSE]
            else:
                self._re_search_ref = local_tokens[_REGEX_SEARCH_REF]
            self._b_slash = tokens[bre._B_SLASH]
            self.max_index = len(string) - 1
            self.index = 0
            self.current = None

        def __iter__(self):
            """Iterate."""

            return self

        def iternext(self):
            """
            Iterate through characters of the string.

            Count escaped Q, E and backslash as a single char.
            """

            if self.index > self.max_index:
                raise StopIteration

            char = self.string[self.index:self.index + 1]
            if char == self._b_slash:
                m = self._re_search_ref.match(self.string[self.index + 1:])
                if m:
                    if m.group(1):
                        if m.group(2):
                            self.index += 1
                        else:
                            char += self._b_slash
                    else:
                        char += m.group(3)

            self.index += len(char)
            self.current = char
            return self.current

    class SearchTemplate(object):

        """Search Template."""

        def __init__(self, search, re_verbose=False, re_version=0):
            """Initialize."""

            if isinstance(bre.search, bre.binary_type):
                self.binary = True
                tokens = bre.btokens
                local_tokens = btokens
            else:
                self.binary = False
                tokens = bre.utokens
                local_tokens = utokens

            self._verbose_flag = tokens[bre._VERBOSE_FLAG]
            self._empty = tokens[bre._EMPTY]
            self._b_slash = tokens[bre._B_SLASH]
            self._ls_bracket = tokens[bre._LS_BRACKET]
            self._rs_bracket = tokens[bre._RS_BRACKET]
            self._esc_end = tokens[bre._ESC_END]
            self._end = tokens[bre._END]
            self._quote = tokens[bre._QUOTE]
            self._negate = tokens[bre._NEGATE]
            self._regex_flags = local_tokens[_REGEX_FLAGS]
            self._nl = tokens[bre._NL]
            self._hashtag = tokens[bre._HASHTAG]
            self._V0 = local_tokens[_V0]
            self._V1 = local_tokens[_V1]
            self.search = search
            if regex.DEFAULT_VERSION == V0:
                self.groups = self.find_char_groups_v0(search)
            else:
                self.groups = self.find_char_groups_v1(search)
            self.verbose, self.version = self.find_flags(search, re_verbose, re_version)
            if self.version != regex.DEFAULT_VERSION:
                if self.version == V0:
                    self.groups = self.find_char_groups_v0(search)
                else:
                    self.groups = self.find_char_groups_v1(search)
            if self.verbose:
                self._verbose_tokens = tokens[bre._VERBOSE_TOKENS]
            else:
                self._verbose_tokens = tuple()
            self.extended = []

        def find_flags(self, s, re_verbose, re_version):
            """Find verbose and unicode flags."""

            new = []
            start = 0
            verbose_flag = re_verbose
            version_flag = re_version
            if version_flag and verbose_flag:
                return bool(verbose_flag), version_flag
            for g in self.groups:
                new.append(s[start:g[0] + 1])
                start = g[1]
            new.append(s[start:])
            for m in self._regex_flags.finditer(self._empty.join(new)):
                if m.group(2):
                    if self._verbose_flag in m.group(2):
                        verbose_flag = True
                    if self._V0 in m.group(2):
                        version_flag = V0
                    elif self._V1 in m.group(2):
                        version_flag = V1
                if version_flag and verbose_flag:
                    break
            return bool(verbose_flag), version_flag if version_flag else regex.DEFAULT_VERSION

        def find_char_groups_v0(self, s):
            """Find character groups."""

            pos = 0
            groups = []
            escaped = False
            found = False
            first = None
            for c in bre.iterstring(s):
                if c == self._b_slash:
                    escaped = not escaped
                elif escaped:
                    escaped = False
                elif c == self._ls_bracket and not found:
                    found = True
                    first = pos
                elif c == self._negate and found and (pos == first + 1):
                    first = pos
                elif c == self._rs_bracket and found and (pos != first + 1):
                    groups.append((first, pos))
                    found = False
                pos += 1
            return groups

        def find_char_groups_v1(self, s):
            """Find character groups."""

            pos = 0
            groups = []
            escaped = False
            found = 0
            first = None
            sub_first = None
            for c in bre.iterstring(s):
                if c == self._b_slash:
                    # Next char is escaped
                    escaped = not escaped
                elif escaped:
                    # Escaped handled
                    escaped = False
                elif c == self._ls_bracket and not found:
                    # Start of first char set found
                    found += 1
                    first = pos
                elif c == self._ls_bracket and found:
                    # Start of sub char set found
                    found += 1
                    sub_first = pos
                elif c == self._negate and found == 1 and (pos == first + 1):
                    # Found ^ at start of first char set; adjust 1st char pos
                    first = pos
                elif c == self._negate and found > 1 and (pos == sub_first + 1):
                    # Found ^ at start of sub char set; adjust 1st char sub pos
                    sub_first = pos
                elif c == self._rs_bracket and found == 1 and (pos != first + 1):
                    # First char set closed; log range
                    groups.append((first, pos))
                    found = 0
                elif c == self._rs_bracket and found > 1 and (pos != sub_first + 1):
                    # Sub char set closed; decrement depth counter
                    found -= 1
                pos += 1
            return groups

        def comments(self, i):
            """Handle comments in verbose patterns."""

            parts = []
            try:
                t = next(i)
                while t != self._nl:
                    parts.append(t)
                    t = next(i)
                parts.append(self._nl)
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
                    while t != self._esc_end:
                        raw.append(t)
                        t = next(i)
                except StopIteration:
                    pass
                if len(raw):
                    quoted.extend([escape(self._empty.join(raw))])
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

            i = RegexSearchTokens(self.search, self.verbose)
            iter(i)

            for t in i:
                if len(t) > 1:
                    # handle our stuff

                    c = t[1:]

                    if c[0:1] in self._verbose_tokens:
                        self.extended.append(t)
                    elif c == self._quote:
                        self.extended.extend(self.quoted(i))
                    elif c != self._end:
                        self.extended.append(t)
                elif self.verbose and t == self._hashtag and not self.in_group(i.index - 1):
                    self.extended.append(t)
                    self.extended.extend(self.comments(i))
                else:
                    self.extended.append(t)

            return self._empty.join(self.extended)

    class RegexReplaceTemplate(bre.ReplaceTemplate):

        """Replace template for the regex module."""

        def parse_template(self, pattern):
            """Parse template for the regex module."""

            self.groups = []
            self.literals = regex._compile_replacement_helper(pattern, self._template)
            count = 0
            for part in self.literals:
                if isinstance(part, int):
                    self.literals[count] = None
                    self.groups.append((count, part))
                count += 1

    def _apply_replace_backrefs(m, repl=None):
        """Expand with either the RegexReplaceTemplate or the user function, compile on the fly, or return None."""

        if repl is not None:
            if hasattr(repl, '__call__'):
                return repl(m)
            elif isinstance(repl, RegexReplaceTemplate):
                return bre.ReplaceTemplateExpander(m, repl).expand()
            elif isinstance(repl, (bre.string_type, bre.binary_type)):
                return bre.ReplaceTemplateExpander(m, RegexReplaceTemplate(m.re, repl)).expand()

    def compile_replace(pattern, repl):
        """Construct a method that can be used as a replace method for sub, subn, etc."""

        call = None
        if pattern is not None:
            if not hasattr(repl, '__call__') and isinstance(pattern, REGEX_TYPE):
                repl = RegexReplaceTemplate(pattern, repl)
            call = functools.partial(_apply_replace_backrefs, repl=repl)
        return call

    compile_search = regex.compile

    # Convenience methods like re has, but slower due to overhead on each call.
    # It is recommended to use compile_search and compile_replace
    def expand(m, repl):
        """Expand the string using the replace pattern or function."""

        return _apply_replace_backrefs(m, repl)

    match = regex.match
    fullmatch = regex.fullmatch
    search = regex.search
    subf = regex.subf
    subfn = regex.subfn
    split = regex.split
    splititer = regex.splititer
    findall = regex.findall
    finditer = regex.finditer

    def sub(pattern, repl, string, count=0, flags=0, pos=None, endpos=None, concurrent=None, **kwargs):
        """Wrapper for sub."""

        pattern = regex.compile(pattern, flags)
        return regex.sub(
            pattern, compile_replace(pattern, repl), string, count, flags, pos, endpos, concurrent, **kwargs
        )

    def subn(pattern, repl, string, count=0, flags=0, pos=None, endpos=None, concurrent=None, **kwargs):
        """Wrapper for subn."""

        pattern = regex.compile(pattern, flags)
        return regex.subn(
            pattern, compile_replace(pattern, repl), string, count, flags, pos, endpos, concurrent, **kwargs
        )
