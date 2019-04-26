# Installation

## Requirements

Rummage has a few requirements when installing.  These will all be taken care of when installing via `pip`.

Name                                        | Details
------------------------------------------- | -------
[`wxPython`\ 4.0.1+][wxpython]              | The new wxPython Phoenix 4.0.0 is required for the GUI.
[`backrefs`\ 4.0.2+][backrefs]              | Used to extend the `re` or `regex` regular expression engine with additional back references.
[`bracex` 1.1.1+][bracex]                   | Bash style brace expansion for file patterns.
[`wcmatch` 3.0.0+][wcmatch]                 | File name matching library.
[`chardet`\ 3.0.4+][chardet]                | Used for file encoding guessing when an encoding is not specified.
[`filelock`][filelock]                      | Used for file locking to allow different instances of Rummage to access the same file.
[`gntp`][gntp]                              | Used to send notifications to Growl via the the Growl Notification Transport Protocol for all platforms (macOS, Windows, and Linux).
[`send2trash`][send2trash]                  | Used for sending files to trash/recycle bin on each platform.
[`pymdown-extensions`][pymdown-extensions]  | An extension pack used in conjunction with [Python Markdown][markdown] to render some dynamic content into HTML that is embedded into the GUI.
[`pygments`][pygments]                      | Used to provide syntax highlighting in some of the dynamically generated HTML help.

Some optional modules that can be manually installed.

Name                   | Details
---------------------- | -------
[`regex`][regex]       | **regex** usage is completely optional, but it is included for those who wish to use it. Regex is a great regular expression engine that adds some nice features such as fuzzy searching, nested char sets, better Unicode support, and more.
[`cchardet`][cchardet] | `cchardet` is high speed universal character encoding detector. Much faster than the default `chardet`.

## Linux Prerequisites

Rummage requires wxPython in order to run. If you have a recent Linux distro that has a pre-built, installable wxPython package for your version of Python, then it may make sense to just install the pre-built package via your Linux package manager (`apt-get` for Ubuntu). The version must meet the version requirement above.

If you have installed a version of Python on your machine that does not have a pre-built wxPython package, or if your distro simply doesn't have a pre-built package that satisfies the requirements, then it may make sense to either install via `pip` or to manually compile and install. In both of these cases, you will have to install the appropriate prerequisites for your Linux distro. Rummage is generally tested on Ubuntu, so instructions are generally most up to date for Ubuntu. Remember, wxPython is a separate project and our instructions may get out of sync, so please check wxPython's official documentation on prerequisites before installing. Particularly under [this section][wxpython-prereq].

Due to recent changes in PyPI, it is probably best to ensure you have at least version 10.0 or greater of `pip`.  Ubuntu provides a method for installing pip with `sudo apt-get install python3-pip`, but this usually installs an older version.  It is recommended to install `pip` with the command shown below (where `python3` is a call to the installed Python version of your choice):

```
curl https://bootstrap.pypa.io/get-pip.py | sudo python3
```

!!! info
    The latest wxPython Phoenix builds with GTK3 by default, so the example below will install GTK3 related dependencies. You can use GTK2 if you build wxPython manually.

Ubuntu
: 

    ```bash
    sudo apt-get install python3.6-dev dpkg-dev build-essential libwebkitgtk-dev libjpeg-dev libtiff-dev libsdl1.2-dev libgstreamer-plugins-base1.0-dev libnotify-dev freeglut3 freeglut3-dev libgtk-3-dev libwebkitgtk-3.0-dev
    ```

    Replace `python3.6-dev` with the Python version you are using.

Fedora 26
: 
    For Fedora 26, it has been reported that you need fewer dependencies to build wxPython; I have not personally confirmed this.

    ```bash
    sudo dnf install gcc-c++ wxGTK-devel gstreamer-devel webkitgtk-devel GConf2-devel gstreamer-plugins-base-devel
    ```

    If your Linux distribution has `gstreamer` 1.0 available (like the Fedora distro), you can install the dev packages for that instead of the 0.10 version.

After getting all the correct prerequisites, you should be able to install Rummage with `pip`, though it is recommended to try and install wxPython first via `pip install wxpython`.

If wxPython doesn't install properly, be sure to reference wxPython's documentation to see if there is something you are missing. Also, creating an issue over at wxPython's GitHub site for related wxPython install issues may get you help faster than creating them on the Rummage issue page, which is mainly meant for tracking Rummage specific issues, not wxPython install issues.

Be patient while installing wxPython as Linux must build wxPython while macOS and Windows do not. If installing with `pip`, you may be waiting a long time with no real indication of how far along the process is.  If `pip` doesn't work, you can look into building and installing manually.  If you find any of this information incorrect, please feel free to offer a pull request.

## macOS Prerequisites

On macOS, Rummage uses either pure Python modules, or modules that provide wheels. What this means is that no C code compilation is required to install Rummage; therefore, no prior steps are needed. But if you want to install `regex`, there will be some C code compilation performed by `pip` which will require Xcode to be installed.

1. Download Xcode from the Mac App Store.
2. Navigate to Xcode > Preferences > Downloads tab.
3. Click the button to install the Command Line Tools.
4. Open Terminal (Applications/Terminal) and run `xcode-select --install`. You will be prompted to install the Xcode Command Line Tools.

## Installation

Here are a couple of ways to install and upgrade. Keep in mind if you are a Linux user, you have some [prerequisites](#linux-prerequisites) to install before proceeding.

Install:

```bash
pip install rummage
```

Install with optional module. Upgrades of optional modules will have to be manually upgraded when needed as well as they are not tracked in Rummage's requirements.

```bash
pip install rummage regex cchardet
```

Upgrade:

```bash
pip install --upgrade rummage
```

## Installing in Virtual Environments (macOS)

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

## Installing in Homebrew (macOS)

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

## Installing in Anaconda

Anaconda can run Rummage fine from my testing on macOS.  The important thing to note is you must launch it with `pythonw -m rummage` on Windows and **not** `python -m rummage`. While this worked on macOS, results may vary on other systems.

--8<-- "links.txt"
