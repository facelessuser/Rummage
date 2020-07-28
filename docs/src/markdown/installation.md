# Installation

## Requirements

Rummage, when installed via `pip`, will install all of your required dependencies, but there are a few optional
dependencies. If desired, you can install these dependencies manually, or install them automatically with
[`pip`](#installation_1).

Name                   | Details
---------------------- | -------
[`regex`][regex]       | Regex is a great regular expression engine that adds some nice features such as fuzzy searching, nested char sets, better Unicode support, and more.
[`cchardet`][cchardet] | `cchardet` is high speed universal character encoding detector. Much faster than the default `chardet`.

## Installation

On systems like Windows, installation is pretty straight forward as wheels are provided for all packages in `pip`. On
other systems, there may be some prerequisites. If on Linux, it is recommended to make sure you can install `wxpython`
first. This is due to the fact that installation of that library may require special instructions and will cause the
installation of Rummage to fail if `wxpython` fails due to not having the necessary prerequisites.

!!! warning "Prerequisites"
    - [Linux](#linux-prerequisites)
    - [macOS](#macos-prerequisites)

Assuming prerequisites are satisfied, installing Rummage is easy.

Install:

```shell-session
$ pip install rummage
```

Install with optional modules.

```shell-session
$ pip install rummage[extras]
```

Upgrade:

```shell-session
$ pip install --upgrade rummage
```

## Linux Prerequisites

Linux is by far the more involved system to install wxPython on, but it is getting easier.

### Recommended

#### Pre-built Wheels

The wxPython project has started providing wheels for certain distros. While not all distros have wheels, this may
be an attractive solution if you run one of the distros that do have pre-built wheels. The one downside is that the
wheels are not available through on PyPI. More information on why and details on installation can be found here:
https://www.wxpython.org/pages/downloads/.

Simplified instructions:

1. Find the folder for your distro over at https://extras.wxpython.org/wxPython4/extras/linux/.

2. Use `pip` and the server's location like so.

    ```shell-session
    $ pip install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-20.04 wxPython
    ```

While the wheel should install fine, when you actually run Rummage, you may see some libraries missing. A common one
on Ubuntu is `libSDL` libraries. If you see a complaint about a library not being found or loaded, and you are on
Ubuntu, you can install `apt-find` and search for the package containing the file, then you can install it.

```shell-session
$ sudo apt install apt-file
$ sudo apt-file update
$ apt-file search libSDL2-2.0.so.0
libsdl2-2.0-0: /usr/lib/x86_64-linux-gnu/libSDL2-2.0.so.0
libsdl2-2.0-0: /usr/lib/x86_64-linux-gnu/libSDL2-2.0.so.0.10.0
$ sudo apt install libsdl2-2.0-0
```

#### Pre-build Packages

If you have a recent Linux distro that has a pre-built, installable wxPython package for your version of Python, then
it may make sense to just install the pre-built package via your Linux package manager. The version must meet the
version requirements of the Rummage package you are installing.

### Manual

If you have installed a version of Python on your machine that does not have a pre-built wxPython package, or are using
a distro that does not have a pre-built wheel, you may have to build it.

You can build the package by installing with `pip`, but you may find that it won't build until you get all the
dependencies installed. Once the dependencies for building are in place, you can run pip to install the package.

We do not have updated lists of prerequisites for distros. The last updated list was from Ubuntu 18.04 and Fedora 26.
What you must install may vary depend on what is already installed on your distro out of the box. Also, the version of
each prerequisites may vary from distro to distro or from distro release to distro release.

Usually the requirements deal with `gstreamer`, `gtk`, `libsdl`, etc. Below are some examples, but are most likely out
of date:

Ubuntu 18.04
: 

    ```shell-session
    $ sudo apt-get install python3.6-dev dpkg-dev build-essential libwebkitgtk-dev libjpeg-dev libtiff-dev libsdl1.2-dev libgstreamer-plugins-base1.0-dev libnotify-dev freeglut3 freeglut3-dev libgtk-3-dev libwebkitgtk-3.0-dev
    ```

Fedora 26
: 

    ```shell-session
    $ sudo dnf install gcc-c++ wxGTK-devel gstreamer-devel webkitgtk-devel GConf2-devel gstreamer-plugins-base-devel
    ```

Once dependencies are in place, you can finally install wxPython with pip (`pip install wxpython`). Be patient when
installing wxPython manually as Linux must build the package, and it won't give much in the way of status while it
builds. If it fails and complains about a missing library, you may have to install more dependencies.

For a complete list of dependencies please check wxPython's official documentation on dependencies before installing.
Particularly under [this section][wxpython-prereq]. If they are out of date, please contact the wxPython team for better
instructions.

## macOS Prerequisites

On macOS, Rummage uses either pure Python modules, or modules that provide wheels. What this means is that no C code
compilation is required to install Rummage; therefore, no prior steps are needed. But if you want to install `regex`,
there will be some C code compilation performed by `pip` which will require Xcode to be installed.

1. Download Xcode from the Mac App Store.
2. Navigate to Xcode > Preferences > Downloads tab.
3. Click the button to install the Command Line Tools.
4. Open Terminal (Applications/Terminal) and run `xcode-select --install`. You will be prompted to install the Xcode
   Command Line Tools.

--8<-- "links.txt"
