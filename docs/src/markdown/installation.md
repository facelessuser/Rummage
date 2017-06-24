# Installation

## Overview

Rummage has a few requirements when installing.  If installing (and not running the scripts directly), the requirements will be installed automatically (except for a few that are optional).  See [Requirements](#requirements) for more info.

## Requirements

In order for PyMdown to work, there are a couple of prerequisites. If following the recommended installation method, the dependencies will be installed for you automatically.

Name                         | Required | Details
---------------------------- | -------- | -------
[backrefs][backrefs]         | Yes      | Used to extend the `re` or `regex` regular expression engine with additional back references.
[gntp][gntp]                 | Yes      | Used to send notifications to Growl via the the Growl Notification Transport Protocol for all platforms (OSX, Windows, and Linux).
[chardet][chardet]           | Yes      | Used for file encoding guessing when an encoding is not specified.
[wxPython\ 4.0.0+][wxpython] | Yes      | The new wxPython 4.0.0 is required for for Rummage to run in Python 2 and Python 3. Classic wxPython support has unfortunately be dropped.
[regex\ 2015.07.19+][regex]  | No       | **regex** is completely optional, but it will be installed automatically if using `pip`. It is a great regular expression engine that adds some nice features such as fuzzy searching, nested char sets, better Unicode support, and more.  I have mentioned `2015.07.19` as the preferred minimum version.

## Installation

Here are a couple of ways to install and upgrade.

1. Install: `#!bash python pip install rummage`.

2. To upgrade: `#!bash python install --upgrade rummage`.

2. If developing on rummage, you can clone the project, install the requirements with the following command:

    ```bash
    pip install -r requirements/project.txt`
    ```

    Then install the package via:

    ```bash
    pip install --editable .
    ```

    You could also just optionally run the package locally, skipping the `--editable` step, and by issuing the following command from the root folder:

    ```
    python -m rummage
    ```

    This method will allow you to instantly see your changes between iterations without reinstalling which is great for developing.  If you want to do this in a virtual machine, you can as well.  Like the first method, you should then be able to access Rummage from the command line via `rummage` or `rummage --path mydirectory`.

--8<-- "links.md"