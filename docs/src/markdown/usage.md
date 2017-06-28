# User Guide

## Overview

Rummage is designed to be easy to pick up. Rummage's interface consists of three tabs: Search, Files, and Content.  In general, a user specifies where they want to search, what they want to search for, and optionally what they want to replace it with.  Search features can be tweaked with toggles, and the files that get searched can be narrowed with filters.  Search and replace options are all contained in the **Search** tab.  When a search has been completed, general info about the matches found in files will be displayed in the **Files** tab, and more detailed context information will be displayed in the **Content** tab.

Rummage also comes with a simple regular expression tester to test out patterns. It also provides a feature where patterns can be saved for later and/or frequent use.

The status bar will show search progress, match counts, and other useful information.

!!! warning "Warning: Replace"
    When replacing, Rummage will back up the file in `<your file name>.rum-bak`.  If the copy fails, it should terminate the replace for that file.  You can disable backups if you like, but if you aren't careful with your patterns, you may remove unwanted text that you won't be able to recover unless you are using version control.

    This is free software, and I am not responsible for files corrupted or lost.

## Running

After installation, you should then be able to access Rummage from the command line.  This assumes the Python bin directory is in the path.

```bash
rummage
```

Or specify a path:

```bash
rummage --path mydirectory
```

You can also run rummage by calling your specific python version like this:

```bash
python3 -m rummage --path mydirectory
```

## Search Tab

![Search Tab](/images/search_tab.png)

The **Search** tab is broken up into 2 panels, the first of which is the **Search &amp; Replace** panel. The **Search &amp; Replace** panel has all the inputs where the search and replace is defined and configured.  It also has access to the regular expression tester and the save/load dialogs for saving/loading patterns for later use.

The second panel, is the **Limit Search** panel.  The **Limit Search** panel contains toggles and inputs that filter the files to be searched.

## Files Tab

![Files Tab](/images/files_tab.png)

The **Files** tab is where files with matches are shown after a search completes.  The files are arranged in a sortable table.  Each entry will show the file's name, size, number of matches in the file, the file path, detected file encoding, date/time when the file was created, and date/time of when the file was last modified.

When mousing over an entry, the full path to the file will be shown in the status bar.  If you have the editor option in the preference dialog configured properly, you can double click an entry to open to the first match of that file in your favorite editor.

## Content Tab

![Content Tab](/images/content_tab.png)

The **Content** tab shows each match in a file individually. The entries will be arranged in a sortable table. Each entry shows the file's name, the line on which the match was found, the number of matches on that line, and the content of the line.  Long lines will be truncated.

When mousing over an entry, the full path to the file will be shown in the status bar.  If you have the editor option in the preference dialog configured properly, you can double click an entry to open to that specific match of that file in your favorite editor.

## Search &amp; Replace Panel

![Search and Replace Panel](/images/search_replace_panel.png)

The **Search &amp; Replace** panel contains three text boxes with a dropdown history. The first text box defines **where to search**, the second defines **what to search for**, and the last defines **what to replace matches with** (this is only needed when doing replaces).  You can select previously used patterns and search targets by expanding the dropdown panel for the input.

Below the text boxes are toggles that control the regular expression engine's flags and/or features.  These will vary depending on which regular expression engine you are using as Rummage can be used with Python's default [Re][re] engine or the third party [Regex][regex] engine.  Both optionally can use the a special wrapper called Backrefs to add support for a couple special escapes.

Underneath the regular expression flags, are toggles for general Rummage search features.  These will alter search and/or replace behavior.

Lastly, Rummage provides buttons to launch a regular expression tester dialog or dialogs to save or load frequently used regular expressions.

### Common Regular Expression Flags

Both the Re and Regex engine have a couple of shared flags that are exposed in Rummage. These toggles are found directly under the search and replace text boxes.

Toggle                   | Description
------------------------ | -----------
Search\ with\ regex      | Alters the behavior of `Search for` and `Replace with`.  When this is checked, both text boxes require regular expression patterns opposed to literal string.
Search\ case-sensitive   | Forces the search to be case-sensitive.
Dot\ matches\ newline    | `.` will also match newlines.
Use\ Unicode\ properties | Changes the behavior of `\w`, `\W`, `\b`, `\B`, `\d`, `\D`, `\s`, and `\S` to use use characters from the Unicode property database (will also modify `\l`, `\L`, `\c`, and `\C` in search patterns if using Backrefs with Re).

### Regex Engine Flags

