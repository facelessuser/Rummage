Rummage
=======

Rummage is a GUI for grep like searches in python.  It was inspired by the tool I use in windows called GrepWin found here: http://stefanstools.sourceforge.net/grepWin.html.  I mainly used the tool for searches, and I wanted a similar tool in OSX...so I wrote Rummage.  The feel is loosely based off of GrepWin, though currently it has no replace options (not sure if/when I will add replace).  It is written in Python; therefore, it will be slower on searches than it would be if the searching were written in C (maybe down the line).  The big reason I wrote this is so I can build a similar tool on both OSX, Windows, and/or Linux (though I haven't yet tested Linux).

The regex used is based off of the Python regex engine `re` (http://docs.python.org/2/library/re.html), with a wrapper that also allows you to do some unicode stuff like this `[\p{Ll}\p{Lu}]` and '\p{Ll}\p{Lu}`.  So keep this in mind if not all regex you know is recognized (but most functional regex should).

Screenshots
=======

<img src="http://dl.dropboxusercontent.com/u/342698/Rummage/rummage_osx.png" border="0">

Usage
=======

Rummage is pretty easy to use:

- select your directory to search (you can also enter a file name):
- configure search options and search limiting options
- press search

You can search in regex or literal.

"Files which match" and "Exclude dirs" settings can be configured with regex or wildcard searches. When using wildcard searches, you can add entries that are separated with `|` to have multiple entires. You can add wildcard entries that start with `-` to do the opposite: `*.*|-*.txt` would search all files, but exclude txt files.

Rummage will keep a history of your last congiuration between sessions.  It will also keep a history of the last 20 configurations of search, file search, etc.

Rummage can generally search ASCII, UTF8, UTF16, Latin-1, and it will search for ASCII strings in binary files if binary file option is enabled.  It really doesn't use an encoding detection right now since detecting the encoding is kind of slow in Python.  It just loops through the aforementioned encodings trying to open the files in different encodings (which turned out to be the fastet so far in Python).

Rummage has the ability to save and load commonly used regex.  It also has a simple regex tester to help you sort out complicated regex.

It displays results in two ways:

- Files: Lists the files with matches and some of the file attributes.  Double clicking an entry will open the file at the first match instance in your editor (if you have configured Rummage to use your editor).
- Content: Lists the line numbers on which the match was found.  It also shows the content of said line.  Double clicking will open the match at the line in your editor (if you have configured Rummage to use your editor).


# Planned Enhancements
See Issues

# License

Rummage is released under the MIT license.

Copyright (c) 2013 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
