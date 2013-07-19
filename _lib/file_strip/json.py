'''
Json Comments
Licensed under MIT
Copyright (c) 2011 Isaac Muse <isaacmuse@gmail.com>
https://gist.github.com/facelessuser/5750103

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import re
from comments import Comments

DANGLING_COMMAS = re.compile(
    r"""((,([\s\r\n]*)(\]))|(,([\s\r\n]*)(\})))|("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|.[^,"']*)""",
    re.MULTILINE | re.DOTALL
)


def strip_dangling_commas(text, preserve_lines=False):
    """
    Strip dangling commas from JSON (they will kill the parsing)
    """

    def remove_comma(m, preserve_lines=False):
        """
        Remove the commas
        """

        if preserve_lines:
            # ,] -> ] else ,} -> }
            return m.group(3) + m.group(4) if m.group(2) else m.group(6) + m.group(7)
        else:
            # ,] -> ] else ,} -> }
            return m.group(4) if m.group(2) else m.group(7)

    return (
        ''.join(
            map(
                lambda m: m.group(8) if m.group(8) else remove_comma(m, preserve_lines),
                DANGLING_COMMAS.finditer(text)
            )
        )
    )


def strip_comments(text, preserve_lines=False):
    """
    Strip JSON comments
    """

    return Comments('json', preserve_lines).strip(text)


def sanitize_json(text, preserve_lines=False):
    """
    Strip dangling commas and C-style comments
    """

    return strip_dangling_commas(Comments('json', preserve_lines).strip(text), preserve_lines)
