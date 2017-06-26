# Installation

## Requirements

Rummage has a few requirements when installing.  These will all be taken care of when installing via `pip`.

Name                           | Required | Details
------------------------------ | -------- | -------
[`backrefs` 1.0.1+][backrefs]    | Yes      | Used to extend the `re` or `regex` regular expression engine with additional back references.
[`gntp`][gntp]                   | Yes      | Used to send notifications to Growl via the the Growl Notification Transport Protocol for all platforms (macOS, Windows, and Linux).
[`chardet`\ 3.0.4+][chardet]             | Yes      | Used for file encoding guessing when an encoding is not specified.
[`wxPython`\ 4.0.0a3+][wxpython] | Yes      | The new wxPython 4.0.0 is required for for Rummage to run in Python 2 and Python 3. Classic wxPython support has unfortunately be dropped.
[`regex`\ 2015.07.19+][regex]    | No       | **regex** is completely optional, but it will be installed automatically if using `pip`. It is a great regular expression engine that adds some nice features such as fuzzy searching, nested char sets, better Unicode support, and more.

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

--8<-- "links.md"
