[![Unix Build Status][travis-image]][travis-link]
[![Code Health][landscape-image]][landscape-link]
[![Coverage][codecov-image]][codecov-link]
[![Requirements Status][requires-image]][requires-link]
![License][license-image]
Rummage
=======

Rummage is a GUI for grep like searches in python.  It was inspired by the tool I use in windows called GrepWin found here: http://stefanstools.sourceforge.net/grepWin.html.  I mainly used the tool for searches, and I wanted a similar tool in OSX...so I wrote Rummage.  The feel is loosely based off of GrepWin, though currently it has no replace options (not sure if/when I will add replace).  It is written in Python; therefore, it will be slower on searches than it would be if the searching were written in C (maybe down the line).  The big reason I wrote this is so I can build a similar tool on both OSX, Windows, and/or Linux (though I haven't yet tested Linux).

Please see the [Wiki](https://github.com/facelessuser/Rummage/wiki/Rummage-Documentation) for documentation.

For help and support, or to see what is planned next, see the the [Issues](https://github.com/facelessuser/Rummage/issues?state=open) page.

## Note on Replacing
Rummage will back up a file when replacing in `<your file name>.rum-bak`.  If the copy fails, it shouldn't replace.  You can disable backups if you like, but know there are greater risks associated with this.  Replace should work without issues, but remember, this is free software, and things can go wrong.  If you disable backups, there is a greater risk if something goes wrong.  Even with backups, something *could* go wrong.  I am not responsible for files corrupted or lost.  You have been warned.

Large files, really large files, can possibly cause an issue and may error out as, currently, the entire file will be read into memory for a replace.  Depending on your pattern on just searches, a lot can also be read into memory.  If you are doing really large files, know that it may error out or get really slow.  Remember this is done in Python, if you are doing massive GB files, maybe you are using the wrong tool for the job.

## Screenshots

<img src="http://dl.dropboxusercontent.com/u/342698/Rummage/rummage_osx.png" border="0">

License
=======

Rummage is released under the MIT license.

Copyright (c) 2013 Isaac Muse <isaacmuse@gmail.com>

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
