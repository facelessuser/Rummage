# Installation

## Requirements

Rummage has a few requirements when installing.  These will all be taken care of when installing via `pip`.

Name                           | Details
------------------------------ | -------
[`wxPython`\ 4.0.1+][wxpython] | The new wxPython Phoenix 4.0.0 is required for the GUI.
[`backrefs`\ 3.5.0+][backrefs] | Used to extend the `re` or `regex` regular expression engine with additional back references.
[`chardet`\ 3.0.4+][chardet]   | Used for file encoding guessing when an encoding is not specified.
[`filelock`][filelock]         | Used for file locking to allow different instances of Rummage to access the same file.
[`gntp`][gntp]                 | Used to send notifications to Growl via the the Growl Notification Transport Protocol for all platforms (macOS, Windows, and Linux).
[`send2trash`][send2trash]     | Used for sending files to trash/recycle bin on each platform.

Some optional modules that can be manually installed.

Name                   | Details
---------------------- | -------
[`regex`][regex]       | **regex** usage is completely optional, but it is included for those who wish to use it. Regex is a great regular expression engine that adds some nice features such as fuzzy searching, nested char sets, better Unicode support, and more.
[`cchardet`][cchardet] | `cchardet` is high speed universal character encoding detector. Much faster than `chardet`.

## Linux Prerequisites

Prerequisites are related to wxPython, the graphical interface for Rummage. For Windows and macOS, there are no prerequisites as wxPython provides pre-built wheels for these operating systems, so Rummage can be installed directly and quickly with `pip`. Only Linux requires additional work before installing, but check out the wxPython documentation to learn how to build manually if you have reasons to do so.  The rest of this section refers exclusively to Linux, and mainly from an Ubuntu perspective as that is usually the distro I test on.

The latest wxPython Phoenix builds with GTK3 by default, so the example below will install GTK3 related dependencies. You can use GTK2 if you build wxPython manually.

!!! info "Read First!"

    WxPython is a separate project from Rummage, so this documentation may not always be up to date when it comes to the prerequisites for wxPython.

    Please check the wxPython prerequisites before installing. Particularly under [this section](https://github.com/wxWidgets/Phoenix/blob/master/README.rst#prerequisites), you should find information about Linux Prerequisites.

    I usually try to keep Ubuntu info up to date, but if you find it is outdated, please let me know.  I rely on the community for other distros.

Here are some last known prerequisite for a couple of distros. **Remember, they might be out of date**.

Example is for Ubuntu:

```bash
sudo apt-get install python3.5-dev dpkg-dev build-essential libwebkitgtk-dev libjpeg-dev libtiff-dev libsdl1.2-dev libgstreamer-plugins-base0.10-dev libnotify-dev freeglut3 freeglut3-dev libgtk-3-dev libwebkitgtk-3.0-dev
```

Replace `python3.5-dev` with the Python version you are using.

For Fedora 26, it has been reported that you need fewer dependencies to build wxPython; I have not personally confirmed this.

```bash
sudo dnf install gcc-c++ wxGTK-devel gstreamer-devel webkitgtk-devel GConf2-devel gstreamer-plugins-base-devel
```

If your Linux distribution has `gstreamer` 1.0 available (like the Fedora distro), you can install the dev packages for that instead of the 0.10 version.

After getting all the correct prerequisites, you should be able to install Rummage with `pip`. Be patient while installing Rummage. Linux must build wxPython while macOS and Windows do not. If installing with `pip`, you may be waiting a long time with no real indication of how far along the process is.  If `pip` doesn't work, you can look into building and installing manually.  If you find any of this information, please feel free to offer a pull request or create an issue on GitHub to at least report the problem.

## macOS Prerequisites

On macOS, Rummage uses either pure Python modules, or modules that provide wheels. What this means is that no C code compilation is required to install Rummage; therefore, no prior steps are needed. But if you want to install `regex`, there will be some C code compilation during install via `pip`.

To install modules like `regex`, you will need to have Xcode installed.

1. Download Xcode from the Mac App Store.
2. Navigate to Xcode > Preferences > Downloads tab.
3. Click the button to install the Command Line Tools.
4. Open Terminal (Applications/Terminal) and run `xcode-select --install`. You will be prompted to install the Xcode Command Line Tools.

## Installation

Here are a couple of ways to install and upgrade. Keep in mind if you are a Linux user, you have some [prerequisites](#linux-prerequisites) to install before proceeding.

1. Install:

    ```bash
    pip install rummage
    ```

    Or upgrade:

    ```bash
    pip install --upgrade rummage
    ```

2. Then you can run it from the command line with (assuming your Python scripts/bin folder is in your system path):

    ```bash
    rummage
    ```

    This is the safest, recommended way to run rummage and will prevent it from loading any Python libraries from your current working directory.

    In some environments it may make sense to run rummage with `python -m rummage` or `pythonw -m rummage` (`pythonw` being the preferred for a GUI script like this).  In some environments, it may be required (see ["Running in Anaconda (macOS)"](#running-in-anaconda-macos)).

    !!! Note "python(w) -m rummage"
        In general, Rummage uses relative imports and removes the current local directory from the import path to prevent Python from accidentally overwriting an expected module with a local one. In general, it should be safe to use `python -m rummage` or `pythonw -m rummage` most anywhere.  The only module that is imported before this change is `sys`, but there isn't really a way to avoid this.  Using global `rummage` command will always be the safest.

4. If developing on Rummage, you can clone the project, and install the requirements with the following command:

    ```bash
    pip install -r requirements/project.txt`
    ```

    When developing, you often want to run the local module, not the one installed. You can do this from the project's root folder by running:

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
