# Rummage

## Overview

Rummage is a cross platform search and replace tool written in Python. Rummage crawls directories and searches for specified patterns (either regular expression or literal) and can optionally replace those targets with desired text.

Rummage is written in Python and is currently available on Python 3.4+. Rummage by default uses the Python's Re regular expression engine, but you can also use the fantastic, feature rich [Regex](https://pypi.python.org/pypi/regex) search engine and do interesting things like fuzzy searching and more.

In general, it is usually preferable to specify an encoding for Rummage to use, but if you don't, Rummage will attempt encoding detection via the default, slower [Chardet](https://pypi.python.org/pypi/chardet) or the optional, faster [cChardet](https://pypi.python.org/pypi/cchardet/) depending on what is installed on your system (Chardet is installed by default with Rummage as it is pure Python). When replacing, it is usually recommended to specify the encoding to ensure the replace is done with the correct encoding.

![Search Tab](/images/search_tab.png)

![Files Tab](/images/files_tab.png)

![Content Tab](/images/content_tab.png)

--8<-- "links.md"