If the Regex engine is being used for regular expressions, a couple of extra toggles will be available. Regex can be run in either `VERSION0` or `VERSION1` mode.  `VERSION0` is compatible with Re regular expression patterns and has the extra `fullcase` toggle.  `VERSION1` does not have this toggle as it is enabled by default and can only be disabled inline via a pattern with `(?-f)`. `VERSION1` is not directly compatible with Re patterns as it adds a number of changes to the syntax allowing for more advanced search options.

Toggle                      | Description
--------------------------- | -----------
Best\ fuzzy\ match          | If performing a fuzzy match, the *best* fuzzy match will be used.
Improve\ fuzzy\ fit         | Makes fuzzy matching attempt to improve the fit of the next match that it finds.
Unicode\ word\ breaks       | Will use proper Unicode word breaks when Unicode is enabled.  This differs from Re's default.
Search\ backwards           | Search backwards. The result of a reverse search is not necessarily the reverse of a forward search.
Format\ style\ replacements | Replace pattern will use [Python's string replace format][format-string] for replace. `#!python "{1[-1]} {1[-2]} {1[-3]}"` etc.
Full\ case-folding          | Use full case folding. For Regex `V0` only as it is enabled by default for `V1`.

### Rummage Flags

Rummage has a couple of flags that are not specific to the regular expression engine.

Toggle                  | Description
----------------------- | -----------
Boolean\ match          | Will check each file up until the first match and will halt searching further.  No line context info will be gathered or displayed. Does not apply when performing replaces.
Count\ only             | Will just count the number of matches in the file and will not display line context information. This has no effect when applying replaces.
Create\ backups         | On replace, files with matches will be backed up before applying the replacements; backup files will have the `.rum-bak` extension.
Force\ &lt;encoding&gt; | Forces all files to be opened with the specified encoding opposed to trying to detect the encoding.  Encoding is hard and slow, so this is the preferred method for fast searches.  On failure, binary will be used instead.

### Regular Expression Tester

![Regex Tester](/images/regex_tester.png)

Rummage comes with a simple regular expression tester.  It has a simple multi-line text box for content to search, and another multi-line box that will show the final results after the find and replace.  Below that you will find two text input boxes for the find pattern and the replace pattern.  Lastly, all related regular expression flag toggles will be found under the patterns.

To use the tester, simply enter the content to search, set your desired toggles, and input your find and replace pattern.  As you change your pattern or change your toggles, matches will be updated and highlighted, and the result box will be updated.

When you are satisfied with your result, click the `Use` button, and your pattern and settings will be populated in the main window.

### Saving and Loading Regular Expressions

Regular expressions can be very complex, and sometimes you might want to save them for future use to save yourself from having to reconstruct them.

When you have a pattern configured that you want to save, simply click the `Save Search` button, and a dialog will pop up asking you to name the search.  When done, click the `Save` button on the dialog and your search patterns and toggles will be saved.

![Save Search](/images/save_search.png)

To load a pattern that was saved previously, click the `Load Search` button.  You will be presented with a dialog showing all your saved searches.  Highlight the pattern you want to load and click the `Load` button.  Your pattern and toggles will be populated in the main dialog.

![Load Search](/images/load_search.png)

## Limit Search Panel

![Limit Search Panel](/images/limit_search_panel.png)

The limit search pattern contains inputs and toggles to filter which files will be searched.  Some people may like to set up the filters and hide the panel.  If this is desired, you can select in the window's menu **View-->Hide Limit Search Panel**, and the panel will be hidden.

Limiter                | Description
---------------------- |------------
Size\ of               | Limits files that are searched by size in Kilobytes.  Files are limited by whether they are greater than, less than, or equal to the specified size.  Setting the dropdown to `any` disables the filter and allows any file size to be searched. It is recommended to cap search sizes in projects with very large files for the best performances.  The more complex the search pattern, the longer it will take to search a really large file.
Modified               | Limits the files to be searched by the modified timestamp.  It contains a date picker and time picker that are used to specify the target date and time. Files are limited by whether their timestamp comes before, after, or on specified date time.  Setting the dropdown to `on any` will disable the filter and allow a file with any timestamp to be searched.
Created                | Limits the files to be searched by the creation timestamp.  It contains a date picker and time picker that are used to specify the target date and time. Files are limited by whether their timestamp comes before, after, or on specified date time.  Setting the dropdown to `on any` will disable the filter and allow a file with any timestamp to be searched.
Files\ which\ match    | Specifies a file pattern for files that should be searched.  Multiple file patterns can be specified with `;` used as a separator. If the Regex toggle to the text box's right is selected, the file pattern must be a regular expression pattern.  You can select previously used patterns by expanding the dropdown panel for the input.
Exclude\ folders       | Specifies a directory exclude pattern to filter out folders that are not to be crawled.  Multiple file patterns can be specified with `;` used as a separator.  If the Regex toggle to the text box's right is selected, the file pattern must be a regular expression pattern.  You can select previously used patterns by expanding the dropdown panel for the input.
Include\ subfolders    | Indicates that folders should be recursively searched.
Include\ hidden        | The given OS's native hidden files, folders and dotfiles will be included in the search.
Include\ binary\ files | Forces Rummage to search binary files.

!!! tip "Tip"
    If you don't specify a search pattern, Rummage will use your file filter and just show files that match your file filter pattern.

## Export to CSV or HTML

![HTML Export](/images/html_export.png)

Rummage allows the exporting of the results to either CSV or HTML.  Simply select **File-->Export** and pick either **CSV** or **HTML**.  The HTML output will be styled similar to the GUI interface with the results in tables with sortable columns.

!!! note "Note":
    Really, really large sets of results will probably be best suited for CSV as a browser may have a hard time loading the entire data set at once.

## Preferences

![Preferences](/images/preferences.png)

The preference dialog (found at **File-->Preferences**) is where Rummage keeps settings that are not frequently accessed.

### Editor

The **Editor** panel is where an editor can be configured that will be used to show files for editing.  To setup, click the `Change` button.  You will be presented with a dialog where you can browse for your editor of choice and manage the arguments to pass to the editor.

![Editor Options](/images/editor_options.png)

The editor options dialog has a file picker to select the the editor.  In macOS it may be beneficial to create a shell script or symlink that you can references as the picker won't be able to descend into an `.app` bundle as it is viewed as a file instead of a folder.

You can then add arguments.  Each argument must be added as a separate entry.  So something like `--file myfile.txt` would be counted as **two** arguments while `--file=myfile` would be counted as one.

As noted in the image above, Rummage provides 3 special variables that can be used to insert the file name, line number, or column number.

Argument Variables | Description
------------------ | -----------
\{$file}           | Insert the file name.
\{$line}           | Insert the line number.
\{$col}            | Insert the column number.

### General
The **General** panel contains a couple of useful settings.

Single Instance
: 
    By default, Rummage will allow for multiple windows to be open.  If this option is enabled, the first window will be be the only window to open.  All subsequent instances will pass their arguments to the first and close without showing a window.

Language
: 
    Rummage has internal support to display dialog labels in different languages. Currently Rummage has English. Russian is outdated but includes most of the needed translations. In order to use locale, you must copy the project's localization files to your user settings directory. See [Localization](#localization) to learn more.

### Regular Expression Modules

The **Regular Expression Modules** panel is where the desired regular expression engine that Rummage uses can be selected.  By default, Rummage will use Re, but if Regex is installed in your Python installation, it can be selected instead.  There is also the options of using Re or Regex with [Backrefs](#backrefs-extended-regex-escapes) (a wrapper that adds a couple of special escapes) with your engine of choice as well.

If using Regex, you can set it to version (mode) to use. `V0` tries to be completely compatible with Re patterns while `V1` breaks compatibility with Re and adds even more useful features. Please see [Regex documentation](https://pypi.python.org/pypi/regex/) to learn more.

### Notifications

The **Notification** panel controls enabling/disabling and configuration of notifications.  You can enable/disable visual notifications and/or audible notification sounds.

You can also select whether to use the system's built-in notifications or Growl.

Ubuntu
: 
   - Growl: [Support for Linux][growl-linux].
   - Native: OSD via `notify-send`.

    !!! Note "Note"
        Though Rummage should run on any Linux distro, the native dialog option was built around Ubuntu's native notifications called OSD.  Notifications will not work on other distros that do not use OSD *unless* they use Growl.  Even without Growl, other distros will probably still get the audible cue, but as each distro varies, it is difficult to be certain.  As notifications are not crucial to usage, this is minor concern.

macOS
: 
    - Growl: [Support for macOS][growl-macos].
    - Native: Notification Center via [terminal-notifier][terminal-notifier]. Path to `terminal-notifier` must be configured.

    !!! Note "Note"
        When selecting `native` on macOS, an option to select the path to terminal notifier will be available since native dialogs rely on `terminal-notifier` to send notifications to the Notification Center. This must be configured or *native* notifications will not work.

        When selecting the `terminal-notifier` path, you can select either the binary directly or the `.<app` bundle (depending on how you installed `terminal-notifier`).  When selecting the `.app` bundle, Rummage will know how to access the binary inside the bundle.

Windows
: 
    - Growl: [Support for Windows][growl-win].
    - Native: Native windows taskbar notifications.


### History

The **History** panel is where all text box drop down history can be cleared.

## Backrefs (Extended Regex Escapes)

Rummage has the option of using a special wrapper called Backrefs around Python's Re or the 3rd party Regex module. Backrefs was written specifically for use with Rummage and adds various additional back references that are known to some regex engines, but not to Python's Re or Regex modules.  The supported back references actually vary depending on the engine being used as one may already have similar support.  You can enable extended back references in the **Preferences** dialog under the [Regular Expressions Module](#regular-expression-modules) panel.

To learn more about the added back references when using Backrefs, read the official [Backrefs documentation][backrefs].


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
        (/Library/Frameworks/Python.framework/Versions/2.7/bin/rummage --path "$1")>/dev/null 2>&1 &
        ```

        This is just an example. You will need to determine the location of your Python install.

- Save to `/Users/<username>/Library/Services/Rummage Here...`.

### Windows

- Create a file `rummage.reg` and put the following in it (replace &lt;rummage_path&gt; path with the actual path to   `rummage.exe` that is created in your Python Script folder on installation).  Remember to escape backslashes appropriately.  This isn't a guide in how to do registry editing proper, so only edit the registry if you are certain of what you are doing.

    ```ini
    Windows Registry Editor Version 5.00

    [HKEY_CLASSES_ROOT\Folder\shell\Rummage Here...]
    @=""

    [HKEY_CLASSES_ROOT\Folder\shell\Rummage Here...\command]
    @="\"<rummage_path>\" \"--path\" \"%1\""

    [HKEY_CLASSES_ROOT\*\shell\Rummage Here...]
    @=""

    [HKEY_CLASSES_ROOT\*\shell\Rummage Here...\command]
    @="\"<rummage_path>\" \"--path\" \"%1\""

    ```

- Save file.
- Double click the registry file to add the context menu into Windows Explorer.

### Linux

There are many different flavors of Linux using different file managers.  This makes it difficult to give a guide to cover all cases.  Please research about your specific distro's file manager and how to add context menus.  If you would like to include the info here, please issue a pull request to update the documentation.

#### Ubuntu Nautilus

Paths might vary depending on Ubuntu version etc.

- Create an executable file called `Rummage Here...` in `~/.local/share/nautilus/scripts/` with the following content (RUMMAGE_PATH should be the binary created when installing rummage in Python which is usually `/usr/local/bin/rummage`).

    ```py
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

Rummage provides an i18n localization framework to allow support for displaying the UI in other languages. But there is some manual setup required as out of the box, only `en_US` is available. Currently the project only has an incomplete Russian translation (I don't speak Russian, so I can't complete it).

### Installing Translations

To install translations, just copy the `locale` folder from the release you are using to your user configuration folder.  For a traditional Python installation, this is where you'd find it for each OS:

Windows: `C:\Users\<my_username>\.Rummage`
macOS: `/Users/<my_username>/.Rummage`
Linux: `/home/<my_username>/.config/Rummage`

Unless the UI changes by adding new untranslated strings, you can keep using the same translations.

After installing the localization files, set the language via the `Language` setting in the settings [General panel](#general).

### Adding New Translations

- Clone the project and create a new folder under `locale` with the appropriate locale name.
- Create another folder under the one you just created called `LC_MESSAGES`.
- Copy `locale/messages.po` to `locale/<my_LOCALE>/LC_MESSAGES/rummage.po`.
- Edit the copied file changing things like:

    ```
    msgid "About"
    msgstr ""
    ```

    To:

    ```
    msgid "About"
    msgstr "<my_translation>"
    ```

- Compile `.mo` files by running the `tools/localize_me.py` script from the root of the project:

    ```
    python3 tools/localize_me.py --i18n /Library/Frameworks/Python.framework/Versions/3.6/share/doc/python3.6/examples/Tools/i18n
    ```

    Modify the `--i18n` path to the appropriate location of the `i18n` folder for your Python.

- Commit, push, and pull request.


I only speak English, so I do not maintain the translations. If the UI changes, someone from the community will need to update them appropriately via pull requests or they will remain out of date.

--8<-- "links.md"
