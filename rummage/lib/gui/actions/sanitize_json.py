"""
Sanitize JSON.

Licensed under MIT
Copyright (c) 2012 - 2019 Isaac Muse <isaacmuse@gmail.com>
"""
import re

__all__ = ('sanitize',)

LINE_PRESERVE = re.compile(r"\r?\n", re.MULTILINE)
JSON_COMMENTS_PATTERN = re.compile(
    r'''(?x)
        (?P<comments>
            /\*[^*]*\*+(?:[^/*][^*]*\*+)*/  # multi-line comments
          | \s*//(?:[^\r\n])*               # single line comments
        )
      | (?P<code>
            "(?:\\.|[^"\\])*"               # double quotes
          | .[^/"]*                         # everything else
        )
    ''',
    re.DOTALL
)

JSON_COMMA_PATTERN = re.compile(
    r'''(?x)
        (
            (?P<square_comma>
                ,                        # trailing comma
                (?P<square_ws>[\s\r\n]*) # white space
                (?P<square_bracket>\])   # bracket
            )
          | (?P<curly_comma>
                ,                        # trailing comma
                (?P<curly_ws>[\s\r\n]*)  # white space
                (?P<curly_bracket>\})    # bracket
            )
        )
      | (?P<code>
            "(?:\\.|[^"\\])*"            # double quoted string
          | .[^," ]*                     # everything else
        )
    ''',
    re.DOTALL
)


def _strip_comments(text, preserve_lines=False):
    """Generic function that strips out comments passed on the given pattern."""

    regex = JSON_COMMENTS_PATTERN

    def remove_comments(group, preserve_lines=False):
        """Remove comments."""

        return ''.join([x[0] for x in LINE_PRESERVE.findall(group)]) if preserve_lines else ''

    def evaluate(m, preserve_lines):
        """Search for comments."""

        g = m.groupdict()
        return g["code"] if g["code"] is not None else remove_comments(g["comments"], preserve_lines)

    return ''.join(map(lambda m: evaluate(m, preserve_lines), regex.finditer(text)))


def _strip_dangling_commas(text, preserve_lines=False):
    """Strip dangling commas."""

    regex = JSON_COMMA_PATTERN

    def remove_comma(g, preserve_lines):
        """Remove comma."""

        if preserve_lines:
            # ,] -> ] else ,} -> }
            if g["square_comma"] is not None:
                return g["square_ws"] + g["square_bracket"]
            else:
                return g["curly_ws"] + g["curly_bracket"]
        else:
            # ,] -> ] else ,} -> }
            return g["square_bracket"] if g["square_comma"] else g["curly_bracket"]

    def evaluate(m, preserve_lines):
        """Search for dangling comma."""

        g = m.groupdict()
        return remove_comma(g, preserve_lines) if g["code"] is None else g["code"]

    return ''.join(map(lambda m: evaluate(m, preserve_lines), regex.finditer(text)))


def sanitize(text, preserve_lines=False):
    """Sanitize the JSON file by removing comments and dangling commas."""

    return _strip_dangling_commas(_strip_comments(text, preserve_lines), preserve_lines)
