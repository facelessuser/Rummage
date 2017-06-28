# Rummage

## Overview

Rummage is a cross platform search and replace tool written in Python. Rummage crawls directories and searches for specified patterns (either regular expression or literal) and can optionally replace those targets with desired text.

Rummage was inspired by the Windows tool [grepWin][grepwin]. At the time, it was difficult to find a decent GUI search and replace tool macOS and Linux. Rummage was created to fill that void and is available on Linux, macOS, and Windows.

Rummage is written in Python and is currently available on Python 2.7 and Python 3.4+. Rummage by default uses the Python's Re regular expression engine, but you can also use the fantastic, feature rich [Regex][regex] search engine and do interesting things like fuzzy searching and more.

When specifying a specific file encoding, Rummage is quick enough to search large projects easily. Optionally you can let Rummage detect encoding, but because the encoding detection is done by the pure Python package [Chardet][chardet], it will run significantly slower. Encoding detection is the biggest bottleneck. This shouldn't be a problem in small projects, but it will become quite noticeable in large projects.

![Search Tab](/images/search_tab.png)

![Files Tab](/images/files_tab.png)

![Content Tab](/images/content_tab.png)

--8<-- "links.md"
