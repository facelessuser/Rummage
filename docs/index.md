# Rummage {: .doctitle}
A Python search and replace tool.

---

!!! caution "Under Construction"
    Documentation is currently under construction for the 1.0.0 release.  Things could change.

## Overview
Rummage is a cross platform tool for crawling directories and searching and replacing in text files.  It is written in Python and using wxPython for the GUI.  Rummage allows for literal or regex searches and has configurations for limiting the files that are searched.

Rummage also has a documented API for accessing the core library for custom search and replace scripts.  You can even write your own custom GUI around the core.

Rummage was inspired by the tool I use in windows called [grepWin](http://stefanstools.sourceforge.net/grepWin.html).  I wanted a similar tool in OSX and Linux, but I found none that I liked...so I wrote Rummage.  The feel is loosely based off of GrepWin.  It is written in Python; therefore, it will be slower on searches than it would be if the searching were written in C.  If you specify an encoding when searching large projects, it should perform quite reasonably as it won't have to guess the encoding of files. On small projects, encoding guessing isn't too bad.  Though I still use grepWin on Windows, Rummage can come in handy by doing things such as fuzzy searching (when using the python **regex** engine) which grepWin cannot do.  It can also dump its results to either CSV or HTML which is sometimes nice.

![Search Tab](./images/search_tab.png)

![Files Tab](./images/files_tab.png)

![Content Tab](./images/content_tab.png)
