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
from . import backrefs as bre
import functools
try:
    import regex
    REGEX_SUPPORT = True
except Exception:
    REGEX_SUPPORT = False

if REGEX_SUPPORT:
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
