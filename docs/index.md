# PyMdown {: .doctitle}
A Python Markdown Preview and Converter Tool
{: .doctitle-info}

---

!!! Danger "Under Construction"
    This documentation is currently under construction, and things are subject to change.

## Overview
PyMdown is a CLI tool to convert or even batch convert Markdown files to HTML.  It can also generate HTML previews of Markdown and auto-open them in a web browser. It allows for specifying simple HTML templates for the Markdown where you can include CSS and JavaScript.  PyMdown is built on top of [Python Markdown][py_md] and [Pygments][pygments].

---

<table markdown="1" class="doctable"><tbody><tr><td>
### [Basic Markdown Syntax](user-guide/markdown-syntax.md)
as laid out by [Mark Gruber][daringfireball]
</td><td>
### [Python Markdown Differences](https://pythonhosted.org/Markdown/#differences)
out of the box differences (no extensions)
</td></tr><tr><td>
### [PyMdown Extensions](user-guide/pymdown-extensions.md)
extensions made specifically for PyMdown
</td><td>
### [Python Markdown Extensions][py_md_extensions]
extensions that come with Python Markdown
</td></tr><tr><td>
###[PyMdown Usage](user-guide/general-usage.md)
how to use the PyMdown application
</td><td>
### [PyMdown Build/Installation](user-guide/installation.md)
how to build and install PyMdown
</td></tr><tr><td>
### [Sublime Plugin](https://github.com/facelessuser/sublime-pymdown)
plugin for Sublime Text 3
</td><td>
### [Custom Lexers and Styles](user-guide/pygments-customization.md)
how to include custom lexers and styes
</td></tr></tbody></table>

[daringfireball]: http://daringfireball.net/
[py_md_extensions]: https://pythonhosted.org/Markdown/extensions/
[py_md]: https://pythonhosted.org/Markdown/
[pygments]: http://pygments.org/
