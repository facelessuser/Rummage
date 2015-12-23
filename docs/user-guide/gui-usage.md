# Using Rummage {: .doctitle}
Detailed usage for rummage.

---

## Overview
Rummage is designed to be easy to pick up. Rummage's interface consists of three tabs: Search, Files, Content.  In general, a user specifies where they want to search, what they want to search for, and optionally what they want to replace it with.  Search features can be tweaked with toggles, and the files that get searched can be narrowed with filters.  Search options are all contained in the **Search** tab.  When a search has been completed, general info about matches found in files will be displayed in the **Files** tab, and more detailed context information will be displayed in the **Content** tab.

Rummage also comes with a simple regex tester to test out patterns, and a feature where patterns can be saved for later and/or frequent use.

The status bar will show search progress, match counts, and other useful information.

!!! caution "Warning: Replace"
    When replacing, Rummage will back up the file in `<your file name>.rum-bak`.  If the copy fails, it should terminate the replace for that file.  You can disable backups if you like, but if you aren't careful with your patterns, you may remove unwanted text that you won't be able to recover unless you use version control.  If using encoding guessing, Rummage *might* guess the wrong encoding causing some things to get lost during replace.  And aside from those issues, something unexpected *could* always occur as well, but hopefully not as Rummage is been trough a lot of testing.

    In short, if you disable backups, there is a greater risk as you will no longer have a safety net.  Even with backups, something *could* go wrong.  This is free software, and I am not responsible for files corrupted or lost.

    Large files, really large files, can possibly cause an issue and may error out as the entire file will be read into memory for a replace.  If you are doing really large files, know that it may error out or get really slow.  Remember this is done in Python, if you are doing massive GB files, maybe you are using the wrong tool for the job.

## Search Tab

![Search Tab](../images/search_tab.png)

The **Search** tab is broken up into 2 panels, the first of which is the **Search &amp; Replace** panel. The **Search &amp; Replace** panel has all the inputs where the search and replace is defined and configured.  It also has access to the regex tester and the save/load dialogs for saving patterns for later use.

The second panel, is the **Limit Search** panel.  The **Limit Search** panel contains toggles and inputs that filter the files to be searched.

## Files Tab

![Files Tab](../images/files_tab.png)

The **Files** tab is where files with matches are shown after a search completes.  The files are arranged in a sortable table.  Each entry will show the files name, file size, number of matches in the file, the file path, detected file encoding, date/time when the file was created, and date/time of when the file was last modified.

When mousing over an entry, the full path to the file will be shown in the status bar.  If you have the editor option in the preference dialog configured properly, you can double click an entry to open the file in your favorite editor.

## Content Tab

![Content Tab](../images/content_tab.png)

The **Content** tab shows each match in a file individually in a sortable table.  Each entry shows the file name, the line on which the match was found, the number of matches on that line, and the content of the line.  Long lines will be truncated. 

When mousing over an entry, the full path to the file will be shown in the status bar.  If you have the editor option in the preference dialog configured properly, you can double click an entry to open the file in your favorite editor.

## Search &amp; Replace Panel

![Search and Replace Panel](../images/search_replace_panel.png)

The **Search &amp; Replace** panel contains three text boxes with a dropdown history. The first textbox defines **where to search**, the second defines **what to search for**, and the last defines **what to replace matches with** (this is only needed when doing replaces).  You can select previously used patterns and search targets by expanding the dropdown panel for the input.

Below the text boxes are toggles that control the regex engines flags and/or features.  These will vary depending on which regex engine you are using as Rummage can be used with Python's default [**re**](https://docs.python.org/2/library/re.html) engine or the third party [**regex**](https://pypi.python.org/pypi/regex) engine.  Both optionally can use the a special wrapper called **backrefs** to add support for a couple special escapes.

Underneath the regex flags, are toggles for general Rummage search features.  These will alter search and/or replace behavior.

Lastly, Rummage provides buttons to launch a regex test window or to save and load frequently used regular expressions.

### Common Regular Expression Flags
Both the **re** and **regex** engine have a couple of shared flags that are exposed in Rummage. These toggles are found directly under the search and replace text boxes.

