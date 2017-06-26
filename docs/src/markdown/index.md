# Rummage

## Overview

Rummage is a cross platform search and replace tool for Python 2.7 and Python 3.4+. It crawls directories and searching for specified patterns and can optionally replace those targets with desired text. Rummage allows for literal or regular expression searches.

Rummage was inspired by the tool [grepWin][grepwin] and was created to provide a suitable GUI search and replace tool for macOS and Linux due to a lack of decent offerings available at the time, but is available on Windows, macOS, and Linux.

Rummage is written in Python; therefore, it will be slower on searches than it would be if the searching were written in C/C++. If you specify a file encoding when searching large projects, it should perform quite reasonably as it won't have to guess the encoding of files (which is the biggest bottleneck). On small projects, encoding guessing isn't too bad, but [Chardet][chardet] (which is what Rummage uses to guess encoding), is not the fastest as it is not written in C/C++ either.

Rummage by default uses the Python's Re regular expression engine, but you can also use the fantastic [Regex][regex] search engine and do interesting things like fuzzy searching.

![Search Tab](/images/search_tab.png)

![Files Tab](/images/files_tab.png)

![Content Tab](/images/content_tab.png)

--8<-- "links.md"
