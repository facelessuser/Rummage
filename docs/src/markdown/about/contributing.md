# Contributing &amp; Support

## Overview

Contribution from the community is encouraged and can be done in a variety of ways:

- Bug reports.
- Reviewing code.
- Code patches via pull requests.
- Documentation improvements via pull requests.

## Bug Reports

1. Please **read the documentation** and **search the issue tracker** to try to find the answer to your question **before** posting an issue.

2. When creating an issue on the repository, please provide as much info as possible:

    - Version being used.
    - Operating system.
    - Errors in console.
    - Detailed description of the problem.
    - Examples for reproducing the error.  You can post pictures, but if specific text or code is required to reproduce the issue, please provide the text in a plain text format for easy copy/paste.

    The more info provided the greater the chance someone will take the time to answer, implement, or fix the issue.

3. Be prepared to answer questions and provide additional information if required.  Issues in which the creator refuses to respond to follow up questions will be marked as stale and closed.

## Reviewing Code

Take part in reviewing pull requests and/or reviewing direct commits.  Make suggestions to improve the code and discuss solutions to overcome weaknesses in the algorithm.

## Pull Requests

Pull requests are welcome, and if you plan on contributing directly to the code, there are a couple of things to be mindful of.

Continuous integration tests are run on all pull requests and commits via Travis CI.  When making a pull request, the tests will automatically be run, and the request must pass to be accepted.  You can (and should) run these tests before pull requesting. You should also add tests for bugs you are fixing. If it is not possible to run these tests locally, they will be run when the pull request is made, but it is strongly suggested that requesters make an effort to verify before requesting to allow for a quick, smooth merge.

### GUI Tools

The GUI is designed with the tool [`wxFormBuilder`](https://github.com/wxFormBuilder/wxFormBuilder).  Usually the latest version is used unless there are some problematic issues. Simply open the `gui.fbp` file with `wxFormBuilder`. The gear icon in the toolbar will generate the Python code.

Current version being used is **3.8.1**.

### Running Validation Tests

1. Make sure that Tox is installed:

    ```
    pip install tox
    ```

2. Run Tox:

    ```
    tox
    ```

    Tox should install necessary dependencies and run the tests. If you are a Linux user, please check out information on [requirements](./installation.md#requirements).

## Documentation Improvements

A ton of time has been spent not only creating and supporting this plugin, but also spent making this documentation.  If you feel it is still lacking, show your appreciation for the plugin by helping to improve the documentation.  Help with documentation is always appreciated and can be done via pull requests.  There shouldn't be any need to run validation tests if only updating documentation.

To build the documentation, you will need the necessary requirements. You can get them by running `pip install -r requirements/docs.txt`. I currently use a combination of [MkDocs][mkdocs], the [Material theme][mkdocs-material], and [PyMdown Extensions][pymdown-extensions] to render the docs.  You can preview the docs if you install these packages via the requirements file.  The command for previewing the docs is `mkdocs serve`. It should be run from the root directory. You can then view the documents at `localhost:8000`.

When providing documentation updates, please generate Rummage's internal documentation via `python tools/gen_docs.py`. Pull requests will currently fail if the documentation is not updated along with the requested changes.

--8<-- "links.txt"
