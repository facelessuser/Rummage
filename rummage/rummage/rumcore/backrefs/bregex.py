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
