# Changelog

## 4.6.0b1

- **NEW**: Search options and file limit options can be collapsed in the main dialog. This allows  hiding these options if you aren't frequently using them, and provides a more compact dialog.
- **NEW**: There is no longer an option to hide the file limit options as now you can just collapse them.
- **NEW**: Added context menu option to allow reordering of columns in the result lists. Positions are remembered across sessions.
- **FIX**: Fix an issue on Linux where tabbing past a hidden directory button would cause an error in GTK. Ensure such controls do not allow focus when they are hidden.
- **FIX**: Fix an internal error where the autocomplete box could throw an error due to the index bounds not being checked.
- **FIX**: When list controls are smaller than the window, don't resize last column too an excessively big width.

## 4.5.0

- **NEW**: Add **Match base** search option. **Match base** affects full path patterns when **Full path directory match** or **Full path file match** is enabled. When a full path pattern has no slashes, it will cause the pattern to only match the base file name. This allows you to have traditional base match patterns and more specific full path patterns usage simultaneously. Requires `wcmatch` 4.0 which is now the minimum requirement.
- **FIX**: Ensure settings version is upgraded properly.

## 4.4.1

- **FIX**: Increase performance by reducing number of `stat`/`lstat` calls during crawls.

## 4.4.0

- **NEW**: Add the ability to follow symlinks via a new symlink toggle in the limit panel (disabled by default).

## 4.3.4

- **FIX**: Fix some glob related issues by upgrading to the minimum version of `wcmatch` version 2.1.0.
- **FIX**: Require the minimum version of `bracex` version 1.1.1.

## 4.3.3

- **FIX**: Fix incompatibilities with latest Regex versions.

## 4.3.2

- **FIX**: Require Backrefs 4.0.1 which includes a number of bug fixes, particularly one that sometimes caused Backrefs not to install properly.

## 4.3.1

- **FIX**: Python file encoding detection should default to the Python 3 assumed default, not Python 2.
- **FIX**: Consolidate internal HTML logic and avoid using base 64 encoded images if using latest Markdown extensions that include path conversion fix.
- **FIX**: Refresh status less to improve on overall speed.
- **FIX**: Simplify status: no need to display `ACITVE` or `DONE` as button will change back to `Search` to signify completion along with the display of the `Benchmark` or even the notification if enabled.
- **FIX**: Ensure single file search with no pattern works like multi-file search with no pattern (just return file).
- **FIX**: Minor cleanup and performance increase in core.
- **FIX**: When search error dialog is shown from the status bar, fix error with window destruction.

## 4.3.0

- **NEW**: Documents are now included locally in installation and can be viewed directly in Rummage via a `webview` dialog.
- **NEW**: License can now be viewed from the application menu.
- **NEW**: Show changelog on next launch after upgrade.
- **NEW**: Render editor instructions as HTML in the settings dialog.
- **NEW**: Simplify regular expression engine selection settings panel.
- **FIX**: New about dialog that no longer breaks on Linux.

## 4.2.4

- **FIX**: Adjustments to work with `wcmatch` version 2.0.0.

## 4.2.3

- **FIX**: Process preview in regular expression test dialog when replace pattern is empty. If replace plugin is enabled, we must have a plugin specified.

## 4.2.2

- **FIX**: Don't open another update notification if one is already open.

## 4.2.1

- **FIX**: Better default input focus on Linux when selecting the search tab.
- **FIX**: Properly select "Search for" as the default when chains mode is enabled.

## 4.2.0

- **NEW**: File time result format has been updated for better readability.
- **NEW**: International file time result format for modified and created times has been added and can be enabled in the global preferences.
- **NEW**: Add ability to hide result columns.
- **FIX**: Use wxPython API to highlight alternate rows in lists in order to properly highlight rows on systems with dark themes etc.

## 4.1.3

- **FIX**: Officially support Python 3.7.

## 4.1.2

- **FIX**: Require `wcmatch` 1.0.1 which fixes a number of bugs, most notably a fix for POSIX character classes not properly being handled when at the start of sequence followed by range syntax (`[[:ascii:]-z]`) which will now be handled properly.
- **FIX**: When full path is enabled, and no file pattern is specified, all files will properly be matched like they are when full path is not enabled.

## 4.1.1

- **FIX**: Fix regression where raw character translations (`\xXX` etc.) are no longer working.
- **FIX**: Style tweaks to HTML output.

## 4.1.0

