# Using Rummage {: .doctitle}
Detailed usage for rummage.

---

## Layout
Rummage is designed to be easy to pick up. Rummage's interface consists of three tabs: Search, Files, Content.  Each element is labeled to indicate its functionality, and they are grouped with like elements.  In general, a user specifies where they want to search, what they want to search for, and optionally what they want to replace it with.  Search features can be tweaked with toggles, and the scope of what files get searched can be narrowed with filters.  When a search has been completed, general info about matches in files will be displayed n the `Files` tab, and more detailed context information will be displayed in the `Content` tab.

### Search Tab
The first section of the Search tab is the "Search & Replace" panel which has all inputs where the search and replace is defined and configured.  The panel contains three text boxes with a dropdown history that a user inputs where to search, what to search, and what to replace matches with.

| Input | Description |
|-------|-------------|
| Search in | This can be either a folder path or file path.  When rummage is launched, this is usually populated with the current working directory, but it can be changed manually by entering text or using the file folder picker button just to the right to select the location.  If typing, the box will show autocomplete options from the history.  The dropdown button can also be clicked to allow for manually selection of a an entry in the history. |
| Search for | This is where the search pattern is entered.  This can be either a regex pattern (if `Search with regex` is selected) or a literal pattern.  When typing, the box will show autocomplete options from the history.  The dropdown button can also be clicked to allow for manually selection of a an entry in the history. |
| Replace with | This is where a replace string or pattern is entered for use when replacing matches.  If `Search with regex` is selected, the replace pattern should be a regex replace pattern.  When typing, the box will show autocomplete options from the history.  The dropdown button can also be clicked to allow for manually selection of a an entry in the history. |

Under the text box, there are a number of toggles for different search related features.

| Toggle | Description |
|--------|-------------|
| Search with regex | Alters the behavior of `Search for` and `Replace with`.  When this is checked, both text boxes require regular expression patterns. |
| Search case-sensitive | Forces the search to be case-sensitive. |
| Dot matches newline | `.` will also match newlines. |
| Use Unicode properties | Changes the behavior of `\w`, `\W`, `\b`, `\B`, `\d`, `\D`, `\s`, `\S`, `\l`, `\L`, `\c`, and `\C` to use use characters from the Unicode property database. |
| Boolean match | Will check each file only up until the first match.  Does not apply to replaces. |
| Count only | Will just count the number of matches in the file, but will not display line context information. |
| Create backups | On replace, files with matches will be backed up before applying the replacements. |
| Force &lt;encoding&gt; | Forces all files to be opened with the specified encoding.  On failure, binary will be used instead. |

The second section is the `Limit Search` panel.  This panel contains options to limit which files are searched.

| Limiter | Description |
|---------|-------------|
| Size of | Limits files that are searched by size in Kilobytes.  Files are limited by whether they are greater than, less than, or equal to the specified size.  Setting the dropdown to `any` essential disables the filter and allows any file size to be searched. |
| Modified | Limits the files to be searched by the modified timestamp.  It contains a date picker and time picker that are used to specify the target date and time. Files are limited by whether their timestamp comes before, after, or on specified date time.  Setting the dropdown to `on any` essential disables the filter and allows a file with any timestamp to be searched. |
| Created | Limits the files to be searched by the creation timestamp.  It contains a date picker and time picker that are used to specify the target date and time. Files are limited by whether their timestamp comes before, after, or on specified date time.  Setting the dropdown to `on any` essential disables the filter and allows a file with any timestamp to be searched. |
| Files which match | Specifies a file pattern to filter files to be searched.  Multiple file patterns are can be specified with `;` used as a separator. If the Regex toggle to the textbox's right is selected, the file pattern must be a regular expression pattern. When typing, the box will show autocomplete options from the history.  The dropdown button can also be clicked to allow for manually selection of a an entry in the history. |
| Exclude folders | Specifies a pattern that is use to exclude certain folders from being crawled.  If the Regex toggle to the textbox's right is selected, the file pattern must be a regular expression pattern. When typing, the box will show autocomplete options from the history.  The dropdown button can also be clicked to allow for manually selection of a an entry in the history. |
| Include subfolders | Indicates that folders should be recursively searched. |
| Include hidden | This will include the given OS's native hidden files and dotfiles. |
| Include binary files | Forces rummage to search binary files. |
