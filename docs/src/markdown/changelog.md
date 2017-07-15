# Changelog

## 2.2.0

Jul, 14, 2017

- **NEW**: Redesign of the preferences dialog.
- **NEW**: Editor configurations are now sent through the shell which changes and simplifies the interface to set it up.
- **FIX**: Simplify dialog initial resize.
- **FIX**: Clean up of closing events: ensure we return a code, destroy objects, and skip unnecessary actions.
- **FIX**: Use double buffering on certain windows and panels in Windows to reduce text flickering on resize.
- **FIX**: Window is only resized by force on initial load, and if the dialog is ever too small when showing something that was hidden.
- **FIX**: Revert ensuring window is never bigger than usable size for now.

## 2.1.0

Jul 9, 2017

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

Jul 2, 2017

- **FIX**: Issue where mousing over results showed nothing in status bar.
- **FIX**: Issue where double clicking result in Content pattern would not open in editor.

## 2.0.4

Jun 30, 2017

- **FIX**: Bump rev.

## 2.0.3

Jun 30, 2017

- **FIX**: Fix editor argument dialog.

## 2.0.2

Jun 27, 2017

- **FIX**: Revert changes in 2.0.1 as wheels don't run setup and don't properly create the Python specific commands.

## 2.0.1

Jun 27, 2017

- **FIX**: Release binary in path as `rummage` and `rummage<version>`. So for 2.7, it would be `rummage2.7`.

## 2.0.0

Jun 27, 2017

- **NEW**: Python 3 support via the new wxPython 4.0.0 Phoenix!
- **NEW**: Dropped classic wxPython (<4.0.0) as it is too much work to maintain legacy support as well.
- **NEW**: Serialize piped argument data.
- **FIX**: Icon now displays in Ubuntu.
- **FIX**: Fix tab traversal issues in both macOS and Linux.
- **FIX**: Fix Linux progress bar disappearing.
- **FIX**: Fix notifications with terminal-notifier.
- **FIX**: Fix issues related to localization.

## 1.0.2

Jul 16, 2016

- **FIX**: issue where editor could not be set.

## 1.0.1

Jun 22, 2016

- **FIX**: Fixed issue where literal replace was not actually literal replace.

## 1.0.0

May 3, 2016

- **NEW**: Initial release
