# Installation

## Requirements

Rummage has a few requirements when installing.  These will all be taken care of when installing via `pip`.

Name                             | Details
-------------------------------- | -------
[`backrefs` 1.0.1+][backrefs]    | Used to extend the `re` or `regex` regular expression engine with additional back references.
[`gntp`][gntp]                   | Used to send notifications to Growl via the the Growl Notification Transport Protocol for all platforms (macOS, Windows, and Linux).
[`chardet`\ 3.0.4+][chardet]     | Used for file encoding guessing when an encoding is not specified.
[`wxPython`\ 4.0.0a3+][wxpython] | The new wxPython 4.0.0 is required for for Rummage to run in Python 2 and Python 3. Classic wxPython support has unfortunately be dropped.
[`regex`\ 2015.07.19+][regex]    | **regex** is usage is completely optional, but it is included for those who wish to use it. Regex is a great regular expression engine that adds some nice features such as fuzzy searching, nested char sets, better Unicode support, and more.

!!! warning "Linux Prerequisites"
    In traditional Linux fashion, there is a little extra work that needs to be done prior to installing.  Linux requires some prerequisites so that it can build wxPython during installation.

    Example is for Ubuntu:

    ```bash
    sudo apt-get install dpkg-dev build-essential python2.7-dev libwebkitgtk-dev libjpeg-dev libtiff-dev libgtk2.0-dev libsdl1.2-dev libgstreamer-plugins-base0.10-dev libnotify-dev freeglut3 freeglut3-dev
    ```

    Replace `python2.7-dev` with the Python version you are using.

    If your Linux distribution has `gstreamer` 1.0 available, you can install the dev packages for that instead of the 0.10 version.

    Be patient while installing on Linux as Linux must build wxPython while macOS and Windows do not.

    Check out the wxPython document to see if prerequisites have changed: https://github.com/wxWidgets/Phoenix/blob/master/README.rst#prerequisites.

## Installation

Here are a couple of ways to install and upgrade. Keep in mind if you are a Linux user, you have some prerequisites to install before proceeding: see [Requirements](#requirements).

1. Install: `#!bash python pip install rummage`.

2. To upgrade: `#!bash python install --upgrade rummage`.

3. If developing on Rummage, you can clone the project, and install the requirements with the following command:

    ```bash
    pip install -r requirements/project.txt`
    ```

    You can then run the command below. This method will allow you to instantly see your changes between iterations without reinstalling which is great for developing.  If you want to do this in a virtual machine, you can as well.  Like the first method, you should then be able to access Rummage from the command line via `rummage` or `rummage --path mydirectory`.

    ```bash
    pip install --editable .
    ```

    You could also just optionally run the package locally, skipping the actual install of Rummage. You can run the project by issuing the following command from the root folder:

    ```
    python -m rummage
    ```

    In general, you may find it more appropriate to use the `pythonw` command instead of `python`.  In some environments, it may be required (see ["Running in Anaconda (macOS)"](#running-in-anaconda-macos)).

## Running in Virtual Environments (macOS)

If installing in a virtual environment via `virtualenv`, you may run into the following error:


This used to be a fairly annoying issue to workaround, but in wxPython 4+, it's not too bad.  The wxPython wiki is a bit out of date.  You don't have to symlink `wx.pth` or anything like that anymore as the design of wxPython is a bit different now.  All you have to do is place the script below in `my_virtual_env/bin`.  In this example I call it `fwpy` for "framework python" (make sure to adjust paths or Python versions to match your installation).

```
#!/bin/bash

# what real Python executable to use
PYVER=2.7
PYTHON=/Library/Frameworks/Python.framework/Versions/$PYVER/bin/python$PYVER

# find the root of the virtualenv, it should be the parent of the dir this script is in
ENV=`$PYTHON -c "import os; print os.path.abspath(os.path.join(os.path.dirname(\"$0\"), '..'))"`
echo $ENV

# now run Python with the virtualenv set as Python's HOME
export PYTHONHOME=$ENV
exec $PYTHON "$@"
```

## Running in Homebrew (macOS)

Homebrew from what I read used to have issues running wxPython in versions less than 4, but this doesn't seem to be an issue with wxPython 4 with Homebrew (at least in my testing).

```
Faceless-MacBook-Pro:~ facelessuser$ brew install python
...a lot of install stuff

Faceless-MacBook-Pro:~ facelessuser$ /usr/local/Cellar/python/2.7.13_1/bin/pip install rummage
Collecting rummage
  Using cached rummage-2.3-py2.py3-none-any.whl
Collecting regex (from rummage)
Collecting backrefs>=1.0.1 (from rummage)
Collecting gntp>=1.0.2 (from rummage)
  Using cached gntp-1.0.3-py2-none-any.whl
Collecting chardet>=3.0.4 (from rummage)
  Using cached chardet-3.0.4-py2.py3-none-any.whl
Collecting wxpython>=4.0.0a3 (from rummage)
  Using cached wxPython-4.0.0a3-cp27-cp27m-macosx_10_6_intel.whl
Collecting six (from wxpython>=4.0.0a3->rummage)
  Using cached six-1.10.0-py2.py3-none-any.whl
Installing collected packages: regex, backrefs, gntp, chardet, six, wxpython, rummage
Successfully installed backrefs-1.0.1 chardet-3.0.4 gntp-1.0.3 regex-2017.7.11 rummage-2.3 six-1.10.0 wxpython-4.0.0a3

Faceless-MacBook-Pro:~ facelessuser$ /usr/local/Cellar/python/2.7.13_1/bin/python2 -m rummage
```

## Running in Anaconda (macOS)

Anaconda can run Rummage fine from my testing.  The important thing to note is you must launch it with `pythonw -m rummage` and **not** `python -m rummage`.

--8<-- "links.md"
