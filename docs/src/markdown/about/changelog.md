# Changelog

## 4.16.4

- **FIX**: Pick up latest `wcmatch` (8.3), `bracex` (2.2), and `backrefs` (5.2) to acquire latest related bug fixes
  related to file search patterns and regular expressions (if using `backrefs`).
- **FIX**: Update internal Markdown and extensions (`markdown` 3.3.4 and `pymdown-extensions` 9.0 and M) to ensure
  latest changes and fixes for UI elements that render Markdown to HTML.
- **FIX**: Update to latest `chardet` (4.0).
- **FIX**: When chaining literal and regular expression patterns together, the mode could get stuck in literal mode
  when applying replacements.

## 4.16.3

- **FIX**: Use latest `wcmatch` (8.1) which does a better job at bailing out of really large expansions. Patterns
  like `{1..1000000}`, while they used to bail according to the set limit, would hang a bit before they do. The whole
  point of bailing was to avoid hangs (if possible) if the intent was disallow such a large pattern now they assert
  much quicker.
- **FIX**: Fix internal documentation "Home" link. On certain pages, the link could be broken.

## 4.16.2

- **FIX**: Support info won't open.
- **FIX**: Small internal code improvements.

## 4.16.1

- **FIX**: Linux regression of date time control color due to recent color fix for macOS in 4.15.1.

## 4.16

