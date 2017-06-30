# Changelog

## 2.0.4

> Jun 30, 2017

- **FIX**: Bump rev.

## 2.0.3

> Jun 30, 2017

- **FIX**: Fix editor argument dialog.

## 2.0.2

> Jun 27, 2017

- **FIX**: Revert changes in 2.0.1 as wheels don't run setup and don't properly create the Python specific commands.

## 2.0.1

> Jun 27, 2017

- **FIX**: Release binary in path as `rummage` and `rummage<version>`. So for 2.7, it would be `rummage2.7`.

## 2.0.0

> Jun 27, 2017

- **NEW**: Python 3 support via the new wxPython 4.0.0 Phoenix!
- **NEW**: Dropped classic wxPython (<4.0.0) as it is too much work to maintain legacy support as well.
- **NEW**: Serialize piped argument data.
- **FIX**: Icon now displays in Ubuntu.
- **FIX**: Fix tab traversal issues in both macOS and Linux.
- **FIX**: Fix Linux progress bar disappearing.
- **FIX**: Fix notifications with terminal-notifier.
- **FIX**: Fix issues related to localization.

## 1.0.2

> Jul 16, 2016

- **FIX**: issue where editor could not be set.

### 1.0.1

> Released Jun 22, 2016

- **FIX**: Fixed issue where literal replace was not actually literal replace.

## 1.0.0

> Released May 3, 2016

- **NEW**: Initial release
