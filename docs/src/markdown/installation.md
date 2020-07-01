# Installation

## Requirements

Rummage, when installed via pip, will install all of your required dependencies, but there are a few optional
dependencies. If desired, you can install these dependencies manually, or install them automatically with `pip` (will
be covered later).

Name                   | Details
---------------------- | -------
[`regex`][regex]       | Regex is a great regular expression engine that adds some nice features such as fuzzy searching, nested char sets, better Unicode support, and more.
[`cchardet`][cchardet] | `cchardet` is high speed universal character encoding detector. Much faster than the default `chardet`.

## Linux Prerequisites

Rummage requires wxPython in order to run. If you have a recent Linux distro that has a pre-built, installable wxPython
package for your version of Python, then it may make sense to just install the pre-built package via your Linux package
manager (`apt-get` for Ubuntu). The version must meet the version requirements which is currently wxPython 4.1+.

If you have installed a version of Python on your machine that does not have a pre-built wxPython package, or if your
distro simply doesn't have a pre-built package that satisfies the requirements, then it may make sense to either install
via `pip` or to manually compile and install. In both of these cases, you will have to install the appropriate
prerequisites for your Linux distro. Rummage is generally tested on Ubuntu, so instructions are generally most up to
date for Ubuntu. Remember, wxPython is a separate project and our instructions may get out of sync, so please check
wxPython's official documentation on prerequisites before installing. Particularly under
[this section][wxpython-prereq].

Ubuntu provides a method for installing pip with `sudo apt-get install python3-pip`, but this usually installs an older
version.  It is recommended to install `pip` with the command shown below (where `python3` is a call to the installed
Python version of your choice):

```
curl https://bootstrap.pypa.io/get-pip.py | sudo python3
```

!!! info
    The latest wxPython Phoenix builds with GTK3 by default, so the example below will install GTK3 related
    dependencies. You can use GTK2 if you build wxPython manually.

Ubuntu (this may or may not be out of date)
: 

    ```bash
    sudo apt-get install python3.6-dev dpkg-dev build-essential libwebkitgtk-dev libjpeg-dev libtiff-dev libsdl1.2-dev libgstreamer-plugins-base1.0-dev libnotify-dev freeglut3 freeglut3-dev libgtk-3-dev libwebkitgtk-3.0-dev
    ```

    Replace `python3.6-dev` with the Python version you are using.

Fedora 26 (this may or may not be out of date)
: 
    For Fedora 26, it has been reported that you need fewer dependencies to build wxPython; I have not personally confirmed this.

    ```bash
    sudo dnf install gcc-c++ wxGTK-devel gstreamer-devel webkitgtk-devel GConf2-devel gstreamer-plugins-base-devel
    ```

    If your Linux distribution has `gstreamer` 1.0 available (like the Fedora distro), you can install the dev packages
    for that instead of the 0.10 version.

After getting all the correct prerequisites, you should be able to install Rummage with `pip`, though it is recommended
to try and install wxPython first via `pip install wxpython`.

If wxPython doesn't install properly, be sure to reference wxPython's documentation to see if there is something you
are missing. Also, creating an issue over at wxPython's GitHub site for related wxPython install issues may get you help
faster than creating them on the Rummage issue page. Rummage issues are mainly meant for tracking Rummage specific
issues, not wxPython install issues.

Be patient while installing wxPython on Linux as Linux must build wxPython while macOS and Windows do not as wheels are
already provided through `pip`. If installing with `pip`, you may be waiting a long time with no real indication of how
far along the process is.  If `pip` doesn't work, you can look into building and installing manually.  If you find any
of this information incorrect, please feel free to offer a pull request.

## macOS Prerequisites

On macOS, Rummage uses either pure Python modules, or modules that provide wheels. What this means is that no C code
compilation is required to install Rummage; therefore, no prior steps are needed. But if you want to install `regex`,
there will be some C code compilation performed by `pip` which will require Xcode to be installed.

1. Download Xcode from the Mac App Store.
2. Navigate to Xcode > Preferences > Downloads tab.
3. Click the button to install the Command Line Tools.
4. Open Terminal (Applications/Terminal) and run `xcode-select --install`. You will be prompted to install the Xcode
   Command Line Tools.

## Installation

Here are a couple of ways to install and upgrade. Keep in mind if you are a Linux user, you have some
[prerequisites](#linux-prerequisites) to install before proceeding.

Install:

```bash
pip install rummage
```

Install with optional modules.

```bash
pip install rummage[extras]
```

Upgrade:

```bash
pip install --upgrade rummage
```

## Installing in Virtual Environments (macOS)

If installing in a virtual environment via `virtualenv`, you may run into the following error:

This used to be a fairly annoying issue to workaround, but in wxPython 4+, it's not too bad.  The wxPython wiki is a bit
out of date.  You don't have to symlink `wx.pth` or anything like that anymore as the design of wxPython is a bit
different now.  All you have to do is place the script below in `my_virtual_env/bin`.  In this example I call it `fwpy`
for "framework python" (make sure to adjust paths or Python versions to match your installation).

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

There are no known issues installing Rummage in Homebrew.

## Installing in Anaconda

Anaconda can run Rummage fine from my testing on macOS.  The important thing to note is you must launch it with
`pythonw -m rummage` on Windows and **not** `python -m rummage`. While this worked on macOS, results may vary on other
systems. `pythonw` is mainly used on Windows and may not be required on macOS or Linux.

--8<-- "links.txt"
