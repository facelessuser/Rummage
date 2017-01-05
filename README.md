[![Unix Build Status][travis-image]][travis-link]
[![Code Health][landscape-image]][landscape-link]
[![Coverage][codecov-image]][codecov-link]
[![Requirements Status][requires-image]][requires-link]
![License][license-image]
Rummage
=======

Rummage is a cross platform tool for crawling directories and searching and replacing in text files.  It is written in Python and uses wxPython for the GUI.  Rummage allows for literal or regex searches and has configurations for limiting the files that are searched.

Rummage was inspired by the tool I use in windows called [grepWin](http://stefanstools.sourceforge.net/grepWin.html).  I wanted a similar tool in OSX and Linux, but I found none that I liked...so I wrote Rummage.  The look and feel is obviously loosely based off of GrepWin.  It is written in Python; therefore, it will be slower on searches than it would be if the searching were written in C.  If you specify an encoding when searching large projects, it should perform quite reasonably as it won't have to guess the encoding of files. On small projects, encoding guessing isn't too bad, but chardet (which is what Rummage uses to guess encoding), just is not the fastest. Though I still use grepWin on Windows, Rummage can come in handy as it you can use the fantastic **regex** search engine and do interesting things like fuzzy searching which grepWin cannot do.  Rummage can also dump its results to either CSV or HTML which is sometimes nice as well.

## Screenshots

![Rummage Search](./docs/images/search_tab.png)

![Rummage Files](./docs/images/files_tab.png)

![Rummage Content](./docs/images/content_tab.png)

# Documentation
http://facelessuser.github.io/Rummage/

License
=======

Rummage is released under the MIT license.

Copyright (c) 2013 - 2017 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

[travis-image]: https://img.shields.io/travis/facelessuser/Rummage/master.svg?label=Unix%20Build
[travis-link]: https://travis-ci.org/facelessuser/Rummage
[license-image]: https://img.shields.io/badge/license-MIT-blue.svg
[landscape-image]: https://landscape.io/github/facelessuser/Rummage/master/landscape.svg?style=flat
[landscape-link]: https://landscape.io/github/facelessuser/Rummage/master
[codecov-image]: https://img.shields.io/codecov/c/github/facelessuser/Rummage/master.svg
[codecov-link]: http://codecov.io/github/facelessuser/Rummage?branch=master
[requires-image]: https://img.shields.io/requires/github/facelessuser/Rummage/master.svg
[requires-link]: https://requires.io/github/facelessuser/Rummage/requirements/?branch=master
