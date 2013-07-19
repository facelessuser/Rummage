'''
Comment Remover
Licensed under MIT
Copyright (c) 2011 Isaac Muse <isaacmuse@gmail.com>
https://gist.github.com/facelessuser/5750103

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import re

CPP_COMMENTS = re.compile(
    r"""(/\*[^*]*\*+(?:[^/*][^*]*\*+)*/|\s*//(?:[^\r\n])*)|("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|.[^/"']*)""",
    re.MULTILINE | re.DOTALL
)

PY_COMMENTS = re.compile(
    r"""(\s*#(?:[^\r\n])*)|("{3}(?:\\.|[^\\])*"{3}|'{3}(?:\\.|[^\\])*'{3}|"(?:\\.|[^"\\])*"|'(?:\\.|[^'])*'|.[^#"']*)""",
    re.MULTILINE | re.DOTALL
)

LINE_ENDING = re.compile(r"\r?\n", re.MULTILINE)


def _strip_regex(pattern, text, preserve_lines):
    """
    Strip the comments via regex
    """

    def remove_comments(group, preserve_lines=False):
        # Remove comments, and optionally leave the line endings
        return ''.join([x[0] for x in LINE_ENDING.findall(group)]) if preserve_lines else ''

    return (
        ''.join(
            map(
                lambda m: m.group(2) if m.group(2) else remove_comments(m.group(1), preserve_lines),
                pattern.finditer(text)
            )
        )
    )


def _cpp(self, text, preserve_lines=False):
    """
    CPP comments regex
    """

    return _strip_regex(CPP_COMMENTS, text, preserve_lines)


def _python(self, text, preserve_lines=False):
    """
    Python comments regex
    """

    return _strip_regex(PY_COMMENTS, text, preserve_lines)


class CommentException(Exception):
    def __init__(self, value):
        """
        Init exception
        """

        self.value = value

    def __str__(self):
        """
        Exception string
        """

        return repr(self.value)


class Comments(object):
    styles = []

    def __init__(self, style=None, preserve_lines=False):
        """
        Init Comments object
        """

        self.preserve_lines = preserve_lines
        self.call = self.__get_style(style)

    @classmethod
    def add_style(cls, style, fn):
        """
        Add comment style
        """

        if not style in cls.__dict__:
            setattr(cls, style, fn)
            cls.styles.append(style)

    def __get_style(self, style):
        """
        Get comment styel
        """

        if style in self.styles:
            return getattr(self, style)
        else:
            raise CommentException(style)

    def strip(self, text):
        """
        Execute comment stripping call
        """

        return self.call(text, self.preserve_lines)


# Supported aliases for comment stripping
Comments.add_style("c", _cpp)
Comments.add_style("json", _cpp)
Comments.add_style("cpp", _cpp)
Comments.add_style("python", _python)