- **NEW**: Escape key will terminate a search or replace from any main tab.
- **NEW**: Old legacy editor configuration is now removed. Only the new is allowed.
- **NEW**: Show history in the settings dialog's history panel.
- **NEW**: Use new `wcmatch` library to handle wild card file matching. Includes new features.
- **NEW**: Add notification test button in settings.
- **NEW**: Regular expression file patterns will respect the user's preference for the Regex libraries version choice.
- **NEW**: Don't force ASCII in regular expression file patterns, but let user choose by sending in `(?a)` flag.
- **FIX**: History clearing did not clear replace plugin history.
- **FIX**: Growl notifications timing out due to image being to large.
- **FIX**: Notifications sound not working when just alert sounds are enabled or sound is enabled with Growl.

## 4.0.7

- **FIX**: Log error during update check. If not a silent check, alert user there was an update check issue.
- **FIX**: Update requests should use `https`.
- **FIX**: Update localization.

## 4.0.6

- **FIX**: Fixes to Windows notifications.

## 4.0.5

- **FIX**: Single instance handling regression #217.

## 4.0.4

- **FIX**: Require Backrefs 3.5.0 which includes fixes for: pattern caching, named Unicode bug.  Also adds better format string replace with the added ability to use format string align and fill.
- **FIX**: Don't escape curly brackets in format strings just because they are string escaped when preprocessing Regex replace templates without Backrefs. Require explicit `{{` or `}}`.

## 4.0.3

- **FIX**: Regression that causes crash when using reverse flag with Regex **and** Backrefs.

## 4.0.2

- **FIX**: In test dialog, when an expression doesn't match, the result box is empty.
- **FIX**: Require Backrefs 3.3.0.

## 4.0.1

- **FIX**: Cleanup some object leaks.
- **FIX**: Incorrect sizing of chain dialog.
- **FIX**: All list objects should be finalized properly to allow sorting.
- **FIX**: Make encoding list style in settings dialog consistent with the look and feel of other list objects.

## 4.0.0

- **NEW**: Drop Python 2.7 support.
- **NEW**: Lines are calculated incrementally as needed opposed to all up front.
- **NEW**: File pattern input will default to `*` or `.*` (for wildcard or regular expression respectively) if left empty.
- **NEW**: Wildcard patterns starting with `-` will now work as expected even if no other patterns are applied (works for both folder exclude and file pattern inputs).

## 3.7.1

- **FIX**: Don't feed Regex version flags into Re patterns.
- **FIX**: Style tweaks to HTML output.

## 3.7.0

- **NEW**: Escape key will terminate a search or replace from any main tab.
- **NEW**: Lines are calculated incrementally as needed opposed to all up front.
- **NEW**: File pattern input will default to `*` or `.*` (for wildcard or regular expression respectively) if left empty.
- **NEW**: Wildcard patterns starting with `-` will now work as expected even if no other patterns are applied (works for both folder exclude and file pattern inputs).
- **NEW**: Old legacy editor configuration is now removed. Only the new is allowed.
- **NEW**: Show history in the settings dialog's history panel.
- **NEW**: Add notification test button in settings.
- **NEW**: Regular expression file patterns will respect the user's preference for the Regex libraries version choice.
- **NEW**: Don't force ASCII in regular expression file patterns, but use the default for the Python version. Let user choose by sending in `(?a)` or `(?u)` flag.
- **FIX**: History clearing did not clear replace plugin history.
- **FIX**: Growl notifications timing out due to image being to large.
- **FIX**: Notifications sound not working when just alert sounds are enabled or sound is enabled with Growl.
- **FIX**: Log error during update check. If not a silent check, alert user there was an update check issue.
- **FIX**: Update requests should use `https`.
- **FIX**: Update localization.
- **FIX**: Fixes to Windows notifications.
- **FIX**: Single instance handling regression #217.
- **FIX**: Require Backrefs 3.5.0 which includes fixes for: pattern caching, named Unicode bug.  Also adds better format string replace with the added ability to use format string align and fill.
- **FIX**: Don't escape curly brackets in format strings just because they are string escaped when preprocessing Regex replace templates without Backrefs. Require explicit `{{` or `}}`.
- **FIX**: Regression that causes crash when using reverse flag with Regex **and** Backrefs.
- **FIX**: In test dialog, when an expression doesn't match, the result box is empty.
- **FIX**: Cleanup some object leaks.
- **FIX**: Incorrect sizing of chain dialog.
- **FIX**: All list objects should be finalized properly to allow sorting.
- **FIX**: Make encoding list style in settings dialog consistent with the look and feel of other list objects.

## 3.6.0