- **NEW**: Require `backrefs` 5.0+ which provides significant Unicode improvements and bug fixes when paired with Re.
  One notable change is that Unicode properties now respect the Unicode Properties flags and Unicode properties will be
  limited to the ASCII range when not enabled just like Regex does. Also POSIX style patterns have been expanded to
  handle any Unicode property, POSIX and otherwise. Check out [Backrefs' documentation][backrefs] for more information.
  Also, the deprecated search references (`\l`, `\L`, `\c`, and `\C`) are no longer available, though you can always
  use the other forms of `[[:lower:]]`, `\p{lower}`, etc.
- **NEW**: Require new `wcmatch` 8.0.1+.
- **FIX**: Remove old `gntp` from support info dialog as we no longer use that package.

## 4.15.1

- **FIX**: High Sierra and below don't work the same in regard to colors. Add special logic to skip dynamic color in old
  macOS versions as they will result in black UI controls.

## 4.15

- **NEW**: Formally support Python 3.9.
- **NEW**: Formally drop Python 3.5.
- **NEW**: Use Apple's Big Sur template for the macOS dock icon.

## 4.14.1

- **FIX**: Our old method of raising macOS windows no longer works. Raise via an `osascript` call.
- **FIX**: Fix internal flag mask issue that would prevent preference for `-` to negatively filter files from working.

## 4.14

- **NEW**: Calculate better looking, alternating list colors instead of relying on wxPython to provide.
- **NEW**: Linux now uses the same autocomplete logic in autocomplete combo boxes that Windows and macOS uses. This
  removes a workaround that required Linux to use different logic. The actual issue has been resolved in wxPython 4.1.
- **FIX**: Notifications should work better on Windows.
- **FIX**: On some Linux systems, the down key, while one of the autocomplete combo boxes have focus, will cause the
  cursor to jump to a widget below the current and then process the `on_key_up` event which is meant to trigger the drop
  down history of the prior autocomplete combo box.
- **FIX**: Latest wxPython changes made escape not close the autocomplete combo boxes.
- **FIX**: Different Linux Desktop Environments need different size icons to show up properly in their taskbar, provide
  an icon bundle to ensure there is always one of appropriate size.
- **FIX**: Use `wcmatch` 7.0 which includes a few bug fixes.

## 4.13

- **NEW**: Drop growl notification support.
- **FIX**: Replace macOS rocket dock icon and Window's default Python task bar icon with Rummage icon.
- **FIX**: On color change, macOS would reset time picker values.

## 4.12

- **NEW**: Add new option to use `!` instead of `-` for exclusion patterns. Rummage has always used `-` due to issues
  with distinguishing between exclusion patterns (`!exclude`) and extended globbing exclude patterns
  (`!(exclude_1| exclude 2)`). `wcmatch` 6.1 now resolves this by requiring `(` to be escaped if the pattern starts with
  `!(` and it is not meant to be an extended glob pattern `!(..)`.
- **NEW**: Require `wcmatch` 6.1 that comes with a number of enhancements and bug fixes.
- **NEW**: Proper support for system color changes. Allows proper transitioning on macOS between light and dark mode.
- **FIX**: Minor fixes to selection colors in regex tester.
- **FIX**: Remove old macOS workaround to force focus on search input.
- **FIX**: Officially support Python 3.8.

## 4.11.1

- **FIX**: Internal color fixes.
- **FIX**: Fix Rummage crashing with wxPython 4.1.X due to image sizing bug on macOS.
- **FIX**: Resolve issue where changelog would not show after an update.

## 4.11

- **NEW**: `wcmatch` the file search library that Rummage uses, is now at version 6 which imposes a pattern limit to
  protect against patterns such as `{1..1000000}` which would expand to a large amount of patterns if brace expansion
  is enabled. Rummage exposes control of this.
- **FIX**: By using `wcmatch` version 6, complex issues involving pattern splitting with `|` and `{,}` are resolved.
- **FIX**: Fix logo not loading in about dialog.

## 4.10

- **NEW**: Pattern save dialog now uses a drop down list so you can easily update an existing saved pattern.
- **FIX**: Fix issue with web view rendering and `pymdown-extensions`.

## 4.9

- **NEW**: Require `wcmatch` 5.1.0+, `bracex` 1.4.0, and `backrefs` `1.3.0` to include latest bug fixes.

## 4.8

- **NEW**: Supports installing extras via `pip install rummage[extras]`.
- **FIX**: Fix for notification sound display in settings dialog.
- **FIX**: Fix notification sound not playing on Linux when configured.

## 4.7.1

- **FIX**: Require `wcmatch` 5.0 and make adjustments to support it.

## 4.7

!!! warning "Warning"
    Backrefs 4.2.0 has deprecated the shorthand references for alphabetic character groups in `re` search patterns:
    `\l`, `\L`, `\c`, and `\C`. Instead you should use: `[[:lower:]]`, `[[:^lower:]]`, `[[:upper:]]`, and `[[:^upper:]]`
    respectively. While the references have only been deprecated, and are technically still available, a future version
    of Backrefs will remove them entirely at some point. It is recommended to transition now so as not to be caught
    unawares.

- **NEW**: Add `col0` variable for editor configuration to allow for using a zero based column value instead of one
  based column value for editors that require it.
- **NEW**: Add global option to turn off alternating row colors in lists.
- **NEW**: Provide support for different players on Linux: `paplay`, `aplay`, and `play` (`sox`). Supported sound
  formats vary.
- **NEW**: Provide interface for selecting custom notification sounds.
- **NEW**: Require `wcmatch` 4.3.1+ and `backrefs` 4.2.0+.
- **FIX**: Better attempt to get appropriate file creation time on all Linux systems.
- **FIX**: Better fix for time picker getting wrong background.
- **FIX**: Ensure column sizing includes header size.
- **FIX**: When showing timed status event for results in status bar (full path name), decrease length of time that the
  temporary status is shown and clear temporary status when the cursor leaves result items.
- **FIX**: Don't log handled notification errors when a notification system is not found as these are handled gracefully
  and there is no need to worry the user.

## 4.6.3

- **FIX**: Notification audio failures should be handled gracefully.
- **FIX**: Sometimes abort doesn't work.

## 4.6.2

- **FIX**: Fix issue where time control used a completely different font and font size.

## 4.6.1

- **FIX**: Fix issues with time control not properly inheriting system colors.
- **FIX**: Fix time control sizing on Linux.
- **FIX**: Fix time control issue on Linux and macOS that prevents decrement button from decrementing past initial
  value.

## 4.6

- **NEW**: Search options and file limit options can be collapsed in the main dialog. This allows  hiding these options
  if you aren't frequently using them, and provides a more compact dialog.
- **NEW**: There is no longer an option to hide the file limit options as now you can just collapse them.
- **NEW**: Added context menu option to allow reordering of columns in the result lists. Positions are remembered across
  sessions.
- **FIX**: Fix an issue on Linux where tabbing past a hidden directory button would cause an error in GTK. Ensure such
  controls do not allow focus when they are hidden.
- **FIX**: Fix an internal error where the autocomplete box could throw an error due to the index bounds not being
  checked.
- **FIX**: When list controls are smaller than the window, don't resize last column too an excessively big width.
- **FIX**: Fix regression with loading replace plugins.
- **FIX**: Better initial focus in autocomplete text boxes on platforms that had issues.
- **FIX**: Fix some localization issues.

## 4.5

- **NEW**: Add **Match base** search option. **Match base** affects full path patterns when **Full path directory
  match** or **Full path file match** is enabled. When a full path pattern has no slashes, it will cause the pattern to
  only match the base file name. This allows you to have traditional base match patterns and more specific full path
  patterns usage simultaneously. Requires `wcmatch` 4.0 which is now the minimum requirement.
- **FIX**: Ensure settings version is upgraded properly.

## 4.4.1

- **FIX**: Increase performance by reducing number of `stat`/`lstat` calls during crawls.

## 4.4

- **NEW**: Add the ability to follow symlinks via a new symlink toggle in the limit panel (disabled by default).

## 4.3.4

- **FIX**: Fix some glob related issues by upgrading to the minimum version of `wcmatch` version 2.1.0.
- **FIX**: Require the minimum version of `bracex` version 1.1.1.

## 4.3.3

- **FIX**: Fix incompatibilities with latest Regex versions.

## 4.3.2

- **FIX**: Require Backrefs 4.0.1 which includes a number of bug fixes, particularly one that sometimes caused Backrefs
  not to install properly.

## 4.3.1

- **FIX**: Python file encoding detection should default to the Python 3 assumed default, not Python 2.
- **FIX**: Consolidate internal HTML logic and avoid using base 64 encoded images if using latest Markdown extensions
  that include path conversion fix.
- **FIX**: Refresh status less to improve on overall speed.
- **FIX**: Simplify status: no need to display `ACITVE` or `DONE` as button will change back to `Search` to signify
  completion along with the display of the `Benchmark` or even the notification if enabled.
- **FIX**: Ensure single file search with no pattern works like multi-file search with no pattern (just return file).
- **FIX**: Minor cleanup and performance increase in core.
- **FIX**: When search error dialog is shown from the status bar, fix error with window destruction.

## 4.3

- **NEW**: Documents are now included locally in installation and can be viewed directly in Rummage via a `webview`
  dialog.
- **NEW**: License can now be viewed from the application menu.
- **NEW**: Show changelog on next launch after upgrade.
- **NEW**: Render editor instructions as HTML in the settings dialog.
- **NEW**: Simplify regular expression engine selection settings panel.
- **FIX**: New about dialog that no longer breaks on Linux.

## 4.2.4

- **FIX**: Adjustments to work with `wcmatch` version 2.0.0.

## 4.2.3

- **FIX**: Process preview in regular expression test dialog when replace pattern is empty. If replace plugin is
  enabled, we must have a plugin specified.

## 4.2.2

- **FIX**: Don't open another update notification if one is already open.

## 4.2.1

- **FIX**: Better default input focus on Linux when selecting the search tab.
- **FIX**: Properly select "Search for" as the default when chains mode is enabled.

## 4.2

- **NEW**: File time result format has been updated for better readability.
- **NEW**: International file time result format for modified and created times has been added and can be enabled in the
  global preferences.
- **NEW**: Add ability to hide result columns.
- **FIX**: Use wxPython API to highlight alternate rows in lists in order to properly highlight rows on systems with
  dark themes etc.

## 4.1.3

- **FIX**: Officially support Python 3.7.

## 4.1.2

- **FIX**: Require `wcmatch` 1.0.1 which fixes a number of bugs, most notably a fix for POSIX character classes not
  properly being handled when at the start of sequence followed by range syntax (`[[:ascii:]-z]`) which will now be
  handled properly.
- **FIX**: When full path is enabled, and no file pattern is specified, all files will properly be matched like they are
  when full path is not enabled.

## 4.1.1

- **FIX**: Fix regression where raw character translations (`\xXX` etc.) are no longer working.
- **FIX**: Style tweaks to HTML output.

## 4.1

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

- **FIX**: Require Backrefs 3.5.0 which includes fixes for: pattern caching, named Unicode bug.  Also adds better format
  string replace with the added ability to use format string align and fill.
- **FIX**: Don't escape curly brackets in format strings just because they are string escaped when preprocessing Regex
  replace templates without Backrefs. Require explicit `{{` or `}}`.

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

## 4.0

- **NEW**: Drop Python 2.7 support.
- **NEW**: Lines are calculated incrementally as needed opposed to all up front.
- **NEW**: File pattern input will default to `*` or `.*` (for wildcard or regular expression respectively) if left
  empty.
- **NEW**: Wildcard patterns starting with `-` will now work as expected even if no other patterns are applied (works
  for both folder exclude and file pattern inputs).

## 3.7.1

- **FIX**: Don't feed Regex version flags into Re patterns.
- **FIX**: Style tweaks to HTML output.

## 3.7

- **NEW**: Escape key will terminate a search or replace from any main tab.
- **NEW**: Lines are calculated incrementally as needed opposed to all up front.
- **NEW**: File pattern input will default to `*` or `.*` (for wildcard or regular expression respectively) if left
  empty.
- **NEW**: Wildcard patterns starting with `-` will now work as expected even if no other patterns are applied (works
  for both folder exclude and file pattern inputs).
- **NEW**: Old legacy editor configuration is now removed. Only the new is allowed.
- **NEW**: Show history in the settings dialog's history panel.
- **NEW**: Add notification test button in settings.
- **NEW**: Regular expression file patterns will respect the user's preference for the Regex libraries version choice.
- **NEW**: Don't force ASCII in regular expression file patterns, but use the default for the Python version. Let user
  choose by sending in `(?a)` or `(?u)` flag.
- **FIX**: History clearing did not clear replace plugin history.
- **FIX**: Growl notifications timing out due to image being to large.
- **FIX**: Notifications sound not working when just alert sounds are enabled or sound is enabled with Growl.
- **FIX**: Log error during update check. If not a silent check, alert user there was an update check issue.
- **FIX**: Update requests should use `https`.
- **FIX**: Update localization.
- **FIX**: Fixes to Windows notifications.
- **FIX**: Single instance handling regression #217.
- **FIX**: Require Backrefs 3.5.0 which includes fixes for: pattern caching, named Unicode bug.  Also adds better format
  string replace with the added ability to use format string align and fill.
- **FIX**: Don't escape curly brackets in format strings just because they are string escaped when preprocessing Regex
  replace templates without Backrefs. Require explicit `{{` or `}}`.
- **FIX**: Regression that causes crash when using reverse flag with Regex **and** Backrefs.
- **FIX**: In test dialog, when an expression doesn't match, the result box is empty.
- **FIX**: Cleanup some object leaks.
- **FIX**: Incorrect sizing of chain dialog.
- **FIX**: All list objects should be finalized properly to allow sorting.
- **FIX**: Make encoding list style in settings dialog consistent with the look and feel of other list objects.

## 3.6

- **NEW**: Rummage will use `cchardet` by default if found.
- **NEW**: Expose way to specify `cchardet` being used.
- **NEW**: Expose special file type encoding handling, and allow user to modify extension list. Covers: `bin`, `python`,
  `html`, and `xml`.
- **NEW**: Detect middle endian 32 bit BOMs (even if Python has no encoder to actually handle them so we'll just default
  to binary).
- **NEW**: Speed up and tweak binary detection.
- **NEW**: Add copy button to support info dialog and ensure support info is read only.
- **NEW**: Don't copy notification icons to user folder for use, but use the packaged icons directly from library.
- **NEW**: Provide better support for localization.  Build current language translation on install and bundle in library
  directly.
- **FIX**: Wildcard pattern splitting on `|` inside a sequence.
- **FIX**: Wildcard patterns not allowing character tokens such as `\x70`, `\u0070`, `\N{unicode name}`, `\160`, and
  standard escapes like `\t` etc.
- **FIX**: Incorrect documentation on wildcard patterns.
- **FIX**: Python 2.7 not translating Unicode escapes #196.
- **FIX**: Require Backrefs 3.1.2. Some bug fixes, but notably, Backrefs switched from using `\<` and `\>` for start and
  end word boundaries to `\m` and `\M`.  This is because of an oversight as Python versions less than 3.7 would escape
  `<` and `>` in `re.escpae` (even though it is unnecessary). Also some Unicode table generation fixes.
- **FIX**: Crashes in Python 2.7 related to not handling 32 bit Unicode in the GUI properly on narrow systems.
- **FIX**: Python 2.7 will translate 32 bit characters to escaped surrogate pairs on narrow systems.
- **FIX**: Tester will replace 32 bit Unicode characters with escaped surrogate pairs place holder in results.
- **FIX**: Rework highlighting in tester dialog to properly highlight 32 bit characters.
- **FIX**: Single instance regression.

## 3.5

- **NEW**: Add context menu to content tab just like file tab with all the same entries.
- **NEW**: Add copy commands to context menus to copy selected file names, paths, or content of match (content tab only).
- **NEW**: Add "delete" and "send to trash" options to context menu.
- **NEW**: Add checksum/hash options to context menu.
- **NEW**: Add feature to check for updates. Also add auto update check (disabled by default).
- **NEW**: Install command line as tool as `rummage` and `rummageX.X` where X.X is the major and minor version of the
  Python in use.
- **FIX**: Fix some leaky objects. Ensure all items are destroyed.
- **FIX**: Rework main application object to fix related issues.
- **FIX**: Limit bulk file open to 20 items to prevent issues when open massive amount of files at once.
- **FIX**: Regression with exports due to recent column addition and order change.
- **FIX**: Search error list destroying parent/main dialog when closed. Also ensure destruction of error list dialog on
  main window closing.
- **FIX**: Python 2.7 not processing Unicode escapes in search patterns.

## 3.4.3

- **FIX**: Import of `bregex` when `regex` is not installed.
- **FIX**: Backwards search did not reassemble text proper.

## 3.4.2

- **FIX**: Require Backrefs 3.0.2 which fixes a minor Bregex cache purge issue.

## 3.4.1

- **FIX**: Regression where installed CLI command would fail on launch.

## 3.4

- **NEW**: Require latest Backrefs 3.0.1.
- **NEW**: Add extension column in results.
- **NEW**: Status now just shows `[ACTIVE]` or `[DONE]` instead of a misleading percentage.
- **NEW**: Can now multi-select and mass open files in your editor.
- **NEW**: Better error feedback in regex tester.
- **NEW**: Remove current directory from Python path when opening Rummage to prevent it from importing local libraries
  when launched inside a Python project.  This mainly affects `python -m rummage` and `pythonw -m rummage` launching.
- **FIX**: Result item hover not showing file name in status bar.
- **FIX**: Warnings in plugin system.

## 3.3

- **NEW**: Add changelog link in menu for quick reference.
- **NEW**: Encoding list is generated from the Python installation being used.
- **FIX**: Infinite loop on result double click in content list.

## 3.2.1

- **FIX**: Complete message should not be of "error" type.

## 3.2.0

- **NEW**: Results update live. Progress has been removed. (#140)
- **FIX**: Windows status bar flicker.
- **FIX**: Results not showing when notifications is set to only play audio alerts.

## 3.1

- **NEW**: Add export/import of settings and/or regular expression rules and chains.
- **NEW**: Add support info dialog to gather info when filing issues.

## 3.0

- **NEW**: Allow Backrefs' replace references to work with format replaces.
- **NEW**: Add support for format replace with Re (with Backrefs only).
- **NEW**: Rummage requires Backrefs 2.1.0+.
- **FIX**: Regex's format replacement (without Backrefs) and Re (without Backrefs) handling of back slashes Unicode,
  byte, notation was different that Backrefs and other Regex modes. Normalize the differences to give the expected feel.
- **FIX**: Ensure replace (in all cases) isn't populated during a search only.

## 2.3.3

- **FIX**: Avoid Backrefs 1.1.0 and 2+ for until 2.1.

## 2.3.2

- **FIX**: Fix Windows `pythonw` failure.

## 2.3.1

- **FIX**: `wxPython` 4.0.0b1 removed label parameter from constructor.
- **FIX**: Debug Unicode issue.

## 2.3

- **NEW**: Add reveal right click menu option in "File" tab results.
- **NEW**: Expose backup configuration and allow putting all backups in a folder if desired.
- **FIX**: Windows Unicode input path issues from command line and through the pipe during single instance argument
  transfer.
- **FIX**: Windows Unicode issue when calling a shell command to open file in editor.

## 2.2

- **NEW**: Redesign of the preferences dialog.
- **NEW**: Editor configurations are now sent through the shell which changes and simplifies the interface to set it up.
- **FIX**: Simplify dialog initial resize.
- **FIX**: Clean up of closing events: ensure we return a code, destroy objects, and skip unnecessary actions.
- **FIX**: Use double buffering on certain windows and panels in Windows to reduce text flickering on resize.
- **FIX**: Window is only resized by force on initial load, and if the dialog is ever too small when showing something
  that was hidden.
- **FIX**: Revert ensuring window is never bigger than usable size for now.

## 2.1

- **NEW**: Add new chained search feature.
- **NEW**: Add new replace plugin support.
- **NEW**: Restructure internal API to support chained search.
- **NEW**: Saved searches will now require a unique name and an optional comment. Old legacy saves will be converted on
  first access. The old legacy name will be the comment, and a unique name will be generated from the comment.
- **NEW**: Saved search names and comments can be edited from the "Load Search" panel.
- **NEW**: Internal API no longer will guess and decode strings, only files.  It is expected that the caller handles
  encoding of string buffers.  A Unicode buffer will be searched as usual, and a binary string buffer will be treated as
  binary.
- **NEW**: Tester dialog will now process literal searches as well.
- **NEW**: Literal searches will now utilize the Unicode related flags. This is particularly notable if using the Regex
  module and wanting to have full case-folding applied in case-insensitive matches.
- **FIX**: Visual inconsistencies in regard to text box size relative to siblings, alignment of labels, etc.
- **FIX**: Content text box in tester dialog will now allow entering tab characters on all platforms instead of
  navigating to next control.
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

## 2.0

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

## 1.0

- **NEW**: Initial release

--8<-- "links.txt"
