# Installation {: .doctitle}
Installing Rummage.

---

## Overview
Rummage has a few requirements when installing.  If installing (and not running the scripts directly), the requirements will be installed automatically except for a few that are optional.  See [Requirements](#requirements) for more info.

## Requirements
In order for PyMdown to work, there are a couple of prerequisites.  **wxPython** is optional as it may only be desired to use the experimental CLI or the API; neither require wxPython. **regex** is also optional as rummage will use **re** by default.

| Name | Required |Details |
|------|----------|--------|
| [backrefs](https://github.com/facelessuser/backrefs) | Yes | Used to extend the `re` or `regex` regular expression engine with additional back references. |
| [gntp](https://github.com/kdfm/gntp) | Yes | Used to send notifications to Growl via the the Growl Notification Transport Protocol for all platforms (OSX, Windows, and Linux). |
| [Chardet](https://github.com/chardet/chardet) | Yes | Used for file encoding guessing when an encoding is not specified. |
| [wxPython 3.0.0+](http://www.wxpython.org/) | GUI only | Older versions may work, but I am arbitrarily specifying 3.0.0.  2.9.4 used to be used and might still work, but I only test on 3.0.0 moving forward.  This is only needed if you want to use the GUI tool.  The experimental CLI doesn't need it, nor does the rumcore API. |
| [regex 2015.07.19+](https://pypi.python.org/pypi/regex) | No | **regex** is completely optional. It is a great engine that adds some nice features such as fuzzy searching, nested char sets, better unicode support, and more.  I have mentioned `2015.07.19` as the preferred minimum version.  You are welcome to use earlier, but you may experience issues.  One particular bug was fixed in `2015.07.19` that had caused some minor issues. |

## Installation
There are two recommended ways to install rummage.

1. Install via `#!bash python setup.py build` and `#!bash python setup.py install`.  You should then be able to access Rummage from the command line via `rummage` or `rummage --path mydirectory`.  You can also access the experimental CLI `rumcl <args>` as well.

2. If developing on rummage, you can install via `#!bash pip install --editable .`.  This method will allow you to instantly see your changes without reinstalling which is great for developing.  If you want to do this in a virtual machine, you can.  Like the first method, you should then be able to access Rummage from the command line via `rummage` or `rummage --path mydirectory`.  You can also access the experimental CLI `rumcl <args>` as well.