- **NEW**: Rummage will use `cchardet` by default if found.
- **NEW**: Expose way to specify `cchardet` being used.
- **NEW**: Expose special file type encoding handling, and allow user to modify extension list. Covers: `bin`, `python`, `html`, and `xml`.
- **NEW**: Detect middle endian 32 bit BOMs (even if Python has no encoder to actually handle them so we'll just default to binary).
- **NEW**: Speed up and tweak binary detection.
- **NEW**: Add copy button to support info dialog and ensure support info is read only.
- **NEW**: Don't copy notification icons to user folder for use, but use the packaged icons directly from library.
- **NEW**: Provide better support for localization.  Build current language translation on install and bundle in library directly.
- **FIX**: Wildcard pattern splitting on `|` inside a sequence.
- **FIX**: Wildcard patterns not allowing character tokens such as `\x70`, `\u0070`, `\N{unicode name}`, `\160`, and standard escapes like `\t` etc.
- **FIX**: Incorrect documentation on wildcard patterns.
- **FIX**: Python 2.7 not translating Unicode escapes #196.
- **FIX**: Require Backrefs 3.1.2. Some bug fixes, but notably, Backrefs switched from using `\<` and `\>` for start and end word boundaries to `\m` and `\M`.  This is because of an oversight as Python versions less than 3.7 would escape `<` and `>` in `re.escpae` (even though it is unnecessary). Also some Unicode table generation fixes.
- **FIX**: Crashes in Python 2.7 related to not handling 32 bit Unicode in the GUI properly on narrow systems.
- **FIX**: Python 2.7 will translate 32 bit characters to escaped surrogate pairs on narrow systems.
- **FIX**: Tester will replace 32 bit Unicode characters with escaped surrogate pairs place holder in results.
- **FIX**: Rework highlighting in tester dialog to properly highlight 32 bit characters.
- **FIX**: Single instance regression.

## 3.5.0

- **NEW**: Add context menu to content tab just like file tab with all the same entries.
- **NEW**: Add copy commands to context menus to copy selected file names, paths, or content of match (content tab only).
- **NEW**: Add "delete" and "send to trash" options to context menu.
- **NEW**: Add checksum/hash options to context menu.
- **NEW**: Add feature to check for updates. Also add auto update check (disabled by default).
- **NEW**: Install command line as tool as `rummage` and `rummageX.X` where X.X is the major and minor version of the Python in use.
- **FIX**: Fix some leaky objects. Ensure all items are destroyed.
- **FIX**: Rework main application object to fix related issues.
- **FIX**: Limit bulk file open to 20 items to prevent issues when open massive amount of files at once.
- **FIX**: Regression with exports due to recent column addition and order change.
- **FIX**: Search error list destroying parent/main dialog when closed. Also ensure destruction of error list dialog on main window closing.
- **FIX**: Python 2.7 not processing Unicode escapes in search patterns.

## 3.4.3

- **FIX**: Import of `bregex` when `regex` is not installed.
- **FIX**: Backwards search did not reassemble text proper.

## 3.4.2

- **FIX**: Require Backrefs 3.0.2 which fixes a minor Bregex cache purge issue.

## 3.4.1

- **FIX**: Regression where installed CLI command would fail on launch.

## 3.4.0

- **NEW**: Require latest Backrefs 3.0.1.
- **NEW**: Add extension column in results.
- **NEW**: Status now just shows `[ACTIVE]` or `[DONE]` instead of a misleading percentage.
- **NEW**: Can now multi-select and mass open files in your editor.
- **NEW**: Better error feedback in regex tester.
- **NEW**: Remove current directory from Python path when opening Rummage to prevent it from importing local libraries when launched inside a Python project.  This mainly affects `python -m rummage` and `pythonw -m rummage` launching.
- **FIX**: Result item hover not showing file name in status bar.
- **FIX**: Warnings in plugin system.

## 3.3.0

- **NEW**: Add changelog link in menu for quick reference.
- **NEW**: Encoding list is generated from the Python installation being used.
- **FIX**: Infinite loop on result double click in content list.

## 3.2.1

- **FIX**: Complete message should not be of "error" type.

## 3.2.0

- **NEW**: Results update live. Progress has been removed. (#140)
- **FIX**: Windows status bar flicker.
- **FIX**: Results not showing when notifications is set to only play audio alerts.

## 3.1.0

- **NEW**: Add export/import of settings and/or regular expression rules and chains.
- **NEW**: Add support info dialog to gather info when filing issues.

## 3.0.0

- **NEW**: Allow Backrefs' replace references to work with format replaces.
- **NEW**: Add support for format replace with Re (with Backrefs only).
- **NEW**: Rummage requires Backrefs 2.1.0+.
- **FIX**: Regex's format replacement (without Backrefs) and Re (without Backrefs) handling of back slashes Unicode, byte, notation was different that Backrefs and other Regex modes. Normalize the differences to give the expected feel.
- **FIX**: Ensure replace (in all cases) isn't populated during a search only.

## 2.3.3

- **FIX**: Avoid Backrefs 1.1.0 and 2+ for until 2.1.

## 2.3.2

- **FIX**: Fix Windows `pythonw` failure.

## 2.3.1

- **FIX**: `wxPython` 4.0.0b1 removed label parameter from constructor.
- **FIX**: Debug Unicode issue.

## 2.3.0

- **NEW**: Add reveal right click menu option in "File" tab results.
- **NEW**: Expose backup configuration and allow putting all backups in a folder if desired.
- **FIX**: Windows Unicode input path issues from command line and through the pipe during single instance argument transfer.
- **FIX**: Windows Unicode issue when calling a shell command to open file in editor.

## 2.2.0

- **NEW**: Redesign of the preferences dialog.
- **NEW**: Editor configurations are now sent through the shell which changes and simplifies the interface to set it up.
- **FIX**: Simplify dialog initial resize.
- **FIX**: Clean up of closing events: ensure we return a code, destroy objects, and skip unnecessary actions.
- **FIX**: Use double buffering on certain windows and panels in Windows to reduce text flickering on resize.
- **FIX**: Window is only resized by force on initial load, and if the dialog is ever too small when showing something that was hidden.
- **FIX**: Revert ensuring window is never bigger than usable size for now.

## 2.1.0

- **NEW**: Add new chained search feature.
- **NEW**: Add new replace plugin support.
- **NEW**: Restructure internal API to support chained search.
- **NEW**: Saved searches will now require a unique name and an optional comment. Old legacy saves will be converted on first access. The old legacy name will be the comment, and a unique name will be generated from the comment.
- **NEW**: Saved search names and comments can be edited from the "Load Search" panel.
- **NEW**: Internal API no longer will guess and decode strings, only files.  It is expected that the caller handles encoding of string buffers.  A Unicode buffer will be searched as usual, and a binary string buffer will be treated as binary.
- **NEW**: Tester dialog will now process literal searches as well.
- **NEW**: Literal searches will now utilize the Unicode related flags. This is particularly notable if using the Regex module and wanting to have full case-folding applied in case-insensitive matches.
- **FIX**: Visual inconsistencies in regard to text box size relative to siblings, alignment of labels, etc.
- **FIX**: Content text box in tester dialog will now allow entering tab characters on all platforms instead of navigating to next control.
- **FIX**: Fix wxPython deprecation noise in the console.
- **FIX**: Fix some binary related replace issues.
- **FIX**: Fix search not aborting.
- **FIX**: Fix issue where selecting file from drop down list didn't hide limit panel.
- **FIX**: Don't display replace message when aborting replace.
- **FIX**: Fix limit panel hide logic so it doesn't show a the hidden panel on search.
- **FIX**: POSIX flag not generating refresh in tester dialog.
- **FIX**: Unicode issue in preferences' editor dialog.
- **FIX**: Ensure all localized strings properly get loaded.
- **FIX**: Ensure initial `on_loaded` event via `CallLater` works properly in Python 2 and 3.
- **FIX**: Call initial main window resize in `on_loaded` event in some situations.
- **FIX**: Ensure main window initial resize is never bigger than usable screen size.

## 2.0.5

- **FIX**: Issue where mousing over results showed nothing in status bar.
- **FIX**: Issue where double clicking result in Content pattern would not open in editor.

## 2.0.4

- **FIX**: Bump rev.

## 2.0.3

- **FIX**: Fix editor argument dialog.

## 2.0.2

- **FIX**: Revert changes in 2.0.1 as wheels don't run setup and don't properly create the Python specific commands.

## 2.0.1

- **FIX**: Release binary in path as `rummage` and `rummage<version>`. So for 2.7, it would be `rummage2.7`.

## 2.0.0

- **NEW**: Python 3 support via the new wxPython 4.0.0 Phoenix!
- **NEW**: Dropped classic wxPython (<4.0.0) as it is too much work to maintain legacy support as well.
- **NEW**: Serialize piped argument data.
- **FIX**: Icon now displays in Ubuntu.
- **FIX**: Fix tab traversal issues in both macOS and Linux.
- **FIX**: Fix Linux progress bar disappearing.
- **FIX**: Fix notifications with terminal-notifier.
- **FIX**: Fix issues related to localization.

## 1.0.2

- **FIX**: issue where editor could not be set.

## 1.0.1

- **FIX**: Fixed issue where literal replace was not actually literal replace.

## 1.0.0

- **NEW**: Initial release
