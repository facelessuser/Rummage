# Rummage {: .doctitle}
A Python search and replace tool.

---

## Overview
Rummage is a cross platform tool for crawling directories and searching and replacing in text files.  It is written in Python and uses wxPython for the GUI.  Rummage allows for literal or regex searches and has configurations for limiting the files that are searched.

Rummage was inspired by the tool I use in windows called [grepWin](http://stefanstools.sourceforge.net/grepWin.html).  I wanted a similar tool in OSX and Linux, but I found none that I liked...so I wrote Rummage.  The look and feel is obviously loosely based off of GrepWin.  It is written in Python; therefore, it will be slower on searches than it would be if the searching were written in C.  If you specify an encoding when searching large projects, it should perform quite reasonably as it won't have to guess the encoding of files. On small projects, encoding guessing isn't too bad, but chardet (which is what Rummage uses to guess encoding), just is not the fastest. Though I still use grepWin on Windows, Rummage can come in handy as it you can use the fantastic **regex** search engine and do interesting things like fuzzy searching which grepWin cannot do.  Rummage can also dump its results to either CSV or HTML which is sometimes nice as well.

![Search Tab](/images/search_tab.png)

![Files Tab](/images/files_tab.png)

![Content Tab](/images/content_tab.png)
