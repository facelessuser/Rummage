# User Guide

## Overview

Rummage is designed to be easy to pick up. Its interface consists of three tabs: Search, Files, and Content.  In the **Search** tab, a user specifies where they want to search, what they want to search for, and optionally what they want to replace it with.  Search features can be tweaked with various options. The files that get searched can also be narrowed with patterns and filters.

Rummage uses the default regular expression library ([Re][re]) that comes with Python. It also optionally works with the 3rd party [Regex][regex] library (if installed).

As matches are found, general info about the matches will be displayed in the **Files** and **Content** tabs. You can double click files to open them in your favorite editor (see [Editor Preferences](#editor) to configure Rummage for your editor).

Rummage also comes with a simple regular expression tester to test out patterns. It also provides a feature where patterns can be saved for later and/or frequent use. You can even create chains that will apply a series of saved searches.

## Running

After installation, you should then be able to access Rummage from the command line.  This assumes the Python bin directory is in the path.

```bash
rummage
```

Or specify a path:

```bash
rummage --path mydirectory
```

Or execute the module:

```bash
python -m rummage
```

## Searching &amp; Replacing

![Search Tab](/images/search_tab.png)

Search and replaces are configured in the **Search** tab which is broken up into 2 panels, the first of which is the **Search &amp; Replace** panel. The second is the **Limit Search** panel.

### Search Panel

![Search and Replace Panel](/images/search_replace_inputs.png)

The **Search &amp; Replace** panel contains three text boxes with a dropdown history. The first text box defines **where to search**, the second defines **what to search for**, and the last defines **what to replace matches with** (this is only needed when doing replaces).  You can select previously used patterns and search targets by expanding the dropdown panel for the input.

Below the text boxes are checkboxes that control the regular expression engine's options and features.

![Search and Replace Checkboxes](/images/search_replace_panel.png)

The available features will vary depending on which regular expression engine you are using. Each feature is documented in [Options](#options).

Lastly, Rummage provides buttons to launch a [regular expression tester](#regular-expression-tester), dialogs to [save or load](#saving-and-loading-regular-expressions) frequently used regular expressions, and a dialog to create and manage [regular expression chains](#search-chains).

![Regular Expression Buttons](/images/regex_buttons.png)

### Limit Search Panel

![Limit Search Panel](/images/limit_search_panel.png)

The **Limit Search** panel contains checkboxes and inputs that filter the files to be searched.  You can hide hidden files, filter out files by size, or creation date.

You can also restrict which files get searched by providing a wild card pattern. By default, the patterns are applied to the base file or folder name. See [File Patterns](#wildcard) to learn more about accepted wild card pattern syntax and how to configure optional file pattern features. If you prefer regular expression, you can optionally use regular expression patterns instead.

### Results

Once a search or replace is initiated, the results will begin to appear in the Files and Content tabs. You can then double click a file to open it in your editor, or right click them to bring up a context menu with additional options.

![Files Tab](/images/files_tab.png)

![Content Tab](/images/content_tab.png)

!!! tip
    You can hide/show columns by right clicking the list header to get a special context menu. You can then deselect or select the the column(s) you wish to hide/show respectively.

## Options

Rummage supports the default regular expression library ([Re][re]) that comes with Python and the 3rd party [Regex][regex] library, and though the basic syntax and features are similar between the two, Regex provides many additional features, some of which causes the syntax to deviate greatly from Re. If you are using Re, you will not see all the options shown below. Please check out documentation for whichever engine you have chosen to learn more about its specific feature set. This documentation will only briefly cover the features that can be enabled in each engine.

### Common Options

Both the Re and Regex engine have a couple of shared flags that are exposed in Rummage as checkboxes. These checkboxes are found directly under the search and replace text boxes.

Toggle                      | Description
--------------------------- | -----------
Search\ with\ regex         | Alters the behavior of `Search for` and `Replace with`.  When this is checked, both text boxes require regular expression patterns opposed to literal string.
Search\ case-sensitive      | Forces the search to be case-sensitive.
Dot\ matches\ newline       | `.` will also match newlines.
Use\ Unicode\ properties    | Changes the behavior of `\w`, `\W`, `\b`, `\B`, `\d`, `\D`, `\s`, and `\S` to use use characters from the Unicode property database (will also modify `\l`, `\L`, `\c`, and `\C` in search patterns if using Backrefs with Re).
Format\ style\ replacements | Replace pattern will use [a string replace format][format-string] for replace. `#!py3 "{1} {1[-2]} {group_name[-3]}"` etc. This is not available for Re without Backrefs, and is limited when using Re with Backrefs. Read more about format mode [here][backrefs-format]. And remember that Rummage normalizes mentioned differences in Backrefs' and Regex's handling of back slash escapes in format replace mode.

### Regex Engine Options

If the Regex engine is being used for regular expressions, a couple of extra checkboxes will be available. Regex can be run in either `VERSION0` or `VERSION1` mode.

`VERSION0` is compatible with Re regular expression patterns and has the extra `fullcase` toggle. `VERSION1` does not have this toggle as it is enabled by default and can only be disabled inline via a pattern with `(?-f)`. `VERSION1` is not directly compatible with Re patterns as it adds a number of changes to the syntax allowing for more advanced search options.

Toggle                      | Description
--------------------------- | -----------
Best\ fuzzy\ match          | If performing a fuzzy match, the *best* fuzzy match will be used.
Improve\ fuzzy\ fit         | Makes fuzzy matching attempt to improve the fit of the next match that it finds.
Unicode\ word\ breaks       | Will use proper Unicode word breaks and line separators when Unicode is enabled. See Regex documentation for more info.
Use\ POSIX\ matching        | Use the POSIX standard for regular expression, which is to return the leftmost longest match.
Search\ backwards           | Search backwards. The result of a reverse search is not necessarily the reverse of a forward search.
Full\ case-folding          | Use full case folding. For Regex `V0` only as it is enabled by default for `V1`.

### Rummage Options

Rummage has a couple of flags that are not specific to the regular expression engine.

Toggle                  | Description
----------------------- | -----------
Boolean\ match          | Will check each file up until the first match and will halt searching further.  No line context info will be gathered or displayed. Does not apply when performing replaces.
Count\ only             | Will just count the number of matches in the file and will not display line context information. This has no effect when applying replaces.
Create\ backups         | On replace, files with matches will be backed up before applying the replacements; backup files will have the `.rum-bak` extension.
Force\ &lt;encoding&gt; | Forces all files to be opened with the specified encoding opposed to trying to detect the encoding.  Encoding is hard and slow, so this is the preferred method for fast searches.  On failure, binary will be used instead.
Use\ chain\ search      | Puts Rummage into ["search chain" mode](#search-chains). When in "search chain" mode, rummage will only use saved search chains for search and replace.
Use\ replace\ plugin    | When enabled, Rummage will use a [replace plugin](#replace-plugins) instead of a replace pattern in order to do more advanced replaces.

!!! tip "Encoding Guessing"

    It is always recommended, if you know the encoding, to use `Force encoding` as it will always be the fastest. Encoding guessing can be slow and not always accurate.

    Encoding guessing is performed by `chardet` which is a pure Python library and is, by far, the slowest option.  If you manually install `cChardet`, you will have a much faster guessing experience.

## Regular Expression Tester

![Regex Tester](/images/regex_tester.png)

Rummage comes with a simple regular expression tester. It has a simple text box to place content to search, and another text box that will show the final results after the find and replace are applied.  Below those text boxes, there are two text input boxes for the find pattern and the replace pattern.  Lastly, all search and replace flag options are found under the patterns.

To use the tester, simply enter the content to search, set your desired options, and input your find and replace pattern.  As you change your pattern or options, matches will be updated and highlighted, and the result box will be updated with any replacements.

When you are satisfied with your result, click the `Use` button, and your pattern and settings will be populated in the main window.

## File Patterns

![File Patterns](/images/file_pattern.png)

Wildcard patterns are the default for file and folder exclude patterns, but regular expression patterns can be used instead by selecting the `Regex` checkbox beside the pattern. Wildcard patterns and regular expression patterns will each be covered separately.

### Wildcard

Rummage uses file patterns and folder excludes to filter which files are searched. The default is to use wild card patterns modeled after `fnmatch` and `glob`. Below is a list of the syntax that is accepted, but not all features are enabled by default.

If you would prefer regular expression file patterns, please see [Regular Expression](#regular-expression) file patterns.

- File patterns are case insensitive by default, even for Linux/Unix systems. Case sensitivity can be enabled in [Preferences](#search).
- Slashes are generally treated as normal characters, but on windows they will be normalized: `/` will become `\\`. There is no need to explicitly use `\\` in patterns on Windows, but if you do, it will be handled.
- `.` is always matched by `*`, `?`, `[]`, and extended patterns such as `*(...)`. Use enable searching hidden files in the [Limit Panel](#limit-panel).

#### Basic Wildcard syntax

Rummage uses the [`wcmatch`][wcmatch] library to implement a specialized version of [`fnmatch`][wcmatch-fnmatch] wildcard patterns for file name matching.

Pattern           | Meaning
----------------- | -------
`*`               | Matches everything.
`?`               | Matches any single character.
`[seq]`           | Matches any character in seq.
`[!seq]`          | Matches any character not in seq.
`[[:alnum:]]`     | POSIX style character classes inside sequences. The `C` locale is used for byte strings and Unicode properties for Unicode strings. See [POSIX Character Classes][posix] in `wcmatch`'s documentation for more info.
`\`               | Escapes characters. If applied to a meta character, it will be treated as a normal character.
`|`               | Multiple patterns can be provided by separating them with `|`.
`-`               | If `-` is found at the start of a pattern, it will match the inverse.
`\xhh`            | By specifying `\x` followed by the hexadecimal byte value, you can specify characters directly.
`\uhhhh`          | By specifying `\u` with the four value hexadecimal character value, you can specify Unicode characters directly.
`\Uhhhhhhhh`      | By specifying `\U` with the eight value hexadecimal character value, you can specify wide Unicode characters directly.
`\N{name}`        | By specifying `\N{name}`, where `name` is a valid Unicode character name, you can specify Unicode characters directly.
`\a`              |  ASCII Bell (BEL).
`\b`              |  ASCII Backspace (BS).
`\f`              |  ASCII Formfeed (FF).
`\n`              |  ASCII Linefeed (LF).
`\r`              |  ASCII Carriage Return (CR).
`\t`              |  ASCII Horizontal Tab (TAB).
`\v`              |  ASCII Vertical Tab (VT).


!!! example "Example Patterns"

    Used in the `Files which match` box, this would match all Python files of `.py` extensions excluding `__init__.py`:

    ```
    *.py|-__init__.py
    ```

    Used in the `Files which match` box, this would match any file type that is not `.py`.

    ```
    -*.py
    ```

    Used in the `Exclude folders`, this would exclude all folders with `name` followed by a single digit, except `name3` which we will always be included.

    ```
    name[0-9]|-name3
    ```

    Used in the `Exclude folders`, this would exclude all folders except `name3`.

    ```
    -name3
    ```

    If you need to escape `-` or `|`, you can put them in a sequence: `[-|]`. Remember to place `-` at the beginning of a sequence as `-` is also used to specify character ranges: `[a-z]`.

#### Extended Match Syntax

In [Preferences](#search), you can also enable extended match patterns. Extended match patterns allow you to provide pattern lists to provide more advanced logic.

Pattern           | Meaning
----------------- | -------
`?(pattern_list)` | The pattern matches if zero or one occurrences of any of the patterns in the `pattern_list` match the input string. Requires extended match feature to be enabled.
`*(pattern_list)` | The pattern matches if zero or more occurrences of any of the patterns in the `pattern_list` match the input string. Requires extended match feature to be enabled.
`+(pattern_list)` | The pattern matches if one or more occurrences of any of the patterns in the `pattern_list` match the input string. Requires extended match feature to be enabled.
`@(pattern_list)` | The pattern matches if exactly one occurrence of any of the patterns in the `pattern_list` match the input string. Requires extended match feature to be enabled.
`!(pattern_list)` | The pattern matches if the input string cannot be matched with any of the patterns in the `pattern_list`. Requires extended match feature to be enabled.
`{}`              | Bash style brace expansions.  This is applied to patterns before anything else. Requires brace expansion feature to be enabled.

!!! example "Example Extended Match Patterns"

    For example, if we wanted to match files `this-file.txt` and `that-file.txt`, we could provide the following pattern:

    ```
    @(this|that)-file.txt
    ```

    The `|` contained within an extended match group will not split the pattern. So it is safe to combine with other patterns:

    ```
    @(this|that)-file.txt|*.py
    ```

#### Brace Expansion Syntax

In [Preferences](#search), you can enables Bash style brace expansion.

Brace expansion is applied before anything else. When applied, a pattern will be expanded into multiple patterns. Each pattern will then be parsed separately.

For simple patterns, it may make more sense to use extended match patterns which will only generate a single pattern: `@(ab|ac|ad)`.

Be careful with patterns such as `{1..100}` which would generate one hundred patterns that will all get individually parsed. Sometimes you really need such a pattern, but be mindful that it will be slower as you generate larger sets of patterns.

Pattern           | Meaning
----------------- | -------
`{,}`             | Bash style brace expansions.  This is applied to patterns before anything else. Requires brace expansion feature to be enabled.
`{n1..n2[..i]}`     | Bash style sequences that expands a range of numbers or alphabetic characters by an optional increment.

!!! example "Example Brace Expansion"

    - `a{b,{c,d}}` --> `ab ac ad`
    - `{1..3}` --> `1 2 3`
    - `{a..d}` --> `a b c d`
    - `{2..4..2}` --> `2 4`
    - `{a..e..2}` --> `a c e`

#### Full Path Matching

In [Preferences](#search), you can enable full path search for either file patterns and/or folder exclude patterns. This will allow for matching against a full path instead of the base file name. While it is referred to as "full path", it is still relative to the provided base path.

Assuming you Provided a base folder to search of `/My/base/path`, and you were to match a file `/My/base/path/some/file.txt`, normally your file pattern would match against `file.txt`, but with full path enabled, you'd match against `some/file.txt`. This means you'd have to use pattern like `*/*.txt` instead of `*.txt`.

When full path matching is enabled for a pattern, slashes are generally treated special. Slashes will not be matched in `[]`, `*`, `?`, or extended patterns like `*(...)`. Slashes can be matched by `**` if globstar (`**`) is enabled in [Preferences](#search).

Pattern           | Meaning
----------------- | -------
`**`              | Matches zero or more directories. Only available for full path matching which is disabled by default.

### Regular Expression

Wildcard patterns are the default for file and folder exclude patterns, but regular expression patterns can be used instead by selecting the `Regex` checkbox beside the pattern. The regular expression engine set in [Preferences](#search) is what will be used for file patterns. It will also respect the case sensitivity setting in [Preferences](#search) for **File/Folder Matching**.

#### Full Path Matching

In [Preferences](#search), you can enable full path search for either file patterns and/or folder exclude patterns. This will allow for matching against a full path instead of the base file name. While it is referred to as "full path", it is still relative to the provided base path.

Assuming you Provided a base folder to search of `/My/base/path`, and you were to match a file `/My/base/path/some/file.txt`, normally your file pattern would match against `file.txt`, but with full path enabled, you'd match against `some/file.txt`. This means you'd have to use pattern like `.*/.*.txt` instead of `.*.txt`.

## Advanced Search Features

### Backrefs

Rummage has the option of using a special wrapper called Backrefs. Backrefs can be applied to either Re or Regex. It adds various back references that are known to some regular expression engines, but not to Python's Re or Regex modules.  The supported back references actually vary depending on whether it is being applied to Re or Regex. For instance, Backrefs only adds Unicode Properties to Re since Regex already has Unicode properties. To learn more about Backrefs adds, read the official [Backrefs documentation][backrefs]. You can enable extended back references in the [Preferences](#search) dialog.

### Saving and Loading Regular Expressions

Regular expressions can be very complex, and sometimes you might want to save them for future use.

When you have a pattern configured that you want to save, simply click the `Save Search` button, and a dialog will pop up asking you to name the search.  When done, click the `Save` button on the dialog and your search patterns and options will be saved.

You'll notice that there are two input boxes. The first requires a unique name (only word characters, underscores, and hyphens are allowed). The second is an optional comment in case you wish to elaborate on what the pattern is for.

Underneath the inputs will be the actual search settings being saved.

![Save Search](/images/save_search.png)

To load a pattern that was saved previously, click the `Load Search` button.  You will be presented with a dialog showing all your saved searches.  Highlight the pattern you want to load and click the `Load` button.  Your pattern and options will be populated in the main dialog.

If you wish to edit the name or comment of a search, you can double click the entry or click the "Edit" button.

![Load Search](/images/load_search.png)

### Search Chains

There are times you may have a task that requires you to do multiple find and replaces that are all related, but are too difficult to represent as a single find and replace. This is where search chains can be helpful.

Search chains are essentially a sequence of multiple [saved search and replace patterns](#saving-and-loading-regular-expressions). You can create a search chain by clicking the `Search Chains` button which will bring up the search change manager.

![Chain Button](/images/chain_button.png)

Here you can create or delete search chains.

![Search Chains](/images/chains.png)

To use search chains, you must put Rummage in "search chain" mode by selecting the check box named `Use search chains` in the main window. When "search chain" mode is enabled, all controls that don't apply to search chains will be disabled, and the search box will be replaced with a drop down for selecting existing chains you've already created. When a search is performed, Rummage will iterate over each file with all the saved searches in the chain.

![Chain Select](/images/chain_mode.png)

### Replace plugins

Regular expressions are great, but sometimes regular expressions aren't enough.  If you are dealing with a replace task that requires logic that cannot be represented in a simple replace pattern, you can create a "replace plugin".

Replace plugins are written in Python and are loaded by first selecting the `Use plugin replace` check box in the main dialog.

![Enable Replace Plugin](/images/plugin_toggle.png)

Then the main dialog's `Replace with` text box will become the `Replace plugin` text box with an associated file picker.  Here you can point to your replace plugin file.

Replace plugins aren't meant to be full, complex modules that import lots of other relative files.  They are meant to be a single, compact script, but inside that script, you can import anything that is *already* installed in your Python environment.

![Enable Replace Plugin](/images/plugin_input.png)

#### Writing a Plugin

Replace plugins should contain two things. The first is a plugin class derived from the `rummage.lib.rumcore.ReplacePlugin`.  The second is a function called `get_replace` that returns your class.

The plugin class is fairly straight forward and is shown below.

```py3
class ReplacePlugin(object):
    """Rummage replace plugin."""

    def __init__(self, file_info, flags):
        """Initialize."""

        self.file_info = file_info
        self.flags = flags
        self.on_init()

    def on_init(self):
        """Override this function to add initialization setup."""

    def get_flags(self):
        """Get flags."""

        return self.flags

    def get_file_name(self):
        """Get file name."""

        return self.file_info.name

    def is_binary(self):
        """Is a binary search."""

        return self.file_info.encoding.encode == 'bin'

    def is_literal(self):
        """Is a literal search."""

        return self.flags & LITERAL

    def replace(self, m):
        """Make replacement."""

        return m.group(0)
```

`ReplacePlugin`'s `replace` function will receive the parameter `m` which is either a `regex` or `re` match object (depending on what regular expression engine is selected). The return value must be either a Unicode string or byte string (for binary files).

The `ReplacePlugin`'s `file_info` property is a named tuple providing information about the current file such as name, size, creation date, etc.

```py3
class FileInfoRecord(namedtuple('FileInfoRecord', ['id', 'name', 'size', 'modified', 'created', 'encoding'])):
    """A record for tracking file info."""
```

The `ReplacePlugin`'s `flags` property contains only Rummage search related flags (the flags are abstracted at this level and are converted to the appropriate regular expression flags later). They can also be accessed from `rummage.lib.rumcore`. The flags are shown below.

```py3
# Common regular expression flags (re|regex)
IGNORECASE = 0x1  # (?i)
DOTALL = 0x2      # (?s)
MULTILINE = 0x4   # (?m)
UNICODE = 0x8     # (?u)

# Regex module flags
ASCII = 0x10            # (?a)
FULLCASE = 0x20         # (?f)
WORD = 0x40             # (?w)
BESTMATCH = 0x80        # (?b)
ENHANCEMATCH = 0x100    # (?e)
REVERSE = 0x200         # (?r)
VERSION0 = 0x400        # (?V0)
VERSION1 = 0x800        # (?V1)
FORMATREPLACE = 0x1000  # Use {1} for groups in replace
POSIX = 0x2000          # (?p)

# Rumcore search related flags
LITERAL = 0x10000           # Literal search
```

!!! example "Example Plugin"
    In the example below, we have a replace plugin that replaces the search result with the name of the file.  It is assumed this is not a binary replace, so a Unicode string is returned.

    ```py3
    from __future__ import unicode_literals
    from rummage.lib import rumcore
    import os


    class TestReplace(rumcore.ReplacePlugin):
        """Replace object."""

        def replace(self, m):
            """Replace method."""

            name = os.path.basename(self.get_file_name())
            return name


    def get_replace():
        """Get the replace object."""

        return TestReplace
    ```

## Preferences

The preference dialog is found in the menu at **File-->Preferences** and contains all of the global options that can be controlled for the editor.

### General

![Preferences: General](/images/settings_general.png)

The **General** tab contains a couple of useful settings.

Single Instance
: 
    By default, Rummage will allow for multiple windows to be open.  If this option is enabled, the first window will be be the only window to open.  All subsequent instances will pass their arguments to the first and close without showing a window.

Language
: 
    Rummage has internal support to display dialog labels in different languages. Currently Rummage has English. Russian is outdated but includes a fair bit of the needed translations. See [Localization](#localization) to learn more about improving current translations or adding additional translations.

Updates
: 
    Controls whether Rummage will check for new updates daily and allows controlling whether you want to be notified of prereleases as well. A button has also been provided to check for updates right away after configuring your update settings.

    The check is only a check for new versions and doesn't perform an upgrade.  Rummage must be upgraded via `pip` from command line.

    !!! info "Update Issues: Python 3.6+ on macOS"
        There is a small issue on macOS with Python 3.6+: Python 3.6 changed how it gets the default certificates required to properly check URLs. The details are actually documented here: https://bugs.python.org/issue28150#msg276516.

        To get access again to the default certificates is actually quite easy. Assuming that Python 3.6+ was installed using the macOS installer from Python.org, you just need to navigate to `/Applications/Python 3.6/Install Certificates.command` and double click the command.  The script will use `pip` to install `certifi` and creates a symlink in the OpenSSL directory to `certifi`'s installed bundle location. If you are using something like macports, then you'll probably have to research to find out how to do the same thing.

International Time
: 
    Rummage displays file creation and modified time in the form `Jul 01, 2018, 03:00:00 AM`, but you can enable this option to display the times in international format: `2018-07-01 03:00:00`.

### Search

![Preferences: Regex](/images/settings_search.png)

The **Regular Expression Modules** panel is where the desired regular expression engine that Rummage uses can be selected and configured.  By default, Rummage will use Re, but if Regex module is installed in your Python installation, it can be selected instead.  There is also the options of using Re or Regex with [Backrefs](#backrefs) (a wrapper that adds a couple of special escapes).

If using Regex, you can set it to version of your choice. `V0` tries to be completely compatible with Re patterns while `V1` breaks compatibility with Re and adds even more useful features. Please see [Regex documentation](https://pypi.python.org/pypi/regex/) to learn more.

Under **File/Folder Matching** are a number options for file and folder matching patterns. Follow the links to learn more about each feature:

- [Extended match](#extended-match-syntax).
- [Brace expansion](#brace-expansion-syntax).
- Case sensitive for [wildcard match](#wildcard) and for [regular expression match](#regular-expression).
- [Globstar](#full-path-matching).
- [Full path directory matching](#full-path-matching).
- [Full path file matching](#full-path-matching_1).

### Encoding

![Preferences: Encoding](/images/settings_encoding.png)

The **Encoding** panel is where you can tweak encoding detection. You can change the default encoding detection used (assuming you have both Chardet and cChardet installed). By default, Rummage will use the fastest (cChardet).

Special encoding file type considerations are also exposed here. File extensions assigned to either HTML, XML, or Python will use special logic to look for encoding declarations in the file's header, while file extensions assigned to binary will shortcut the encoding selection to binary. Just double click the file type whose extensions you would like to modify.

Remember that encoding detection is far from bulletproof and can pick an incorrect encoding. While during searches it might not be as big an issue, it is strongly suggested you use a forced encoding when performing replaces.

### Editor

![Preferences: Editor](/images/settings_editor.png)

The **Editor** panel allows you to configure the editor that will be used to open files.  To setup, simply enter the path to the editor and the options it should be called with. Once done, press the save button.

As noted in the image above, Rummage provides 3 special variables that can be used to insert the file name, line number, or column number.

Argument Variables | Description
------------------ | -----------
`{$file}`          | Insert the file name.
`{$line}`          | Insert the line number.
`{$col}`           | Insert the column number.

### Notifications

![Preferences: Notifications](/images/settings_notify.png)

The **Notification** panel controls enabling/disabling and configuration of notifications.  You can enable/disable visual notifications and/or audible notification sounds.

You can also select whether to use the system's built-in notifications or Growl.

A test button is provided to test the configuration once set.

Ubuntu
: 
   - Growl: [Support for Linux][growl-linux].
   - Native: OSD via `notify-send`.

    !!! info "Other Distros"
        Though Rummage should run on any Linux distro, the native dialog option was built around Ubuntu's native notifications called OSD.  Notifications will not work on other distros that do not use OSD *unless* they use Growl.  Even without Growl, other distros will probably still get the audible cue, but as each distro varies, it is difficult to be certain.  As notifications are not crucial to usage, this is minor concern.

macOS
: 
    - Growl: [Support for macOS][growl-macos].
    - Native: Notification Center via [terminal-notifier][terminal-notifier]. Path to `terminal-notifier` must be configured.

    !!! info "Configuring macOS Native"
        When selecting `native` on macOS, an option to select the path to terminal notifier will be available since native dialogs rely on `terminal-notifier` to send notifications to the Notification Center. This must be configured or *native* notifications will not work.

        When selecting the `terminal-notifier` path, you can select either the binary directly or the `.<app` bundle (depending on how you installed `terminal-notifier`).  When selecting the `.app` bundle, Rummage will know how to access the binary inside the bundle.

Windows
: 
    - Growl: [Support for Windows][growl-win].
    - Native: Native windows taskbar notifications.


### History

![Preferences: History](/images/settings_history.png)

The **History** panel is where all text box, drop down history can be cleared.

### Backups

![Preferences: Backups](/images/settings_backup.png)

The **Backups** panel allows you to configure where Rummage creates backups. You can control whether backups are all placed in the same folder as the original source, or if they are put into a subfolder. You can also configure the name of the subfolder used or the extension used when not writing to a subfolder.

## Export to CSV or HTML

![HTML Export](/images/html_export.png)

Rummage allows the exporting of the results to either CSV or HTML.  Simply select **File-->Export** and pick either **CSV** or **HTML**.  The HTML output will be styled similar to the GUI interface with the results in tables with sortable columns.

!!! info "Large Result Sets"
    Really, really large sets of results will probably be best suited for CSV as a browser may have a hard time loading the entire data set at once.

## Import/Export Settings

If desired, Rummage's settings can be exported to a JSON file or imported from a JSON file.  This can be particularly useful for importing regular expression patterns from one system into another system's existing regular expression list. This can also be useful if you have a lot of regular expression patterns you wish to create, and it would be too cumbersome to do it through the GUI.  In the latter case, you could construct the pattern configurations in a JSON file and import all the patterns in one shot.

Import and export are broken up into three types of settings: general settings, chains, and searches. General settings are the basic feature configurations for Rummage.  Chains contains all of your configured pattern chains.  And searches is the actual configured search and replaces.  When exporting, you will be presented with a dialog allowing you to select which categories of settings you wish to export.

![Settings: Export](/images/settings_export.png)

When importing, you will be prompted to select the settings file to import.  Then you will be asked to select one or more settings categories to import.  Rummage will skip any malformed or invalid settings. If you are going to overwrite an existing chain or search, it will prompt you whether to proceed with the overwrite.  Afterwards, it will output the import results in the text box.

![Settings: Export](/images/settings_import.png)

The general settings are meant to be transferred between installations, not specifically configured by hand, so all the supported settings will not be covered here, but the chain and search format will be discussed in details.

The chain format for importing is shown below:

```js
{
    "chains": {                 // The key that denotes this setting is the "chains" setting.
        "a-chain": [            // Unique chain ID.  Must be composed of letters, numbers, underscores, and hyphens.
            "example-1",        // A list of references to specific unique search IDs.
            "example-2"
        ],
        "another-chain": [
            "example-3",
            "example-4"
        ]
    }
}
```

The search/replace format for importing is show below:

```js
{
    "saved_searches": {                                         // The key that denotes this setting is the "chains" setting.
        "Copyright-update": {                                   // Unique search ID.  Must be composed of letters, numbers, underscores, and hyphens.
            "flags": "is",                                      // Search and replace flags (covered below).
            "is_function": false,                               // Boolean stating whether the replace pattern is a function or not.
            "is_regex": true,                                   // Boolean stating whether the search pattern is a regular expression or literal string.
            "name": "Copyright update",                         // A more user friendly name or description of the pattern.
            "replace": "\\g<1>16",                              // The replace pattern, or in case `is_function` is `true`, the path to the Python replace plugin file.
            "search": "(Copyright \\(c\\) \\d+ - 20)(\\d{2})"   // The search pattern.
        }
    }
}
```

Below is a table containing valid flags for the `flags` parameter.  Literal searches only allow flags `i`, `u`, and `f`.  Regular expression patterns can use `i`, `u`, `f`, `s`, `b`, `e`, `w`, `r`, `p`, and `F` (though flags are applicable depending on whether you are using Re, Regex, or one of the two with Backrefs).

Flags | Supported\ Libraries                       | Option
----- | ------------------------------------------ | -----------
`i`   | All                                        | [Search case-sensitive.](#common-options)
`u`   | All                                        | [Use Unicode properties.](#common-options)
`s`   | All                                        | [Dot matches newline.](#common-options)
`f`   | Regex, Regex\ + \Backrefs                  | [Full case-folding.](#regex-options)
`b`   | Regex, Regex\ + \Backrefs                  | [Best fuzzy match.](#regex-options)
`e`   | Regex, Regex\ + \Backrefs                  | [Improve fuzzy fit.](#regex-options)
`w`   | Regex, Regex\ + \Backrefs                  | [Unicode word breaks.](#regex-options)
`r`   | Regex, Regex\ + \Backrefs                  | [Search backwards.](#regex-options)
`p`   | Regex, Regex\ + \Backrefs                  | [Use POSIX matching.](#regex-options)
`F`   | Regex, Regex\ + \Backrefs, Re\ + \Backrefs | [Format style replacements.](#common-options)

## File Manager Context Menu

### macOS

- Open Automator.
- Create new Service.
- Set the following:
    - Service receives selected `files or folders` in `any Application`.
    - Shell: `/bin/sh`.
    - Pass input: `as arguments`.
    - Content of script:

        ```
        (/Library/Frameworks/Python.framework/Versions/3.6/bin/rummage --path "$1")>/dev/null 2>&1 &
        ```

        This is just an example. You will need to determine the location of your Python install.

- Save to `/Users/<username>/Library/Services/Rummage Here...`.

### Windows

- Create a file `rummage.reg` with the content from one of the entries below. Replace `<python_install_path>` with the actual path to your Python directory (usually something like: `c:\Python35`).  Remember to escape backslashes appropriately. Also note that we quote `%1` to allow spaces in the command line argument. Paths may vary, and it is left up to the user to discover where their Python install directory is.

    !!! warning
        This isn't a guide in how to do registry editing proper, so only edit the registry if you are certain of what you are doing.

    ```ini
    Windows Registry Editor Version 5.00

    [HKEY_CLASSES_ROOT\Folder\shell\Rummage Here...]
    @=""

    [HKEY_CLASSES_ROOT\Folder\shell\Rummage Here...\command]
    @="<python_install_path>\\Scripts\\rummage.exe --path \"%1\""

    [HKEY_CLASSES_ROOT\*\shell\Rummage Here...]
    @=""

    [HKEY_CLASSES_ROOT\*\shell\Rummage Here...\command]
    @="<python_install_path>\\Scripts\\rummage.exe --path \"%1\""

    ```

    Optionally, you can also include the Rummage icon beside your context menu entry by adding a few additional lines:

    ```ini
    Windows Registry Editor Version 5.00

    [HKEY_CLASSES_ROOT\Folder\shell\Rummage Here...]
    @=""
    "Icon"="<python_install_path>\\Lib\\site-packages\\rummage\\lib\\gui\\data\\rummage.ico"

    [HKEY_CLASSES_ROOT\Folder\shell\Rummage Here...\command]
    @="<python_install_path>\\Scripts\\rummage.exe --path \"%1\""

    [HKEY_CLASSES_ROOT\*\shell\Rummage Here...]
    @=""
    "Icon"="<python_install_path>\\Lib\\site-packages\\rummage\\lib\\gui\\data\\rummage.ico"

    [HKEY_CLASSES_ROOT\*\shell\Rummage Here...\command]
    @="<python_install_path>\\Scripts\\rummage.exe --path \"%1\""

    ```

- Save file.
- Double click the registry file to add the context menu into Windows Explorer.

### Linux

There are many different flavors of Linux using different file managers.  This makes it difficult to give a guide to cover all cases.  Please research about your specific distro's file manager and how to add context menus.  If you would like to include the info here, please issue a pull request to update the documentation.

#### Ubuntu Nautilus

Paths might vary depending on Ubuntu version etc.

- Create an executable file called `Rummage Here...` in `~/.local/share/nautilus/scripts/` with the following content (RUMMAGE_PATH should be the binary created when installing rummage in Python which is usually `/usr/local/bin/rummage`).

    ```py3
    #!/usr/bin/python
    import os
    import subprocess

    RUMMAGE_PATH = "/usr/local/bin/rummage"

    selected_paths = os.environ.get("NAUTILUS_SCRIPT_SELECTED_FILE_PATHS", None)
    if selected_paths is not None:
        paths = selected_paths.split("\n")
        if len(paths):
            subprocess.Popen([RUMMAGE_PATH, "--path", paths[0]])
    ```

- Restart of Nautilus may or may not be needed, but context menu item should appear under `Scripts` and should work on files and folders.

## Localization

Rummage provides an i18n localization framework to allow support for displaying the UI in other locales. Currently the project only has an incomplete Russian translation (I don't speak Russian, so I can't complete it).

Translations should be compiled and included by default requiring no additional steps starting in version 3.6.0.

I only speak English, so I do not maintain the translations. If the UI changes, someone from the community will need to update them appropriately via pull requests or they will remain out of date.

### Editing Existing Translations

Translations are stored at `rummage/lib/gui/localization/locale/<LOCALE>/LC_MESSAGES/rummage.po`. Just edit the `rummage.po` for the appropriate `<LOCALE>`.

Inside each `.po` file there will be a `msgid` for each unique translatable string.  Each `msgid` represents the actual US English text that is shown in Rummage. Underneath each `msgid`, you'll also find a `msgstr` which represents the translation for the `msgid`. Just edit the corresponding `msgstr` for each `msgid` in the existing `rummage.po` file.

```
msgid "About"
msgstr "<my_translation>"
```

### Generate New Template from Source

In the Python source, you'll notice that translatable strings are represented as `_("some text")`. `_` is the function that retrieves the proper translations. In order to provide translations, we have to build up a template of all of these strings in a `.pot` file.  This is done by running:

```
python setup.py extract_messages
```

This will scan the Python source and generate a template at `rummage/lib/gui/localization/locale/rummage.pot`.

If you update the source in a way that requires generating a new `.pot` file, then you will most likely need to update existing `.po` files as well. See [Update Translation Files](#update-translation-files) to see how.

See Babel's documentation on [`extract_messages`][babel_extract_messages] for more info.

### Update Translation Files

When new strings are added in the source, or strings are changed, you will need to re-generate the `.pot` file and then update the `.po` files. This should update all `.po` files.

```
python setup.py update_catalog
```

If you need to only update a specific `.po` file:

```
python setup.py update_catalog -l en_US
```

See Babel's documentation on [`update_catalog`][babel_update_catalog] for more info.

### Create New Translations

To create a translation `.po` file to edit, all you need to do is run the command below specifying your locale. The command should create a `.po` file to edit and the associated directory structure.

```
python setup.py init_catalog -l en_US
```

See Babel's documentation on [`init_catalog`][babel_init_catalog] for more info.

### Build Translations

Building translations is also pretty easy:

```
python setup.py compile_catalog
```

This should build `.mo` files for all languages.  See Babel's documentation on [`compile_catalog`][babel_compile_catalog] for more info.

--8<-- "refs.md"
