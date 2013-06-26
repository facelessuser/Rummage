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


def _strip_regex(pattern, text, preserve_lines):
    def remove_comments(group, preserve_lines=False):
        return ''.join([x[0] for x in re.compile(r"\r?\n", re.MULTILINE).findall(group)]) if preserve_lines else ''

    return (
        ''.join(
            map(
                lambda m: m.group(2) if m.group(2) else remove_comments(m.group(1), preserve_lines),
                re.compile(pattern, re.MULTILINE | re.DOTALL).finditer(text)
            )
        )
    )


def _cpp(self, text, preserve_lines=False):
    return _strip_regex(
        r"""(/\*[^*]*\*+(?:[^/*][^*]*\*+)*/|\s*//(?:[^\r\n])*)|("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|.[^/"']*)""",
        text,
        preserve_lines
    )


def _python(self, text, preserve_lines=False):
    return _strip_regex(
        r"""(\s*#(?:[^\r\n])*)|("{3}(?:\\.|[^\\])*"{3}|'{3}(?:\\.|[^\\])*'{3}|"(?:\\.|[^"\\])*"|'(?:\\.|[^'])*'|.[^#"']*)""",
        text,
        preserve_lines
    )


class CommentException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Comments(object):
    styles = []

    def __init__(self, style=None, preserve_lines=False):
        self.preserve_lines = preserve_lines
        self.call = self.__get_style(style)

    @classmethod
    def add_style(cls, style, fn):
        if not style in cls.__dict__:
            setattr(cls, style, fn)
            cls.styles.append(style)

    def __get_style(self, style):
        if style in self.styles:
            return getattr(self, style)
        else:
            raise CommentException(style)

    def strip(self, text):
        return self.call(text, self.preserve_lines)

Comments.add_style("c", _cpp)
Comments.add_style("json", _cpp)
Comments.add_style("cpp", _cpp)
Comments.add_style("python", _python)