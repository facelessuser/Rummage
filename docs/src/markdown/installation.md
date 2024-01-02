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

For well supported platforms, Python wheels are usually available for Rummage and its dependencies. In most cases,
installation can be done quickly and easily through `pip`. Some platforms, like Linux,  may require some additional
hoops that you must jump through. Additionally, wxPython, the GUI library that Rummage depends on, may sometimes have
support lagging for the latest Python version.

In general, it is always recommended to try and install `wxpython` first and make sure it is properly available
before installing Rummage. The wxPython installation may be more complicated depending on the platform. But in general,
for non-Linux systems, the following steps are usually sufficient.

Make sure wxPython is installed first. It is important to first ensure wxPython can be installed for your platform and
specific Python version first.

```console
$ pip install wxpython
```

Install Rummage:

```console
$ pip install rummage
```

Install Rummage with optional modules.

```console
$ pip install rummage[extras]
```

Upgrade Rummage:

```console
$ pip install --upgrade rummage
```

### Windows and macOS

On Windows, installation is pretty straight forward as wheels are provided for all packages in `pip`. In recent years,
macOS installation also usually has wheels available as well. Support for the latest Python version may not always be
available as the development cycle for wxPython can take a bit to catch up.

Simply using `pip` to install is sufficient.

```console
$ pip install rummage
```

### Linux

Linux doesn't often have pre-built wheels for wxPython, so often, you must first ensure some prerequisites are in place
before using `pip install` (or other methods). Additionally, Linux, in recent years, has made managing libraries and
applications in Python a bit more complex with its new restrictions. Despite all of this, Rummage is still supported,
but may require slightly more complex installation.

#### pipx

If installing Rummage on Linux, you may consider `pipx`, especially if your distro has a new enough wxPython [distro
packages](#distro-packages). On Ubuntu, installation may look similar to the following:

``` console
$ sudo apt install python3-wgtk4.0 python3-wxgtk-webview4.0
$ pipx install --system-site-packages rummage
```

The `--system-site-packages` flag is necessary as by default, `pipx` will create a brand new virtual environment that
does not have access to the globally available distro package.

#### venv

Another approach on Linux is to use the `venv` package to install Rummage and its dependencies. If your distro has a new
enough wxPython [distro package](#distro-packages), you can install the wxPython and then create your virtual
environment with the `--system-site-packages` flag to ensure it has access to the installed package. On Ubuntu, it may
look similar to:

``` console
$ sudo apt install python3-wgtk4.0 python3-wxgtk-webview4.0
$ python3 -m venv --system-site-packages ./venv/rummage
$ source ./venv/rummage/bin/activate
$ (rummage) $ pip install rummage
```

If your distro does not have a proper wxPython package, you may have to install it from another source under your
virtual environment.

#### Prerequisites

The most important prerequisite to getting Rummage installed is `wxpython`. It is always recommended to ensure it is
installed before trying to install Rummage. If it is not, installation may try and download `wxpython` and build it
from scratch. This can take a long time and can fail.

##### Distro Packages

Many Linux distros make wxPython available via their package manager. Assuming the package is not too old and is still
supported by Rummage, this should automatically fulfill all the needed requirements. As an example, on Ubuntu, you must
install the following:

``` console
$ sudo apt install python3-wgtk4.0 python3-wxgtk-webview4.0
```

##### Pre-built Wheels

Another option, if your distro packages are too old, is to see if there is a readily available pre-built wheel from the
wxPython team. These are usually kept here: https://extras.wxpython.org/wxPython4/extras/linux/.  It is possible through
that even after this, there may be some Linux dependencies missing. The wheel can be installed in a virtual environment
using pip:

```console
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

##### Manual Building

If you have installed a version of Python on your machine that does not have a pre-built wxPython package, or are using
a distro that does not have a pre-built wheel, you may have to build it.

You can build the package by installing with `pip`, but you may find that it won't build until you get all the
dependencies installed. Once the dependencies for building are in place, you can run pip to install the package.

We do not have updated lists of prerequisites for distros. The last updated list was from Ubuntu 18.04 and Fedora 26.
What you must install may vary depend on what is already installed on your distro out of the box. Also, the version of
each prerequisites may vary from distro to distro or from distro release to distro release.

Usually the requirements deal with `gstreamer`, `gtk`, `libsdl`, etc. Below are some examples, but are most likely out
of date:

/// define
Ubuntu 18.04

- 
    ```shell-session
    $ sudo apt-get install python3.6-dev dpkg-dev build-essential libwebkitgtk-dev libjpeg-dev libtiff-dev libsdl1.2-dev libgstreamer-plugins-base1.0-dev libnotify-dev freeglut3 freeglut3-dev libgtk-3-dev libwebkitgtk-3.0-dev
    ```

Fedora 26

- 
    ```shell-session
    $ sudo dnf install gcc-c++ wxGTK-devel gstreamer-devel webkitgtk-devel GConf2-devel gstreamer-plugins-base-devel
    ```
///

Once dependencies are in place, you can finally install wxPython with pip (`pip install wxpython`). Be patient when
installing wxPython manually as Linux must build the package, and it won't give much in the way of status while it
builds. If it fails and complains about a missing library, you may have to install more dependencies.

For a complete list of dependencies please check wxPython's official documentation on dependencies before installing.
Particularly under [this section][wxpython-prereq]. If they are out of date, please contact the wxPython team for better
instructions.

other systems, there may be some prerequisites. If on Linux, it is recommended to make sure you can install `wxpython`
first. This is due to the fact that installation of that library may require special instructions and will cause the
installation of Rummage to fail if `wxpython` fails due to not having the necessary prerequisites.
