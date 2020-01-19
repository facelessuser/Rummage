[![Gitter][gitter-image]][gitter-link]
[![Build][github-ci-image]][github-ci-link]
[![Unix Build Status][travis-image]][travis-link]
[![Windows Build Status][appveyor-image]][appveyor-link]
[![Coverage][codecov-image]][codecov-link]
[![PyPI Version][pypi-image]][pypi-link]
[![PyPI - Python Version][python-image]][pypi-link]
![License][license-image-mit]

Rummage
=======

Rummage is a cross platform search and replace tool. Rummage crawls directories and searches for specified patterns (either regular expression or literal) and can optionally replace those targets with desired text.

Rummage is written in Python and is currently available on Python 3.4+ (some older releases are available for Python 2.7). Rummage by default uses Python's Re regular expression engine, but you can also use the fantastic, feature rich [Regex](https://pypi.python.org/pypi/regex) search engine and do interesting things like fuzzy searching and more.

## Screenshots

![Rummage Search](https://github.com/facelessuser/Rummage/raw/master/docs/src/markdown/images/search_tab.png)

![Rummage Files](https://github.com/facelessuser/Rummage/raw/master/docs/src/markdown/images/files_tab.png)

![Rummage Content](https://github.com/facelessuser/Rummage/raw/master/docs/src/markdown/images/content_tab.png)

# Documentation

https://facelessuser.github.io/Rummage/

License
=======

Rummage is released under the MIT license.

Copyright (c) 2013 - 2020 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

[github-ci-image]: https://github.com/facelessuser/Rummage/workflows/build/badge.svg
[github-ci-link]: https://github.com/facelessuser/Rummage/actions?workflow=build
[travis-image]: https://img.shields.io/travis/facelessuser/Rummage/master.svg?label=travis&logo=travis%20ci&logoColor=cccccc
[travis-link]: https://travis-ci.org/facelessuser/Rummage
[appveyor-image]: https://img.shields.io/appveyor/ci/facelessuser/Rummage/master.svg?label=appveyor&logo=appveyor&logoColor=cccccc
[appveyor-link]: https://ci.appveyor.com/project/facelessuser/Rummage
[license-image]: https://img.shields.io/badge/license-MIT-blue.svg
[codecov-image]: https://img.shields.io/codecov/c/github/facelessuser/Rummage/master.svg?logo=codecov&logoColor=cccccc
[codecov-link]: http://codecov.io/github/facelessuser/Rummage?branch=master
[gitter-image]: https://img.shields.io/gitter/room/facelessuser/Rummage.svg?logo=gitter&color=fuchsia&logoColor=cccccc
[gitter-link]: https://gitter.im/facelessuser/Rummage
[pypi-image]: https://img.shields.io/pypi/v/Rummage.svg?logo=pypi&logoColor=cccccc
[pypi-link]: https://pypi.python.org/pypi/Rummage
[python-image]: https://img.shields.io/pypi/pyversions/Rummage?logo=python&logoColor=cccccc
[license-image-mit]: https://img.shields.io/badge/license-MIT-blue.svg