| Toggle | Description |
|--------|-------------|
| Search with regex | Alters the behavior of `Search for` and `Replace with`.  When this is checked, both text boxes require regular expression patterns opposed to literal string. |
| Search case-sensitive | Forces the search to be case-sensitive. |
| Dot matches newline | `.` will also match newlines. |
| Use Unicode properties | Changes the behavior of `\w`, `\W`, `\b`, `\B`, `\d`, `\D`, `\s`, and `\S` to use use characters from the Unicode property database (will also modify `\l`, `\L`, `\c`, and `\C` if using **backrefs** with **re**). |

### Regex Engine Flags
If the **regex** engine is being used for regular expressions, a couple of extra toggles will be available.  **Regex** can be run in either `VERSION0` or `VERSION1` mode.  `VERSION0` is compatible with **re** regex patterns and has the extra `fullcase` toggle.  `VERSION1` does not have this toggle as it is enabled by default and can only be disabled inline in a pattern with `(?-f)`. `VERSION1` is not directly compatible with **re** as it adds a number of changes to the syntax allowing for more advanced search options.

| Toggle | Description |
|--------|-------------|
| Best fuzzy match | If performing a fuzzy match, the *best* fuzzy match will be used. |
| Improve fuzzy fit | Makes fuzzy matching attempt to improve the fit of the next match that it finds. |
| Unicode word breaks | Will use proper Unicode word breaks when Unicode is enabled.  This differs from **re**'s default. |
| Search backwards | Search backwards. The result of a reverse search is not necessarily the reverse of a forward search. |
| Format style replacements | Replace pattern will use [Python's string replace format](https://docs.python.org/2/library/string.html#format-string-syntax) for replace. `#!python "{1[-1]} {1[-2]} {1[-3]}"` etc. |
| Full case-folding | Use full case folding. Regex `V0` only as it is enabled by default for `V1`. |

### Rummage Flags
Rummage has a couple of flags that are not specific to the regular expression engine.

| Toggle | Description |
|--------|-------------|
| Boolean match | Will check each file up until the first match and will then move on.  No line context info will be gathered or displayed. Does not apply to replaces. |
| Count only | Will just count the number of matches in the file, but will not display line context information. This has no effect or replaces. |
| Create backups | On replace, files with matches will be backed up before applying the replacements; backup files will have `.rum-bak` extension. |
| Force &lt;encoding&gt; | Forces all files to be opened with the specified encoding opposed to trying to detect the encoding.  Encoding is hard and slow, so this is the preferred method for fast searches.  On failure, binary will be used instead. |

### Regex Tester

![Regex Tester](../images/regex_tester.png)

Rummage comes with a simple regex tester.  It has a simple multi-line text box for content to search, and another multi-line box that will show the final results after the find and replace.  Below that you will find two text input boxes for the find pattern and the replace pattern.  Lastly, all related regular expression flag toggles will be found under the patterns.

To use the tester, simply enter the content to search, set your desired toggles, and input your find and replace pattern.  As you change your pattern or change your toggles, matches will be updated and highlighted, and the result box will be updated.

When you are satisfied with your result, click the `Use` button, and your pattern and settings will be populated in the main window.

### Saving and Loading Regular Expressions
Regular expressions can be very complex, and sometimes you might want to save them for future use to save yourself from having to reconstruct them.

When you have a pattern configured that you want to save, simply click the `Save Search` button, and a dialog will pop up asking you to name the search.  When done, click the `Save` button on the dialog and your search patterns and toggles will be saved.

![Save Search](../images/save_search.png)

To load a pattern that was saved previously, click the `Load Search` button.  You will be presented with a dialog showing all your saved searches.  Highlight the pattern you want to load and click the `Load` button.  Your pattern and toggles will be populated in the main dialog.

![Load Search](../images/load_search.png)

## Limit Search Panel

![Limit Search Panel](../images/limit_search_panel.png)

The limit search pattern contains inputs and toggles to filter which files will be searched.  Some people may like to set up the filters and hide the panel.  If this is desired, you can select in the windows menu **View-->Hide Limit Search Panel**, and the panel will be hidden.

| Limiter | Description |
|---------|-------------|
| Size of | Limits files that are searched by size in Kilobytes.  Files are limited by whether they are greater than, less than, or equal to the specified size.  Setting the dropdown to `any` essential disables the filter and allows any file size to be searched. It is recommended to cap searches sizes for the best performances.  The more complex the search pattern, the longer it will take to search really large files. |
| Modified | Limits the files to be searched by the modified timestamp.  It contains a date picker and time picker that are used to specify the target date and time. Files are limited by whether their timestamp comes before, after, or on specified date time.  Setting the dropdown to `on any` essential disables the filter and allows a file with any timestamp to be searched. |
| Created | Limits the files to be searched by the creation timestamp.  It contains a date picker and time picker that are used to specify the target date and time. Files are limited by whether their timestamp comes before, after, or on specified date time.  Setting the dropdown to `on any` essential disables the filter and allows a file with any timestamp to be searched. |
| Files which match | Specifies a file pattern for files that should be searched.  Multiple file patterns can be specified with `;` used as a separator. If the Regex toggle to the text box's right is selected, the file pattern must be a regular expression pattern.  You can select previously used patterns by expanding the dropdown panel for the input. |
| Exclude folders | Specifies a directory exclude pattern to filter out folders that are not to be crawled.  Multiple file patterns can be specified with `;` used as a separator.  If the Regex toggle to the text box's right is selected, the file pattern must be a regular expression pattern.  You can select previously used patterns by expanding the dropdown panel for the input. |
| Include subfolders | Indicates that folders should be recursively searched. |
| Include hidden | The given OS's native hidden files, folders and dotfiles will be included in the search. |
| Include binary files | Forces rummage to search binary files. |

## Export to CSV or HTML

![HTML Export](../images/html_export.png)

Rummage allows the exporting of the results to either CSV or HTML.  Simply select **File-->Export** and pick either **CSV** or **HTML**.  The HTML output will be styled similar to the GUI interface with the results in tables with sortable columns.

!!! note "Note":
    Really, really large sets of results will probably be best suited for CSV as a browser may have a hard time loading the entire data set at once.

## Preferences

![Preferences](../images/preferences.png)

The preference dialog (found at **File-->Preferences**) is where Rummage keeps settings that are not frequently accessed.

### Editor
The **Editor** panel is where an editor can be configured that will be used to show files for editing.  To setup, click the `Change` button.  You will be presented with a dialog where you can browse for your editor of choice and manage the arguments to pass to the editor.

![Editor Options](../images/editor_options.png)

The editor options dialog has a file picker to select the the editor.  In OSX it may be beneficial to create a shell script or symlink that you can references as the picker won't be able to descend into an `.app` bundle as it is viewed as a file instead of a folder.

You can then add arguments.  Each argument must be added as a separate entry.  So something like `--file myfile.txt` would be counted as **two** arguments while `--file=myfile` would be counted as one.

As noted in the image above, Rummage provides 3 special variables that can be used to insert the file name, line number, or column number.

| Argument Variables | Description |
|--------------------|-------------|
| \{$file} | Insert the file name. |
| \{$line} | Insert the line number. |
| \{$col}  | Insert the column number. |

### General
The **General** panel contains a couple of useful settings.

Single Instance
: 
    By default, Rummage will allow for multiple windows to be open.  If this option is enabled, the first window will be be the only window to open.  All subsequent instances will pass their arguments to the first and close without showing a window.

Language
: 
    Rummage has internal support to display dialog labels in different languages.  Currently Rummage has English and most of Russian.

### Regular Expression Modules
The **Regular Expression Modules** panel is where the desired regular expression engine that Rummage uses can be selected.  By default, Rummage will use **re**, but if **regex** is installed in your Python installation, it can be selected as well.  There is also the option of using [backrefs](#backrefs-extended-regex-escapes) (a wrapper that adds a couple of special escapes) with your engine of choice as well.

If using **regex**, you can set it the version (mode) to use.  `V0` tries to be completely compatible with **re**.  `V1` breaks compatibility with **re** but adds a number of useful additions even over **V0**.

### Notifications
The **Notification** panel controls enabling/disabling and configuration of notifications.  You can enable/disable notification popups and/or audible notification sound.

You can also select whether to use the systems built in notifications or growl.

Ubuntu
: 
   - Growl: Support for Linux - http://mattn.github.io/growl-for-linux/.
   - Native: OSD via `notify-send`.

    !!! Note "Note"
        Though Rummage should run on any Linux distro, the native dialog option was built around Ubuntu's native notifications called OSD.  Notifications will not work on other distros that do not use OSD **unless** they use Growl.  Even without Growl, other distros will probably still get the audible cue but, as each distro varies; it is difficult to be certain.  As notifications are not crucial to usage, this is minor concern.

OSX
: 
    - Growl: Support for OSX - http://growl.info/.
    - Native: Notification Center via [terminal-notifier](https://github.com/alloy/terminal-notifier). Path to `terminal-notifier` must be configured.

    !!! Note "Note"
        When selecting `native` on OSX, an option to select the path to terminal notifier will be available since native dialogs rely on `terminal-notifier` to send notifications to the Notification Center. This must be configured or *native* notifications will not work.

        When selecting the `terminal-notifier` path, you can select either the binary directly or the `.<app` bundle (depending on how you installed `terminal-notifier`).  When selecting the `.app` bundle, Rummage will know how to access the binary inside the bundle.

Windows
: 
    - Growl: Support for Windows - http://www.growlforwindows.com/gfw/.
    - Native: Native windows taskbar notifications.


### History
The **History** panel is where all text box drop down history can be cleared.

## Backrefs (Extended Regex Escapes)
Rummage has the option of using a special wrapper around Python's **re** or **regex** library called backrefs.  Backrefs was written for use with Rummage and adds various additional backrefs that are known to some regex engines, but not to Python's **re** or **regex**.  The supported back references actually vary depending on the engine being used as one may already have support.  You can enable extended back references in the **Preferences** dialog under the [Regular Expressions Module](#regular-expression-modules) panel.

### Search Back References

For **re**:

| Back&nbsp;References | Description |
| ---------------------|-------------|
| `\c`                 | Uppercase character class.  ASCII or Unicode when re Unicode flag is used.  Can be used in character classes `[]`. |
| `\l`                 | Lowercase character class.  ASCII or Unicode when re Unicode flag is used.  Can be used in character classes `[]`. |
| `\C`                 | Inverse uppercase character class.  ASCII or Unicode when re Unicode flag is used.  Can be used in character classes `[]`. |
| `\L`                 | Inverse lowercase character class.  ASCII or Unicode when re Unicode flag is used.  Can be used in character classes `[]`. |
| `\Q...\E`            | Quotes (escapes) text for regex.  `\E` signifies the end of the quoting. Will be ignored in character classes `[]`. |
| `\p{UnicodeProperty}`| Unicode property character class. Search string must be a Unicode string. Can be used in character classes `[]`. See [Unicode Properties](#unicode-properties) for more info. |
| `\P{UnicodeProperty}`| Inverse Unicode property character class. Search string must be a Unicode string. Can be used in character classes `[]`. See [Unicode Properties](#unicode-properties) for more info. |

For **regex**:

| Back&nbsp;References | Description |
| ---------------------|-------------|
| `\Q...\E`            | Quotes (escapes) text for regex.  `\E` signifies the end of the quoting. Will be ignored in character classes `[]`. |

### Replace Back References
None of the replace back references can be used in character classes `[]`.  These apply to both **re** and **regex**.

| Back&nbsp;References | Description |
| ---------------------|-------------|
| `\c`                 | Uppercase the next character. |
| `\l`                 | Lowercase the next character. |
| `\C...\E`            | Apply uppercase to all characters until either the end of the string or the end marker `\E` is found. |
| `\L...\E`            | Apply lowercase to all characters until either the end of the string or the end marker `\E` is found. |

!!! tip "Tip"
    Complex configurations of casing should work fine.

    - `\L\cTEST\E` --> `Test`
    - `\c\LTEST\E` --> `Test`
    - `\L\cTEST \cTEST\E` --> `Test Test`

### Unicode Properties
Unicode properties can be used with the format: `\p{property=value}`, `\p{property:value}`, `\p{value}`, `\p{^property=value}`, `\p{^value}`.  Though you don't have to specify the `UNICODE` flag, the search pattern must be a Unicode string and the search buffer must also be Unicode.  It supports `General_Category`, `Block`, 'Script', `Bidi_Class`, and binary properties. It should support most if not all their aliases.  In the future it is possible that more Unicode property support will be added, but the current set seems fairly reasonable.

The inverse of properties can also be used to specify everything not in a Unicode property: `\P{value}` or `\p{^value}` etc.  They are only used in the search patterns. Only one property may specified between the curly braces.  If you want to use multiple properties, you can place them in a character class: `[\p{UnicodeProperty}\p{OtherUnicodeProperty}]`.

When specifying a property, the value matching is case insensitive and characters like `[ -_]` will be ignored.  So the following are all equivalent: `\p{Uppercase_Letter}`, `\p{Uppercase-letter}`, `\p{UPPERCASELETTER}`, `\p{upper case letter}`.

When evaluating a property in the form `\p{value}`, they are evaluated in this order:

1. General Category
2. Script
3. Blocks
4. Binary
6. Posix Style properties

When installed, the Unicode version that comes with the Python it is installed under will be used to generate all the Unicode tables.  For instance, Python 2.7 is currently using Unicode 5.2.0.  And Python 3.5 is using 8.0.0.

!!! caution "Narrow Python Builds"
    If you are using a narrow python build, your max Unicode value will be `\uffff`.  Unicode blocks above that limit will not be available.  Also Unicode values above the limit will not be available in character classes either.

    If you are using a wide build, you should have access to all Unicode values.

#### General Category
General categories can be specified in one of three ways: `\p{gc: value}`, `\p{General_Category: value}`, `\p{value}` etc.  Again, case is not important.  See the table below to see all the Unicode category properties that can be used.

| Verbose&nbsp;Property&nbsp;Form | Terse&nbsp;Property&nbsp;Form |
|---------------------------------|-------------------------------|
| Other | C |
| Control | Cc |
| Format | Cf |
| Surrogate | Cs |
| Private_Use | Co |
| Unassigned | Cn |
| Letter | L |
| Cased_Letter | L& or Lc |
| Uppercase_Letter | Lu |
| Lowercase_Letter | Ll |
| Titlecase_Letter | Lt |
| Modifier_Letter | Lm |
| Other_Letter | Lo |
| Mark | M |
| Nonspacing_Mark | Mc |
| Spacing_Mark | Me |
| Enclosing_Mark | Md |
| Number | N |
| Decimal_Number | Nd |
| Letter_Number | Nl |
| Other_Number | No |
| Punctuation | P |
| Connector_Punctuation | Pc |
| Dash_Punctuation | Pd |
| Open_Punctuation | Ps |
| Close_Punctuation | Pe |
| Initial_Punctuation | Pi |
| Final_Punctuation | Pf |
| Other_Punctuation | Po |
| Symbol | S |
| Math_Symbol | Sm |
| Currency_Symbol | Sc |
| Modifier_Symbol | Sk |
| Other_Symbol | So |
| Separator | Z |
| Space_Separator | Zs |
| Line_Separator | Zl |
| Paragraph_Separator | Z |

#### Blocks
There are a number of Unicode blocks and also aliases for blocks (they won't be listed here), but they can be specified in two ways: `\p{Block: Basic_Latin}` or `\p{InBasic_Latin}`.

#### Scripts
There are a number of Unicode scripts and also aliases for scripts (they won't be listed here), but they can be specified in two ways: `\p{Script: Latin}` or `\p{IsLatin}`.

#### Binary
There are a number of binary properties and even aliases for some of the binary properties.  Comprehensive lists are available on the web, but they are specified in the following way: `\p{Alphabetic}`.  Normal just specifying inverse via `\P{value}` or `\p{^value}` should be enough, but for completeness the form `\p{Alphabetic: Y}` and `\p{Alphabetic: N}` along with all the variants (Yes|No|T|F|True|False).

#### Bidi Classes
Bidi classes must be defined in the form `\p{Bidi_Class: White_Space}` or `\p{bc: ws}` etc.

#### Posix
A number of posix property names are also available.  In general, when used in the `\p{}` form, they are aliases for existing unicode properties with the same name. There are some posix names that aren't used in the current Unicode properties `alnum`, `xdigit`, etc.  If you want to force the posix form inside `\p{}` you can use their name prefixed with `posix`: `\p{Punct}` --> `\p{PosixPunct}`.  Currently when using posix values in `\p{}` they will be forced into their Unicode form (see [Posix Style Properties](#posix-style-properties) for more info).

### Posix Style Properties
Posix properties in the form of `[:posix:]` and the inverse `[:^posix:]` are available.  These character classes are only available inside a character group `[]`.  If needed, you can use the alternate form of `\p{Posix}` to use inside and outside a character group.

!!! caution "Posix Values in `p{}`"
    If using the `\p{Posix}` form, the return will always be Unicode and properties like `punct` will revert to the Unicode property form opposed the posix unless `posix` is prefixed to the name.  Example: the Unicode property `punct` = `[\p{P}]`, but the posix `punct` = `[\p{P}\p{S}]`.

<table markdown="1" class="docutils">
<thead>
<tr>
<th>[:posix:]</th>
<th>\p{Posix}</th>
<th>ASCII</th>
<th>Unicode</th>
</tr>
</thead>
<tbody>
<tr>
<td>alnum</td>
<td>Alnum</td>
<td>`[a-zA-Z0-9]`</td>
<td>`[\p{L&}\p{Nd}]`</td>
</tr>
<tr>
<td>alpha</td>
<td>Alpha</td>
<td>`[a-zA-Z]`</td>
<td>`[\p{L&}]`</td>
</tr>
<tr>
<td>ascii</td>
<td>ASCII</td>
<td>`[\x00-\x7F]`</td>
<td>`[\x00-\x7F]`</td>
</tr>
<tr>
<td>blank</td>
<td>Blank</td>
<td>`[ \t]`</td>
<td>`[\p{Zs}\t]`</td>
</tr>
<tr>
<td>cntrl</td>
<td>Cntrl</td>
<td>`[\x00-\x1F\x7F]`</td>
<td>`[\p{Cc}]`</td>
</tr>
<tr>
<td>digit</td>
<td>Digit</td>
<td>`[0-9]`</td>
<td>`[\p{Nd}]`</td>
</tr>
<tr>
<td>graph</td>
<td>Graph</td>
<td>`[\x21-\x7E]`</td>
<td>`[^\p{Z}\p{C}]`</td>
</tr>
<tr>
<td>lower</td>
<td>Lower</td>
<td>`[a-z]`</td>
<td>`[\p{Ll}]`</td>
</tr>
<tr>
<td>print</td>
<td>Print</td>
<td>`[\x20-\x7E]`</td>
<td>`[\P{C}]`</td>
</tr>
<tr>
<td>punct</td>
<td>Punct</td>
<td>``[!\"\#$%&'()*+,\-./:;&lt;=&gt;?@\[\\\]^_`{}~]``</td>
<td>`[\p{P}\p{S}]`</td>
</tr>
<tr>
<td>space</td>
<td>Space</td>
<td>`[ \t\r\n\v\f]`</td>
<td>`[\p{Z}\t\r\n\v\f]`</td>
</tr>
<tr>
<td>upper</td>
<td>Upper</td>
<td>`[A-Z]`</td>
<td>`[\p{Lu}]`</td>
</tr>
<tr>
<td>xdigit</td>
<td>XDigit</td>
<td>`[A-Fa-f0-9]`</td>
<td>`[A-Fa-f0-9]`</td>
</tr>
</tbody>
</table>
