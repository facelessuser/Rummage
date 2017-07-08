"""
Rummage Dialog.

Licensed under MIT
Copyright (c) 2011 - 2015 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.
"""
from __future__ import unicode_literals
import wx
import wx.adv
import threading
import traceback
import webbrowser
from time import time
import os
import re
import codecs
import wx.lib.newevent
from backrefs import bre, bregex
from .settings import Settings
from .actions import export_html
from .actions import export_csv
from .actions import open_editor
from .generic_dialogs import errormsg, yesno
from .app.custom_app import DebugFrameExtender, debug, error, simplelog
from .controls import custom_statusbar
from .regex_test_dialog import RegexTestDialog
from .controls.autocomplete_combo import AutoCompleteCombo
from .load_search_dialog import LoadSearchDialog
from .save_search_dialog import SaveSearchDialog
from .search_error_dialog import SearchErrorDialog
from .search_chain_dialog import SearchChainDialog
from .settings_dialog import SettingsDialog
from .about_dialog import AboutDialog
from .controls import pick_button
from .messages import filepickermsg
from .localization import _
from . import gui
from . import data
from . import notify
from ..util import epoch_timestamp
from .. import __meta__
from .. import rumcore
from .. import util
import decimal

# Combo options
SIZE_ANY = _("any")
SIZE_GT = _("greater than")
SIZE_EQ = _("equal to")
SIZE_LT = _("less than")

TIME_ANY = _("on any")
TIME_GT = _("after")
TIME_EQ = _("on")
TIME_LT = _("before")

# Search/replace button states
SEARCH_BTN_STOP = _("Stop")
SEARCH_BTN_SEARCH = _("Search")
SEARCH_BTN_ABORT = _("Aborting")
REPLACE_BTN_REPLACE = _("Replace")

# Picker/Save messages
DIRECTORY_SELECT = _("Select directory to rummage")
SCRIPT_SELECT = _("Select replace script")
EXPORT_TO = _("Export to...")

# Dialog messages
MSG_REPLACE_WARN = _("Are you sure you want to replace all instances?")
MSG_BACKUPS_DISABLED = _("Backups are currently disabled.")

# Notifications
NOTIFY_SEARCH_ABORTED = _("Search Aborted")
NOTIFY_SEARCH_COMPLETED = _("Search Completed")
NOTIFY_MATCHES_FOUND = _("\n%d matches found!")

# ERRORS
ERR_NO_LOG = _("Cannot find log file!")
ERR_EMPTY_SEARCH = _("There is no search to save!")
ERR_HTML_FAILED = _("There was a problem exporting the HTML!  See the log for more info.")
ERR_CSV_FAILED = _("There was a problem exporting the CSV!  See the log for more info.")
ERR_NOTHING_TO_EXPORT = _("There is nothing to export!")
ERR_SETUP = _("There was an error in setup! Please check the log.")
ERR_INVALID_SEARCH_PTH = _("Please enter a valid search path!")
ERR_INVALID_SEARCH = _("Please enter a valid search!")
ERR_EMPTY_CHAIN = _("There are no searches in this this chain!")
ERR_MISSING_SEARCH = _("'%s' is not found in saved searches!")
ERR_INVALID_CHAIN = _("Please enter a valid chain!")
ERR_INVALID_CHAIN_SEARCH = _("Saved search '%s' does not contain a valid search pattern!")
ERR_INVALID_FILE_SEARCH = _("Please enter a valid file pattern!")
ERR_INVALID_EXCLUDE = _("Please enter a valid exlcude directory regex!")
ERR_INVLAID_SIZE = _("Please enter a valid size!")
ERR_INVALID_MDATE = _("Please enter a modified date!")
ERR_INVALID_CDATE = _("Please enter a created date!")

# Status
INIT_STATUS = _("Searching: 0/0 0% Skipped: 0 Matches: 0")
UPDATE_STATUS = _("Searching: %d/%d %d%% Skipped: %d Matches: %d")
FINAL_STATUS = _("Searching: %d/%d %d%% Skipped: %d Matches: %d Benchmark: %s")
BENCHMARK_STATUS = _("%01.2f seconds")

# Status bar popup
SB_ERRORS = _("errors")
SB_TOOLTIP_ERR = _("%d errors\nClick to see errors.")

# Controls
SEARCH_REPLACE = _("Search and Replace")
LIMIT_SEARCH = _("Limit Search")
SEARCH_IN = _("Search in")
SEARCH_FOR = _("Search for")
SEARCH_CHAIN = _("Search chain")
REPLACE_WITH = _("Replace with")
REPLACE_PLUGIN = _("Replace plugin")
SIZE_IS = _("Size is")
MODIFIED = _("Modified")
CREATED = _("Created")
EXCLUDE = _("Exclude folders")
FILE_MATCH = _("Files which match")
SEARCH_WITH_REGEX = _("Search with regex")
CASE = _("Search case-sensitive")
DOTALL = _("Dot matches newline")
UNICODE = _("Use Unicode properties")
BOOLEAN = _("Boolean match")
COUNT_ONLY = _("Count only")
CREATE_BACKUPS = _("Create backups")
FORCE = _("Force")
USE_CHAIN = _("Use chain search")
USE_PLUGIN = _("Use plugin replace")
BESTMATCH = _("Best fuzzy match")
FUZZY_FIT = _("Improve fuzzy fit")
WORD = _("Unicode word breaks")
REVERSE = _("Search backwards")
POSIX = _("Use POSIX matching")
FORMAT = _("Format style replacements")
CASEFOLD = _("Full case-folding")
SUBFOLDERS = _("Include subfolders")
HIDDEN = _("Include hidden")
INCLUDE_BINARY = _("Include binary files")
USE_REGEX = _("Regex")
TEST_REGEX = _("Test Regex")
SAVE_SEARCH = _("Save Search")
LOAD_SEARCH = _("Load Search")
SEARCH = _("Search")

# Menu
MENU_EXPORT = _("Export")
MENU_FILE = _("File")
MENU_VIEW = _("View")
MENU_HELP = _("Help")
MENU_PREFERENCES = _("&Preferences")
MENU_EXIT = _("&Exit")
MENU_HTML = _("HTML")
MENU_CSV = _("CSV")
MENU_HIDE_LIMIT = _("Hide Limit Search Panel")
MENU_OPEN_LOG = _("Open Log File")
MENU_ABOUT = _("&About Rummage")
MENU_DOCUMENTATION = _("Documentation")
MENU_HELP_SUPPORT = _("Help and Support")
MENU_SHOW_LIMIT = _("Show Limit Search Panel")
MENU_HIDE_LIMIT = _("Hide Limit Search Panel")

_LOCK = threading.Lock()
_RESULTS = []
_COMPLETED = 0
_TOTAL = 0
_RECORDS = 0
_SKIPPED = 0
_ERRORS = []
_ABORT = False

LIMIT_COMPARE = {
    0: "any",
    1: "gt",
    2: "eq",
    3: "lt"
}

ENCODINGS = [
    "ASCII",
    "BIG5",
    "BIG5-HKSCS",
    "BIN",
    "CP037",
    "CP154",
    "CP424",
    "CP437",
    "CP500",
    "CP720",
    "CP737",
    "CP775",
    "CP850",
    "CP852",
    "CP855",
    "CP856",
    "CP857",
    "CP858",
    "CP860",
    "CP861",
    "CP862",
    "CP863",
    "CP864",
    "CP865",
    "CP866",
    "CP869",
    "CP874",
    "CP875",
    "CP949",
    "CP950",
    "CP1006",
    "CP1026",
    "CP1140",
    "EUC-JP",
    "EUC-JIS-2004",
    "EUC-JISX0213",
    "EUC-KR",
    "GB2312",
    "GBK",
    "GB18030",
    "HZ",
    "ISO-2022-JP",
    "ISO-2022-JP-1",
    "ISO-2022-JP-2",
    "ISO-2022-JP-2004",
    "ISO-2022-JP-3",
    "ISO-2022-JP-ext",
    "ISO-2022-KR",
    "ISO-8859-2",
    "ISO-8859-3",
    "ISO-8859-4",
    "ISO-8859-5",
    "ISO-8859-6",
    "ISO-8859-7",
    "ISO-8859-8",
    "ISO-8859-9",
    "ISO-8859-10",
    "ISO-8859-13",
    "ISO-8859-14",
    "ISO-8859-15",
    "ISO-8859-16",
    "JOHAB",
    "KOI8-R",
    "KOI8-U",
    "LATIN-1",
    "MAC-CYRILLIC",
    "MAC-GREEK",
    "MAC-ICELAND",
    "MAC-LATIN2",
    "MAC-ROMAN",
    "MAC-TURKISH",
    "MS-KANJI",
    "SHIFT-JIS",
    "SHIFT-JIS-2004",
    "SHIFT-JISX0213",
    "UTF-32-BE",
    "UTF-32-LE",
    "UTF-16-BE",
    "UTF-16-LE",
    "UTF-7",
    "UTF-8",
    "WINDOWS-1250",
    "WINDOWS-1251",
    "WINDOWS-1252",
    "WINDOWS-1253",
    "WINDOWS-1254",
    "WINDOWS-1255",
    "WINDOWS-1256",
    "WINDOWS-1257",
    "WINDOWS-1258"
]

SIZE_LIMIT_I18N = {
    SIZE_ANY: "any",
    SIZE_GT: "greater than",
    SIZE_EQ: "equal to",
    SIZE_LT: "less than"
}

TIME_LIMIT_I18N = {
    TIME_ANY: "on any",
    TIME_GT: "after",
    TIME_EQ: "on",
    TIME_LT: "before"
}


def eng_to_i18n(string, mapping):
    """Convert english to i18n."""

    i18n = None
    for k, v in mapping.items():
        if v == string:
            i18n = k
            break
    return i18n


def i18n_to_eng(string, mapping):
    """Convert i18n to english."""

    return mapping.get(string, None)


def setup_datepicker(obj, key):
    """Setup GenericDatePickerCtrl object."""

    d = Settings.get_search_setting(key, None)
    if d is None:
        day = wx.DateTime()
        day.SetToCurrent()
        obj.SetValue(day)
    else:
        day = wx.DateTime()
        saved_day = d.split("/")
        day.Set(int(saved_day[1]), int(saved_day[0]) - 1, int(saved_day[2]))
        obj.SetValue(day)


def setup_timepicker(obj, spin, key):
    """Setup time control object."""

    t = Settings.get_search_setting(key, wx.DateTime.Now().Format("%H:%M:%S"))
    obj.SetValue(t)
    obj.BindSpinButton(spin)


def setup_autocomplete_combo(obj, key, load_last=False, changed_callback=None, default=None):
    """Setup autocomplete object."""

    if default is None:
        default = []
    choices = Settings.get_search_setting(key, default)
    if choices == [] and choices != default:
        choices = default
    if changed_callback is not None:
        obj.set_changed_callback(changed_callback)
    obj.update_choices(choices, load_last=load_last)


def update_autocomplete(obj, key, load_last=False, default=None):
    """Convienance function for updating the AutoCompleteCombo choices."""

    if default is None:
        default = []
    choices = Settings.get_search_setting(key, default)
    if choices == [] and choices != default:
        choices = default
    obj.update_choices(choices, load_last)


class RummageThread(threading.Thread):
    """Threaded Rummage."""

    def __init__(self, args):
        """Set up Rummage thread with the rumcore object."""

        self.runtime = ""
        self.no_results = 0
        self.running = False
        self.file_search = len(args['chain']) == 0

        self.rummage = rumcore.Rummage(
            target=args['target'],
            searches=args['chain'],
            file_pattern=self.not_none(args['filepattern']),
            folder_exclude=self.not_none(args['directory_exclude']),
            flags=args['flags'],
            encoding=args['force_encode'],
            modified=args['modified_compare'],
            created=args['created_compare'],
            size=args['size_compare'],
            backup_ext=args['backup_ext'],
            regex_mode=args['regex_mode']
        )

        threading.Thread.__init__(self)

    def not_none(self, item, alt=None):
        """Return item if not None, else return the alternate."""

        return item if item is not None else alt

    def update_status(self):
        """Update status."""

        global _COMPLETED
        global _TOTAL
        global _RECORDS
        global _SKIPPED

        with _LOCK:
            _COMPLETED, _TOTAL, _SKIPPED, _RECORDS = self.rummage.get_status()
            _RECORDS -= self.no_results

    def done(self):
        """Check if thread is done running."""

        return not self.running

    def payload(self):
        """Execute the rummage command and gather results."""

        global _RESULTS
        global _COMPLETED
        global _TOTAL
        global _RECORDS
        global _ERRORS
        global _SKIPPED
        with _LOCK:
            _RESULTS = []
            _COMPLETED = 0
            _TOTAL = 0
            _RECORDS = 0
            _SKIPPED = 0
            _ERRORS = []
        for f in self.rummage.find():
            with _LOCK:
                if hasattr(f, 'skipped') and f.skipped:
                    self.no_results += 1
                elif f.error is None and (self.file_search or f.match is not None):
                    _RESULTS.append(f)
                else:
                    if isinstance(f, rumcore.FileRecord):
                        self.no_results += 1
                    if f.error is not None:
                        _ERRORS.append(f)
            self.update_status()
            wx.WakeUpIdle()

            if _ABORT:
                self.rummage.kill()

    def run(self):
        """Start the Rummage thread benchmark the time."""

        global _ABORT
        self.running = True
        start = time()

        try:
            self.payload()
        except Exception:
            error(traceback.format_exc())

        bench = time() - start
        runtime = BENCHMARK_STATUS % bench

        self.runtime = runtime
        self.running = False
        self.update_status()
        if _ABORT:
            _ABORT = False


class RummageArgs(object):
    """Rummage argument object."""

    def __init__(self):
        """Default the rummage args on instatiation."""

        self.reset()

    def reset(self):
        """Reset rummage args to defaults."""

        self.regexp = False
        self.ignore_case = False
        self.dotall = False
        self.recursive = False
        self.directory_exclude = None
        self.regexdirpattern = False
        self.regexfilepattern = None
        self.filepattern = None
        self.pattern = None
        self.target = None
        self.show_hidden = False
        self.size_compare = None
        self.modified_compare = None
        self.created_compare = None
        self.count_only = False
        self.unicode = False
        self.boolean = False
        self.backup = True
        self.replace = None
        self.force_encode = None
        self.backup_ext = None
        self.bestmatch = False
        self.enhancematch = False
        self.process_binary = False
        self.word = False
        self.reverse = False
        self.posix = False
        self.fullcase = False
        self.regex_mode = rumcore.RE_MODE
        self.regex_version = 0
        self.formatreplace = False


class RummageFrame(gui.RummageFrame, DebugFrameExtender):
    """Rummage Frame."""

    def __init__(self, parent, start_path, debug_mode=False):
        """Init the RummageFrame object."""

        super(RummageFrame, self).__init__(parent)

        self.hide_limit_panel = False

        self.SetIcon(
            data.get_image('rummage_medium.png' if util.platform() == 'linux' else 'rummage_large.png').GetIcon()
        )

        self.no_pattern = False
        self.paylod = {}
        self.error_dlg = None
        self.debounce_search = False
        self.searchin_update = False
        self.replace_plugin_update = False
        self.checking = False
        self.kill = False
        self.thread = None
        self.allow_update = False
        self.imported_plugins = {}
        if start_path is None:
            start_path = util.getcwd()

        if debug_mode:
            self.open_debug_console()

        # Setup debugging
        self.set_keybindings(
            [
                (wx.ACCEL_CMD if util.platform() == "osx" else wx.ACCEL_CTRL, ord('A'), self.on_textctrl_selectall),
                (wx.ACCEL_NORMAL, wx.WXK_RETURN, self.on_enter_key)
            ],
            debug_event=(self.on_debug_console if debug_mode else None)
        )

        # Update status on when idle
        self.Bind(wx.EVT_IDLE, self.on_idle)

        # Extend the statusbar
        custom_statusbar.extend_sb(self.m_statusbar)
        self.m_statusbar.set_status("")

        # Extend browse button
        pick_button.pick_extend(self.m_searchin_dir_picker, pick_button.PickButton)
        self.m_searchin_dir_picker.pick_init(
            pick_button.PickButton.DIR_TYPE,
            DIRECTORY_SELECT,
            pick_change_evt=self.on_dir_changed
        )
        pick_button.pick_extend(self.m_replace_plugin_dir_picker, pick_button.PickButton)
        self.m_replace_plugin_dir_picker.pick_init(
            pick_button.PickButton.FILE_TYPE,
            SCRIPT_SELECT,
            default_path=os.path.join(Settings.get_config_folder(), 'plugins'),
            pick_change_evt=self.on_replace_plugin_dir_changed
        )

        # Replace result panel placeholders with new custom panels
        self.m_result_file_list.load_list()
        self.m_result_list.load_list()
        self.m_grep_notebook.SetSelection(0)

        # Set progress bar to 0
        self.m_progressbar.SetRange(100)
        self.m_progressbar.SetValue(0)

        self.localize()

        # Setup the inputs history and replace
        # placeholder objects with actual objecs
        self.setup_inputs()

        # Pick optimal size
        self.optimize_size(True)
        if Settings.get_hide_limit():
            self.hide_limit_panel = True
            self.limit_panel_hide()
            self.m_hide_limit_menuitem.SetItemLabel(MENU_SHOW_LIMIT)

        self.init_search_path(start_path)

        self.refresh_regex_options()
        self.refresh_chain_mode()

        # So this is to fix some platform specific issues.
        # We will wait until we are sure we are loaded, then
        # We will fix mac focusing random elements, and we will
        # process and resize the window to fix Linux tab issues.
        # Linux seems to need the resize to get its control tab
        # order right as we are hiding some items, but doing it
        # now won't work, so we delay it.
        wx.CallLater(500, self.on_loaded).Start()

    def localize(self):
        """Localize."""

        self.m_settings_panel.GetSizer().GetItem(0).GetSizer().GetItem(0).GetSizer().GetStaticBox().SetLabel(
            SEARCH_REPLACE
        )
        self.m_settings_panel.GetSizer().GetItem(0).GetSizer().GetItem(1).GetSizer().GetStaticBox().SetLabel(
            LIMIT_SEARCH
        )
        self.m_search_button.SetLabel(SEARCH_BTN_SEARCH)
        self.m_replace_button.SetLabel(REPLACE_BTN_REPLACE)
        self.m_searchin_label.SetLabel(SEARCH_IN)
        self.m_searchfor_label.SetLabel(SEARCH_FOR)
        self.m_replace_label.SetLabel(REPLACE_WITH)
        self.m_size_is_label.SetLabel(SIZE_IS)
        self.m_modified_label.SetLabel(MODIFIED)
        self.m_created_label.SetLabel(CREATED)
        self.m_exclude_label.SetLabel(EXCLUDE)
        self.m_filematch_label.SetLabel(FILE_MATCH)
        self.m_regex_search_checkbox.SetLabel(SEARCH_WITH_REGEX)
        self.m_case_checkbox.SetLabel(CASE)
        self.m_dotmatch_checkbox.SetLabel(DOTALL)
        self.m_unicode_checkbox.SetLabel(UNICODE)
        self.m_force_encode_choice.SetSelection(0)
        self.m_boolean_checkbox.SetLabel(BOOLEAN)
        self.m_count_only_checkbox.SetLabel(COUNT_ONLY)
        self.m_backup_checkbox.SetLabel(CREATE_BACKUPS)
        self.m_force_encode_checkbox.SetLabel(FORCE)
        self.m_force_encode_choice.Clear()
        for x in ENCODINGS:
            self.m_force_encode_choice.Append(x)
        self.m_chains_checkbox.SetLabel(USE_CHAIN)
        self.m_replace_plugin_checkbox.SetLabel(USE_PLUGIN)
        self.m_bestmatch_checkbox.SetLabel(BESTMATCH)
        self.m_enhancematch_checkbox.SetLabel(FUZZY_FIT)
        self.m_word_checkbox.SetLabel(WORD)
        self.m_reverse_checkbox.SetLabel(REVERSE)
        self.m_posix_checkbox.SetLabel(POSIX)
        self.m_format_replace_checkbox.SetLabel(FORMAT)
        self.m_fullcase_checkbox.SetLabel(CASEFOLD)
        self.m_subfolder_checkbox.SetLabel(SUBFOLDERS)
        self.m_hidden_checkbox.SetLabel(HIDDEN)
        self.m_binary_checkbox.SetLabel(INCLUDE_BINARY)
        self.m_dirregex_checkbox.SetLabel(USE_REGEX)
        self.m_fileregex_checkbox.SetLabel(USE_REGEX)
        self.m_regex_test_button.SetLabel(TEST_REGEX)
        self.m_save_search_button.SetLabel(SAVE_SEARCH)
        self.m_load_search_button.SetLabel(LOAD_SEARCH)
        self.m_grep_notebook.SetPageText(0, SEARCH)
        exportid = self.m_menu.FindMenuItem("File", "Export")
        self.m_menu.SetLabel(exportid, MENU_EXPORT)
        self.m_menu.SetMenuLabel(0, MENU_FILE)
        self.m_menu.SetMenuLabel(1, MENU_VIEW)
        self.m_menu.SetMenuLabel(2, MENU_HELP)
        self.m_preferences_menuitem.SetItemLabel(MENU_PREFERENCES)
        self.m_quit_menuitem.SetItemLabel(MENU_EXIT)
        self.m_export_html_menuitem.SetItemLabel(MENU_HTML)
        self.m_export_csv_menuitem.SetItemLabel(MENU_CSV)
        self.m_hide_limit_menuitem.SetItemLabel(MENU_HIDE_LIMIT)
        self.m_log_menuitem.SetItemLabel(MENU_OPEN_LOG)
        self.m_about_menuitem.SetItemLabel(MENU_ABOUT)
        self.m_documentation_menuitem.SetItemLabel(MENU_DOCUMENTATION)
        self.m_issues_menuitem.SetItemLabel(MENU_HELP_SUPPORT)

        self.m_logic_choice.Clear()
        for x in [SIZE_ANY, SIZE_GT, SIZE_EQ, SIZE_LT]:
            self.m_logic_choice.Append(x)

        self.m_modified_choice.Clear()
        for x in [TIME_ANY, TIME_GT, TIME_EQ, TIME_LT]:
            self.m_modified_choice.Append(x)

        self.m_created_choice.Clear()
        for x in [TIME_ANY, TIME_GT, TIME_EQ, TIME_LT]:
            self.m_created_choice.Append(x)

    def init_search_path(self, start_path):
        """Initialize the search path input."""

        # Init search path with passed in path
        if start_path and os.path.exists(start_path):
            self.m_searchin_text.safe_set_value(os.path.abspath(os.path.normpath(start_path)))

    def optimize_size(self, first_time=False, height_only=False):
        """Optimally resize window."""

        best = self.m_settings_panel.GetBestSize()
        current = self.m_settings_panel.GetSize()
        offset = best[1] - current[1]
        mainframe = self.GetSize()
        if (first_time or offset > 0) and not height_only:
            sz = wx.Size(mainframe[0], mainframe[1] + offset + 15)
            if first_time:
                self.SetMinSize(sz)
            self.SetSize(sz)
        elif height_only:
            min_size = self.GetMinSize()
            self.SetMinSize(wx.Size(min_size[0], mainframe[1] + offset + 15))
            self.SetSize(wx.Size(mainframe[0], mainframe[1] + offset + 15))
        self.Refresh()

    def setup_inputs(self):
        """Setup and configure input objects."""

        self.m_regex_search_checkbox.SetValue(Settings.get_search_setting("regex_toggle", True))
        self.m_fileregex_checkbox.SetValue(Settings.get_search_setting("regex_file_toggle", False))
        self.m_dirregex_checkbox.SetValue(Settings.get_search_setting("regex_dir_toggle", False))

        self.m_logic_choice.SetStringSelection(
            eng_to_i18n(
                Settings.get_search_setting("size_compare_string", "any"),
                SIZE_LIMIT_I18N
            )
        )
        self.m_size_text.SetValue(Settings.get_search_setting("size_limit_string", "1000"))

        self.m_case_checkbox.SetValue(not Settings.get_search_setting("ignore_case_toggle", False))
        self.m_dotmatch_checkbox.SetValue(Settings.get_search_setting("dotall_toggle", False))
        self.m_unicode_checkbox.SetValue(Settings.get_search_setting("unicode_toggle", True))
        self.m_boolean_checkbox.SetValue(Settings.get_search_setting("boolean_toggle", False))
        self.m_count_only_checkbox.SetValue(Settings.get_search_setting("count_only_toggle", False))
        self.m_backup_checkbox.SetValue(Settings.get_search_setting("backup_toggle", True))
        self.m_force_encode_checkbox.SetValue(Settings.get_search_setting("force_encode_toggle", False))
        encode_val = Settings.get_search_setting("force_encode", "ASCII")
        index = self.m_force_encode_choice.FindString(encode_val)
        if index != wx.NOT_FOUND:
            self.m_force_encode_choice.SetSelection(index)
        self.m_bestmatch_checkbox.SetValue(Settings.get_search_setting("bestmatch_toggle", False))
        self.m_enhancematch_checkbox.SetValue(Settings.get_search_setting("enhancematch_toggle", False))
        self.m_word_checkbox.SetValue(Settings.get_search_setting("word_toggle", False))
        self.m_reverse_checkbox.SetValue(Settings.get_search_setting("reverse_toggle", False))
        self.m_posix_checkbox.SetValue(Settings.get_search_setting("posix_toggle", False))
        self.m_format_replace_checkbox.SetValue(Settings.get_search_setting("format_replace_toggle", False))
        self.m_fullcase_checkbox.SetValue(Settings.get_search_setting("fullcase_toggle", False))

        self.m_hidden_checkbox.SetValue(Settings.get_search_setting("hidden_toggle", False))
        self.m_subfolder_checkbox.SetValue(Settings.get_search_setting("recursive_toggle", True))
        self.m_binary_checkbox.SetValue(Settings.get_search_setting("binary_toggle", False))
        self.m_chains_checkbox.SetValue(Settings.get_search_setting("chain_toggle", False))
        self.m_replace_plugin_checkbox.SetValue(Settings.get_search_setting("replace_plugin_toggle", False))

        self.m_modified_choice.SetStringSelection(
            eng_to_i18n(
                Settings.get_search_setting("modified_compare_string", "on any"),
                TIME_LIMIT_I18N
            )
        )
        self.m_created_choice.SetStringSelection(
            eng_to_i18n(
                Settings.get_search_setting("created_compare_string", "on any"),
                TIME_LIMIT_I18N
            )
        )

        setup_datepicker(self.m_modified_date_picker, "modified_date_string")
        setup_datepicker(self.m_created_date_picker, "created_date_string")
        setup_timepicker(self.m_modified_time_picker, self.m_modified_spin, "modified_time_string")
        setup_timepicker(self.m_created_time_picker, self.m_created_spin, "created_time_string")
        setup_autocomplete_combo(self.m_searchin_text, "target", changed_callback=self.on_searchin_changed)

        if not self.m_chains_checkbox.GetValue():
            setup_autocomplete_combo(
                self.m_searchfor_textbox,
                "regex_search" if self.m_regex_search_checkbox.GetValue() else "literal_search"
            )
        else:
            self.setup_chains(Settings.get_search_setting("chain", ""))

        if self.m_replace_plugin_checkbox.GetValue():
            self.m_replace_label.SetLabel(REPLACE_PLUGIN)
            self.m_replace_plugin_dir_picker.Show()
            setup_autocomplete_combo(
                self.m_replace_textbox,
                "replace_plugin"
            )
        else:
            self.m_replace_plugin_dir_picker.Hide()
            setup_autocomplete_combo(
                self.m_replace_textbox,
                "regex_replace" if self.m_regex_search_checkbox.GetValue() else "literal_replace"
            )
        setup_autocomplete_combo(
            self.m_exclude_textbox,
            "regex_folder_exclude" if self.m_dirregex_checkbox.GetValue() else "folder_exclude",
            load_last=True
        )
        setup_autocomplete_combo(
            self.m_filematch_textbox,
            "regex_file_search" if self.m_fileregex_checkbox.GetValue() else "file_search",
            load_last=True,
            default=([".*"] if self.m_fileregex_checkbox.GetValue() else ["*?"])
        )

    def setup_chains(self, setup=None):
        """Setup chains."""

        is_selected = False
        selected = self.m_searchfor_textbox.Value
        chains = sorted(list(Settings.get_chains().keys()))

        for x in range(len(chains)):
            string = chains[x]
            if string == selected:
                is_selected = True

        if not is_selected and not setup:
            setup = Settings.get_search_setting("chain", "")
        elif is_selected and not setup:
            setup = selected

        if setup and setup in chains:
            self.m_searchfor_textbox.update_choices(chains)
            self.m_searchfor_textbox.SetValue(setup)
        else:
            self.m_searchfor_textbox.update_choices(chains, load_last=True)

    def refresh_regex_options(self):
        """Refresh the regex module options."""

        mode = Settings.get_regex_mode()
        if mode in rumcore.REGEX_MODES:
            self.m_word_checkbox.Show()
            self.m_enhancematch_checkbox.Show()
            self.m_bestmatch_checkbox.Show()
            self.m_reverse_checkbox.Show()
            self.m_posix_checkbox.Show()
            self.m_format_replace_checkbox.Show()
            if Settings.get_regex_version() == 0:
                self.m_fullcase_checkbox.Show()
            else:
                self.m_fullcase_checkbox.Hide()
        else:
            self.m_word_checkbox.Hide()
            self.m_enhancematch_checkbox.Hide()
            self.m_bestmatch_checkbox.Hide()
            self.m_reverse_checkbox.Hide()
            self.m_posix_checkbox.Hide()
            self.m_format_replace_checkbox.Hide()
            self.m_fullcase_checkbox.Hide()

    def refresh_chain_mode(self):
        """Refresh chain mode."""

        if self.m_chains_checkbox.GetValue():
            self.m_regex_search_checkbox.Enable(False)
            self.m_case_checkbox.Enable(False)
            self.m_dotmatch_checkbox.Enable(False)
            self.m_unicode_checkbox.Enable(False)
            self.m_bestmatch_checkbox.Enable(False)
            self.m_enhancematch_checkbox.Enable(False)
            self.m_word_checkbox.Enable(False)
            self.m_reverse_checkbox.Enable(False)
            self.m_posix_checkbox.Enable(False)
            self.m_format_replace_checkbox.Enable(False)
            self.m_fullcase_checkbox.Enable(False)

            self.m_replace_plugin_checkbox.Enable(False)

            self.m_searchfor_label.SetLabel(SEARCH_CHAIN)
            self.m_replace_label.Enable(False)
            self.m_replace_textbox.Enable(False)
            self.m_replace_plugin_dir_picker.Enable(False)

            self.m_save_search_button.Enable(False)
            self.setup_chains(Settings.get_search_setting("chain", ""))
            return True
        else:
            self.m_regex_search_checkbox.Enable(True)
            self.m_case_checkbox.Enable(True)
            self.m_dotmatch_checkbox.Enable(True)
            self.m_unicode_checkbox.Enable(True)
            self.m_bestmatch_checkbox.Enable(True)
            self.m_enhancematch_checkbox.Enable(True)
            self.m_word_checkbox.Enable(True)
            self.m_reverse_checkbox.Enable(True)
            self.m_posix_checkbox.Enable(True)
            self.m_format_replace_checkbox.Enable(True)
            self.m_fullcase_checkbox.Enable(True)

            self.m_replace_plugin_checkbox.Enable(True)

            self.m_searchfor_label.SetLabel(SEARCH_FOR)
            self.m_searchfor_textbox.Value = ""
            self.m_replace_label.Enable(True)
            self.m_replace_textbox.Enable(True)
            self.m_replace_plugin_dir_picker.Enable(True)

            self.m_save_search_button.Enable(True)
            update_autocomplete(
                self.m_searchfor_textbox,
                "regex_search" if self.m_regex_search_checkbox.GetValue() else "literal_search"
            )
            return False

    def limit_panel_toggle(self):
        """Show/Hide limit panel."""

        limit_box = self.m_settings_panel.GetSizer().GetItem(0).GetSizer().GetItem(1).GetSizer()
        if not self.hide_limit_panel:
            pth = self.m_searchin_text.GetValue()
            if os.path.isfile(pth) and limit_box.IsShown(0):
                limit_box.ShowItems(False)
                self.m_settings_panel.GetSizer().Layout()
                self.Refresh()
            elif os.path.isdir(pth) and not limit_box.IsShown(0):
                limit_box.ShowItems(True)
                limit_box.Fit(limit_box.GetStaticBox())
                limit_box.Layout()
                self.m_settings_panel.GetSizer().Layout()
                self.Refresh()
        elif limit_box.IsShown(0):
            limit_box.ShowItems(False)
            self.m_settings_panel.GetSizer().Layout()
            self.Refresh()

    def limit_panel_hide(self):
        """Hide the limit panel."""

        self.limit_panel_toggle()
        self.optimize_size(height_only=True)

    def check_searchin(self):
        """Determine if search in input is a file or not, and hide/show elements accordingly."""

        self.limit_panel_toggle()
        self.optimize_size(height_only=True)

        pth = self.m_searchin_text.GetValue()
        if not self.searchin_update:
            if os.path.isdir(pth):
                self.m_searchin_dir_picker.SetPath(pth)
            elif os.path.isfile(pth):
                self.m_searchin_dir_picker.SetPath(os.path.dirname(pth))
            self.searchin_update = False

    def start_search(self, replace=False):
        """Initiate search or stop search depending on search state."""

        global _ABORT
        if self.debounce_search:
            return
        self.debounce_search = True

        is_replacing = self.m_replace_button.GetLabel() in [SEARCH_BTN_STOP, SEARCH_BTN_ABORT]
        is_searching = self.m_search_button.GetLabel() in [SEARCH_BTN_STOP, SEARCH_BTN_ABORT]

        if is_searching or is_replacing:
            # Handle a search or replace request when a search or replace is already running

            if self.thread is not None and not self.kill:
                if is_replacing:
                    self.m_replace_button.SetLabel(SEARCH_BTN_ABORT)
                else:
                    self.m_search_button.SetLabel(SEARCH_BTN_ABORT)
                _ABORT = True
                self.kill = True
            else:
                self.debounce_search = False
        else:
            # Handle a search or a search & replace request

            if replace:
                message = [MSG_REPLACE_WARN]
                if not self.m_backup_checkbox.GetValue():
                    message.append(MSG_BACKUPS_DISABLED)

                if not yesno(' '.join(message)):
                    self.debounce_search = False
                    return

            is_chain = self.m_chains_checkbox.GetValue()
            chain = self.m_searchfor_textbox.Value if is_chain else None

            if is_chain and (not chain.strip() or chain not in Settings.get_chains()):
                errormsg(ERR_INVALID_CHAIN)
            elif not self.validate_search_inputs(replace=replace, chain=chain):
                self.do_search(replace=replace, chain=chain is not None)
            self.debounce_search = False

    def do_search(self, replace=False, chain=None):
        """Start the search."""

        self.thread = None

        # Reset status
        self.m_progressbar.SetRange(100)
        self.m_progressbar.SetValue(0)
        self.m_statusbar.set_status("")

        # Delete old plugins
        self.clear_plugins()

        # Remove errors icon in status bar
        if self.error_dlg is not None:
            self.error_dlg.Destroy()
            self.error_dlg = None
        self.m_statusbar.remove_icon("errors")

        try:
            # Setup arguments
            self.set_arguments(chain, replace)
        except Exception:
            self.clear_plugins()
            error(traceback.format_exc())
            errormsg(ERR_SETUP)
            return

        # Change button to stop search
        if replace:
            self.m_replace_button.SetLabel(SEARCH_BTN_STOP)
            self.m_search_button.Enable(False)
        else:
            self.m_search_button.SetLabel(SEARCH_BTN_STOP)
            self.m_replace_button.Enable(False)

        # Init search status
        self.m_statusbar.set_status(INIT_STATUS)

        # Setup search thread
        self.thread = RummageThread(self.payload)
        self.thread.setDaemon(True)

        # Reset result tables
        self.count = 0
        self.m_result_file_list.reset_list()
        self.m_result_list.reset_list()

        # Run search thread
        self.thread.start()
        self.allow_update = True

    def chain_flags(self, string, regexp):
        """Chain flags."""

        regex_mode = Settings.get_regex_mode()
        regex_version = Settings.get_regex_version()

        flags = rumcore.MULTILINE

        if regex_mode in rumcore.REGEX_MODES:
            if regex_version == 1:
                flags |= rumcore.VERSION1
            else:
                flags |= rumcore.VERSION0
                if "f" in string:
                    flags |= rumcore.FULLCASE

        if not regexp:
            flags |= rumcore.LITERAL
        elif "s" in string:
            flags |= rumcore.DOTALL

        if "u" in string:
            flags |= rumcore.UNICODE
        elif regex_mode == rumcore.REGEX_MODE:
            flags |= rumcore.ASCII

        if "i" in string:
            flags |= rumcore.IGNORECASE

        if regex_mode in rumcore.REGEX_MODES:
            if "b" in string:
                flags |= rumcore.BESTMATCH
            if "e" in string:
                flags |= rumcore.ENHANCEMATCH
            if "w" in string:
                flags |= rumcore.WORD
            if "r" in string:
                flags |= rumcore.REVERSE
            if "p" in string:
                flags |= rumcore.POSIX
            if "F" in string:
                flags |= rumcore.FORMATREPLACE

        return flags

    def get_flags(self, args):
        """Determine rumcore flags from RummageArgs."""

        flags = rumcore.MULTILINE | rumcore.TRUNCATE_LINES

        if args.regex_mode in rumcore.REGEX_MODES:
            if args.regex_version == 1:
                flags |= rumcore.VERSION1
            else:
                flags |= rumcore.VERSION0
                if args.fullcase:
                    flags |= rumcore.FULLCASE

        if args.regexfilepattern:
            flags |= rumcore.FILE_REGEX_MATCH

        if not args.regexp:
            flags |= rumcore.LITERAL
        elif args.dotall:
            flags |= rumcore.DOTALL

        if args.unicode:
            flags |= rumcore.UNICODE
        elif args.regex_mode == rumcore.REGEX_MODE:
            flags |= rumcore.ASCII

        if args.ignore_case:
            flags |= rumcore.IGNORECASE

        if args.recursive:
            flags |= rumcore.RECURSIVE

        if args.regexdirpattern:
            flags |= rumcore.DIR_REGEX_MATCH

        if args.show_hidden:
            flags |= rumcore.SHOW_HIDDEN

        if args.process_binary:
            flags |= rumcore.PROCESS_BINARY

        if args.count_only:
            flags |= rumcore.COUNT_ONLY

        if args.boolean:
            flags |= rumcore.BOOLEAN

        if args.backup:
            flags |= rumcore.BACKUP

        if args.regex_mode in rumcore.REGEX_MODES:
            if args.bestmatch:
                flags |= rumcore.BESTMATCH
            if args.enhancematch:
                flags |= rumcore.ENHANCEMATCH
            if args.word:
                flags |= rumcore.WORD
            if args.reverse:
                flags |= rumcore.REVERSE
            if args.posix:
                flags |= rumcore.POSIX
            if args.formatreplace:
                flags |= rumcore.FORMATREPLACE

        return flags

    def set_chain_arguments(self, chain, replace):
        """Set the search arguments."""

        search_chain = rumcore.Search(replace)
        searches = Settings.get_search()
        for search_name in Settings.get_chains()[chain]:
            search_obj = searches[search_name]
            if search_obj[5] and replace:
                replace_obj = self.import_plugin(search_obj[2])
            else:
                replace_obj = search_obj[2]

            search_chain.add(search_obj[1], replace_obj, self.chain_flags(search_obj[3], search_obj[4]))

        debug(search_chain)

        return search_chain

    def import_plugin(self, script):
        """Import replace plugin."""

        import imp

        if script not in self.imported_plugins:
            module = imp.new_module(script)
            with open(script, 'rb') as f:
                encoding = rumcore.text_decode._special_encode_check(f.read(256), '.py')
            with codecs.open(script, 'r', encoding=encoding.encode) as f:
                exec(
                    compile(
                        f.read(),
                        script,
                        'exec'
                    ),
                    module.__dict__
                )

            # Don't let the module get garbage collected
            # We will remove references when we are done with it.
            self.imported_plugins[script] = module

        return self.imported_plugins[script].get_replace()

    def clear_plugins(self):
        """Clear old plugins."""

        self.imported_plugins = {}

    def set_arguments(self, chain, replace):
        """Set the search arguments."""

        # Create a arguments structure from the GUI objects
        args = RummageArgs()

        # Path
        args.target = self.m_searchin_text.GetValue()

        # Search Options
        args.regex_mode = Settings.get_regex_mode()
        args.regexp = self.m_regex_search_checkbox.GetValue()
        args.ignore_case = not self.m_case_checkbox.GetValue()
        args.dotall = self.m_dotmatch_checkbox.GetValue()
        args.unicode = self.m_unicode_checkbox.GetValue()
        args.count_only = self.m_count_only_checkbox.GetValue()
        args.regex_version = Settings.get_regex_version()
        if args.regex_mode in rumcore.REGEX_MODES:
            args.bestmatch = self.m_bestmatch_checkbox.GetValue()
            args.enhancematch = self.m_enhancematch_checkbox.GetValue()
            args.word = self.m_word_checkbox.GetValue()
            args.reverse = self.m_reverse_checkbox.GetValue()
            args.posix = self.m_posix_checkbox.GetValue()
            args.formatreplace = self.m_format_replace_checkbox.GetValue()
            if args.regex_version == 0:
                args.fullcase = self.m_fullcase_checkbox.GetValue()
        args.boolean = self.m_boolean_checkbox.GetValue()
        args.backup = self.m_backup_checkbox.GetValue()
        args.force_encode = None
        if self.m_force_encode_checkbox.GetValue():
            args.force_encode = self.m_force_encode_choice.GetStringSelection()
        args.backup_ext = 'rum-bak'
        args.recursive = self.m_subfolder_checkbox.GetValue()
        args.pattern = self.m_searchfor_textbox.Value
        args.replace = self.m_replace_textbox.Value if replace else None

        # Limit Options
        if os.path.isdir(args.target):
            args.process_binary = self.m_binary_checkbox.GetValue()
            args.show_hidden = self.m_hidden_checkbox.GetValue()

            args.filepattern = self.m_filematch_textbox.Value
            if self.m_fileregex_checkbox.GetValue():
                args.regexfilepattern = True

            if self.m_exclude_textbox.Value != "":
                args.directory_exclude = self.m_exclude_textbox.Value
            if self.m_dirregex_checkbox.GetValue():
                args.regexdirpattern = True

            cmp_size = self.m_logic_choice.GetSelection()
            if cmp_size:
                size = decimal.Decimal(self.m_size_text.GetValue())
                args.size_compare = (LIMIT_COMPARE[cmp_size], int(round(size * decimal.Decimal(1024))))
            else:
                args.size_compare = None
            cmp_modified = self.m_modified_choice.GetSelection()
            cmp_created = self.m_created_choice.GetSelection()
            if cmp_modified:
                args.modified_compare = (
                    LIMIT_COMPARE[cmp_modified],
                    epoch_timestamp.local_time_to_epoch_timestamp(
                        self.m_modified_date_picker.GetValue().Format("%m/%d/%Y"),
                        self.m_modified_time_picker.GetValue()
                    )
                )
            if cmp_created:
                args.created_compare = (
                    LIMIT_COMPARE[cmp_created],
                    epoch_timestamp.local_time_to_epoch_timestamp(
                        self.m_modified_date_picker.GetValue().Format("%m/%d/%Y"),
                        self.m_modified_time_picker.GetValue()
                    )
                )
        else:
            args.process_binary = True

        # Track whether we have an actual search pattern,
        # if we are doing a boolean search,
        # or if we are only counting matches
        self.no_pattern = not args.pattern
        self.is_boolean = args.boolean
        self.is_count_only = args.count_only

        # Setup payload to pass to Rummage thread
        flags = self.get_flags(args)

        # Setup chain argument
        if chain:
            search_chain = self.set_chain_arguments(args.pattern, replace)
        else:
            search_chain = rumcore.Search(args.replace is not None)
            if not self.no_pattern:
                if self.m_replace_plugin_checkbox.GetValue() and replace:
                    replace = self.import_plugin(args.replace)
                else:
                    replace = args.replace
                search_chain.add(args.pattern, replace, flags & rumcore.SEARCH_MASK)

        self.payload = {
            'target': args.target,
            'chain': search_chain,
            'flags': flags & rumcore.FILE_MASK,
            'filepattern': args.filepattern,
            'directory_exclude': args.directory_exclude,
            'force_encode': args.force_encode,
            'modified_compare': args.modified_compare,
            'created_compare': args.created_compare,
            'size_compare': args.size_compare,
            'backup_ext': args.backup_ext,
            'regex_mode': args.regex_mode
        }

        # Save GUI history
        self.save_history(args, replace, chain=chain)

    def save_history(self, args, replace, chain):
        """
        Save the current configuration of the search for the next time the app is opened.

        Save a history of search directory, regex, folders, and excludes as well for use again in the future.
        """

        history = [
            ("target", args.target),
            ("regex_replace", args.replace) if args.regexp else ("literal_replace", args.replace)
        ]

        if not chain:
            history.append(("regex_search", args.pattern) if args.regexp else ("literal_search", args.pattern))

            if replace:
                if self.m_replace_plugin_checkbox.GetValue():
                    history.append(
                        ("replace_plugin", args.replace)
                    )
                else:
                    history.append(
                        ("regex_replace", args.replace) if args.regexp else ("literal_replace", args.replace)
                    )

        if os.path.isdir(args.target):
            history += [
                (
                    "regex_folder_exclude", args.directory_exclude
                ) if self.m_dirregex_checkbox.GetValue() else ("folder_exclude", args.directory_exclude),
                (
                    "regex_file_search", args.filepattern
                ) if self.m_fileregex_checkbox.GetValue() else ("file_search", args.filepattern)
            ]

        toggles = [
            ("regex_toggle", args.regexp),
            ("ignore_case_toggle", args.ignore_case),
            ("dotall_toggle", args.dotall),
            ("unicode_toggle", args.unicode),
            ("backup_toggle", args.backup),
            ("force_encode_toggle", args.force_encode is not None),
            ("recursive_toggle", args.recursive),
            ("hidden_toggle", args.show_hidden),
            ("binary_toggle", args.process_binary),
            ("regex_file_toggle", self.m_fileregex_checkbox.GetValue()),
            ("regex_dir_toggle", self.m_dirregex_checkbox.GetValue()),
            ("boolean_toggle", args.boolean),
            ("count_only_toggle", args.count_only),
            ("bestmatch_toggle", args.bestmatch),
            ("enhancematch_toggle", args.enhancematch),
            ("word_toggle", args.word),
            ("reverse_toggle", args.reverse),
            ("posix_toggle", args.posix),
            ("format_replace_toggle", args.formatreplace),
            ("chain_toggle", self.m_chains_checkbox.GetValue()),
            ('replace_plugin_toggle', self.m_replace_plugin_checkbox.GetValue())
        ]

        if Settings.get_regex_version() == 0:
            toggles.append(("fullcase_toggle", args.fullcase))

        eng_size = i18n_to_eng(self.m_logic_choice.GetStringSelection(), SIZE_LIMIT_I18N)
        eng_mod = i18n_to_eng(self.m_modified_choice.GetStringSelection(), TIME_LIMIT_I18N)
        eng_cre = i18n_to_eng(self.m_created_choice.GetStringSelection(), TIME_LIMIT_I18N)
        strings = [
            ("size_compare_string", eng_size),
            ("modified_compare_string", eng_mod),
            ("created_compare_string", eng_cre)
        ]

        if chain:
            chain_name = self.m_searchfor_textbox.Value
            strings.append(('chain', chain_name if chain_name else ''))

        strings.append(("force_encode", self.m_force_encode_choice.GetStringSelection()))

        if eng_size != "any":
            strings += [("size_limit_string", self.m_size_text.GetValue())]
        if eng_mod != "on any":
            strings += [
                ("modified_date_string", self.m_modified_date_picker.GetValue().Format("%m/%d/%Y")),
                ("modified_time_string", self.m_modified_time_picker.GetValue())
            ]
        if eng_cre != "on any":
            strings += [
                ("created_date_string", self.m_created_date_picker.GetValue().Format("%m/%d/%Y")),
                ("created_time_string", self.m_created_time_picker.GetValue())
            ]

        Settings.add_search_settings(history, toggles, strings)

        # Update the combo boxes history for related items
        update_autocomplete(self.m_searchin_text, "target")

        if not chain:
            update_autocomplete(
                self.m_searchfor_textbox,
                "regex_search" if self.m_regex_search_checkbox.GetValue() else "literal_search"
            )
            if replace:
                if self.m_replace_plugin_checkbox.GetValue():
                    update_autocomplete(
                        self.m_replace_textbox,
                        "replace_plugin"
                    )
                else:
                    update_autocomplete(
                        self.m_replace_textbox,
                        "regex_replace" if self.m_regex_search_checkbox.GetValue() else "literal_replace"
                    )

        update_autocomplete(
            self.m_exclude_textbox,
            "regex_folder_exclude" if self.m_dirregex_checkbox.GetValue() else "folder_exclude"
        )
        update_autocomplete(
            self.m_filematch_textbox,
            "regex_file_search" if self.m_fileregex_checkbox.GetValue() else "file_search"
        )

    def check_updates(self):
        """Check if updates to the result lists can be done."""

        if not self.checking and self.allow_update:
            self.checking = True
            is_complete = self.thread.done()
            debug("Processing current results")
            with _LOCK:
                completed = _COMPLETED
                total = _TOTAL
                records = _RECORDS
                skipped = _SKIPPED
            count = self.count
            if records > count or not is_complete:
                with _LOCK:
                    results = _RESULTS[0:records - count]
                    del _RESULTS[0:records - count]
                count = self.update_table(count, completed, total, skipped, *results)
            else:
                self.m_statusbar.set_status(
                    UPDATE_STATUS % (
                        completed,
                        total,
                        int(float(completed) / float(total) * 100) if total != 0 else 0,
                        skipped,
                        count
                    )
                )
                self.m_progressbar.SetRange(total if total else 100)
                self.m_progressbar.SetValue(completed)
            self.count = count

            # Run is finished or has been terminated
            if is_complete:
                benchmark = self.thread.runtime
                self.m_search_button.SetLabel(SEARCH_BTN_SEARCH)
                self.m_replace_button.SetLabel(REPLACE_BTN_REPLACE)
                self.m_search_button.Enable(True)
                self.m_replace_button.Enable(True)
                self.clear_plugins()
                if self.kill:
                    self.m_statusbar.set_status(
                        FINAL_STATUS % (
                            completed,
                            total,
                            int(float(completed) / float(total) * 100) if total != 0 else 0,
                            skipped,
                            count,
                            benchmark
                        )
                    )
                    self.m_progressbar.SetRange(total)
                    self.m_progressbar.SetValue(completed)
                    if Settings.get_notify():
                        notify.error(
                            NOTIFY_SEARCH_ABORTED,
                            NOTIFY_MATCHES_FOUND % count,
                            sound=Settings.get_alert()
                        )
                    elif Settings.get_alert():
                        notify.play_alert()
                    self.kill = False
                    global _ABORT
                    if _ABORT:
                        _ABORT = False
                else:
                    self.m_statusbar.set_status(
                        FINAL_STATUS % (
                            completed,
                            total,
                            100,
                            skipped,
                            count,
                            benchmark
                        )
                    )
                    self.m_progressbar.SetRange(100)
                    self.m_progressbar.SetValue(100)
                    if Settings.get_notify():
                        notify.info(
                            NOTIFY_SEARCH_COMPLETED,
                            NOTIFY_MATCHES_FOUND % count,
                            sound=Settings.get_alert()
                        )
                    elif Settings.get_alert():
                        notify.play_alert()
                with _LOCK:
                    errors = _ERRORS[:]
                    del _ERRORS[:]
                if errors:
                    self.error_dlg = SearchErrorDialog(self, errors)
                    self.m_statusbar.set_icon(
                        SB_ERRORS,
                        data.get_bitmap('error.png'),
                        msg=SB_TOOLTIP_ERR % len(errors),
                        click_left=self.on_error_click
                    )
                self.m_result_file_list.load_list()
                self.m_result_list.load_list()
                self.m_grep_notebook.SetSelection(1)
                self.debounce_search = False
                self.allow_update = False
                self.thread = None
            self.checking = False

    def update_table(self, count, done, total, skipped, *results):
        """Update the result lists with current search results."""

        p_range = self.m_progressbar.GetRange()
        p_value = self.m_progressbar.GetValue()
        actually_done = done - 1 if done > 0 else 0
        for f in results:
            self.m_result_file_list.set_match(f, self.no_pattern)
            if (self.is_count_only or self.is_boolean or self.payload['chain'].is_replace() or self.no_pattern):
                count += 1
                continue

            self.m_result_list.set_match(f)
            count += 1

        if total != 0:
            if p_range != total:
                self.m_progressbar.SetRange(total)
            if p_value != done:
                self.m_progressbar.SetValue(actually_done)
        self.m_statusbar.set_status(
            UPDATE_STATUS % (
                (
                    actually_done, total,
                    int(float(actually_done) / float(total) * 100),
                    skipped,
                    count
                ) if total != 0 else (0, 0, 0, 0, 0)
            )
        )
        return count

    def validate_search_inputs(self, replace=False, chain=None):
        """Validate the search inputs."""

        debug("validate")
        fail = False
        msg = ""

        if not fail and not os.path.exists(self.m_searchin_text.GetValue()):
            msg = ERR_INVALID_SEARCH_PTH
            fail = True

        if chain is None:
            if not fail and self.m_regex_search_checkbox.GetValue():
                if (self.m_searchfor_textbox.GetValue() == "" and replace) or self.validate_search_regex():
                    msg = ERR_INVALID_SEARCH
                    fail = True
            elif not fail and self.m_searchfor_textbox.GetValue() == "" and replace:
                msg = ERR_INVALID_SEARCH
                fail = True
        else:
            chain_searches = Settings.get_chains().get(chain, {})
            if not chain_searches:
                msg = ERR_EMPTY_CHAIN
                fail = True
            else:
                searches = Settings.get_search()
                for search in chain_searches:
                    s = searches.get(search)
                    if s is None:
                        msg = ERR_MISSING_SEARCH % search
                        fail = True
                        break
                    if self.validate_chain_regex(s[1], self.chain_flags(s[3], s[4])):
                        msg = ERR_INVALID_CHAIN_SEARCH % search
                        fail = True
                        break

        if not fail and not os.path.isfile(self.m_searchin_text.GetValue()):
            if not fail and self.m_fileregex_checkbox.GetValue():
                if (
                    self.m_filematch_textbox.GetValue().strip() == "" or
                    self.validate_regex(self.m_filematch_textbox.Value)
                ):
                    msg = ERR_INVALID_FILE_SEARCH
                    fail = True
            elif not fail and self.m_filematch_textbox.GetValue().strip() == "":
                msg = ERR_INVALID_FILE_SEARCH
                fail = True
            if not fail and self.m_dirregex_checkbox.GetValue():
                if self.validate_regex(self.m_exclude_textbox.Value):
                    msg = ERR_INVALID_EXCLUDE
                    fail = True

            try:
                value = float(self.m_size_text.GetValue())
            except ValueError:
                value = None
            if (
                not fail and
                self.m_logic_choice.GetStringSelection() != "any" and
                value is None
            ):
                msg = ERR_INVLAID_SIZE
                fail = True
            if not fail:
                try:
                    self.m_modified_date_picker.GetValue().Format("%m/%d/%Y")
                except Exception:
                    msg = ERR_INVALID_MDATE
                    fail = True
            if not fail:
                try:
                    self.m_created_date_picker.GetValue().Format("%m/%d/%Y")
                except Exception:
                    msg = ERR_INVALID_CDATE
                    fail = True
        if fail:
            errormsg(msg)
        return fail

    def validate_search_regex(self):
        """Validate search regex."""

        mode = Settings.get_regex_mode()
        if mode in rumcore.REGEX_MODES:
            import regex

            engine = bregex if rumcore.BREGEX_MODE else regex
            flags = engine.MULTILINE
            version = Settings.get_regex_version()
            if version == 1:
                flags |= engine.VERSION1
            else:
                flags |= engine.VERSION0
            if self.m_dotmatch_checkbox.GetValue():
                flags |= engine.DOTALL
            if not self.m_case_checkbox.GetValue():
                flags |= engine.IGNORECASE
            if self.m_unicode_checkbox.GetValue():
                flags |= engine.UNICODE
            else:
                flags |= engine.ASCII
            if self.m_bestmatch_checkbox.GetValue():
                flags |= engine.BESTMATCH
            if self.m_enhancematch_checkbox.GetValue():
                flags |= engine.ENHANCEMATCH
            if self.m_word_checkbox.GetValue():
                flags |= engine.WORD
            if self.m_reverse_checkbox.GetValue():
                flags |= engine.REVERSE
            if self.m_posix_checkbox.GetValue():
                flags |= engine.POSIX
            if version == 0 and self.m_fullcase_checkbox.GetValue():
                flags |= engine.FULLCASE
        else:
            engine = bre if mode == rumcore.BRE_MODE else re
            flags = engine.MULTILINE
            if self.m_dotmatch_checkbox.GetValue():
                flags |= engine.DOTALL
            if not self.m_case_checkbox.GetValue():
                flags |= engine.IGNORECASE
            if self.m_unicode_checkbox.GetValue():
                flags |= engine.UNICODE
        return self.validate_regex(self.m_searchfor_textbox.Value, flags)

    def validate_chain_regex(self, pattern, cflags):
        """Validate chain regex."""

        mode = Settings.get_regex_mode()
        if mode in rumcore.REGEX_MODES:
            import regex

            engine = bregex if mode == rumcore.BREGEX_MODE else regex
            flags = engine.MULTILINE
            if cflags & rumcore.VERSION1:
                flags |= engine.VERSION1
            else:
                flags |= engine.VERSION0
            if cflags & rumcore.DOTALL:
                flags |= engine.DOTALL
            if cflags & rumcore.IGNORECASE:
                flags |= engine.IGNORECASE
            if cflags & rumcore.UNICODE:
                flags |= engine.UNICODE
            else:
                flags |= engine.ASCII
            if cflags & rumcore.BESTMATCH:
                flags |= engine.BESTMATCH
            if cflags & rumcore.ENHANCEMATCH:
                flags |= engine.ENHANCEMATCH
            if cflags & rumcore.WORD:
                flags |= engine.WORD
            if cflags & rumcore.REVERSE:
                flags |= engine.REVERSE
            if cflags & rumcore.POSIX:
                flags |= engine.POSIX
            if flags & engine.VERSION0 and cflags & rumcore.FULLCASE:
                flags |= engine.FULLCASE
        else:
            engine = bre if mode == rumcore.BRE_MODE else re
            flags = engine.MULTILINE
            if cflags & rumcore.DOTALL:
                flags |= engine.DOTALL
            if cflags & rumcore.IGNORECASE:
                flags |= engine.IGNORECASE
            if cflags & rumcore.UNICODE:
                flags |= engine.UNICODE

        return self.validate_regex(self.m_searchfor_textbox.Value, flags)

    def validate_regex(self, pattern, flags=0):
        """Validate regular expresion compiling."""

        try:
            mode = Settings.get_regex_mode()
            if mode == rumcore.BREGEX_MODE:
                if flags == 0:
                    flags = bregex.ASCII
                bregex.compile_search(pattern, flags)
            elif mode == rumcore.REGEX_MODE:
                import regex
                if flags == 0:
                    flags = regex.ASCII
                regex.compile(pattern, flags)
            elif mode == rumcore.BRE_MODE:
                bre.compile_search(pattern, flags)
            else:
                re.compile(pattern, flags)
            return False
        except Exception:
            debug('Pattern: %s' % pattern)
            debug('Flags: %s' % hex(flags))
            debug(traceback.format_exc())
            return True

    def on_loaded(self):
        """
        Stupid workarounds on load.

        Focus after loaded (stupid macOS workaround) and select the appropriate entry.
        Resize window after we are sure everything is loaded (stupid Linux workaround) to fix tab order stuff.
        """

        if self.m_chains_checkbox.GetValue():
            self.m_searchin_text.GetTextCtrl().SetFocus()
        else:
            self.m_searchfor_textbox.GetTextCtrl().SetFocus()
        self.Refresh()

        self.Fit()
        self.m_settings_panel.GetSizer().Layout()
        self.optimize_size(height_only=True)

    def on_enter_key(self, event):
        """Search on enter."""

        obj = self.FindFocus()
        is_ac_combo = isinstance(obj, AutoCompleteCombo)
        is_date_picker = isinstance(obj, wx.adv.GenericDatePickerCtrl)
        is_button = isinstance(obj, wx.Button)
        if (
            (
                is_ac_combo and not obj.IsPopupShown() or
                (not is_ac_combo and not is_date_picker and not is_button)
            ) and
            self.m_grep_notebook.GetSelection() == 0
        ):
            self.start_search()
        elif is_button:
            wx.PostEvent(
                obj.GetEventHandler(),
                wx.PyCommandEvent(wx.EVT_BUTTON.typeId, obj.GetId())
            )

        event.Skip()

    def on_textctrl_selectall(self, event):
        """Select all in the TextCtrl and AutoCompleteCombo objects."""

        text = self.FindFocus()
        if isinstance(text, (wx.TextCtrl, AutoCompleteCombo)):
            text.SelectAll()
        event.Skip()

    def on_chain_click(self, event):
        """Chain button click."""

        dlg = SearchChainDialog(self)
        dlg.ShowModal()
        dlg.Destroy()
        if self.m_chains_checkbox.GetValue():
            self.setup_chains()

    def on_plugin_function_click(self, event):
        """Plugin function click."""

        self.setup

    def on_preferences(self, event):
        """Show settings dialog, and update history of AutoCompleteCombo if the history was cleared."""

        dlg = SettingsDialog(self)
        dlg.ShowModal()
        if dlg.history_cleared():
            update_autocomplete(self.m_searchin_text, "target")

            if not self.m_chains_checkbox.GetValue():
                update_autocomplete(
                    self.m_searchfor_textbox,
                    "regex_search" if self.m_regex_search_checkbox.GetValue() else "literal_search"
                )

            if self.m_replace_plugin_checkbox.GetValue():
                update_autocomplete(
                    self.m_replace_textbox,
                    "replace_plugin"
                )
            else:
                update_autocomplete(
                    self.m_replace_textbox,
                    "regex_replace" if self.m_regex_search_checkbox.GetValue() else "literal_replace"
                )
            update_autocomplete(
                self.m_exclude_textbox,
                "regex_folder_exclude" if self.m_dirregex_checkbox.GetValue() else "folder_exclude"
            )
            update_autocomplete(
                self.m_filematch_textbox,
                "regex_file_search" if self.m_fileregex_checkbox.GetValue() else "file_search",
                default=([".*"] if self.m_fileregex_checkbox.GetValue() else ["*?"])
            )
        dlg.Destroy()
        self.refresh_regex_options()
        self.m_settings_panel.GetSizer().Layout()
        self.optimize_size(height_only=True)

    def on_chain_toggle(self, event):
        """Handle chain toggle event."""

        self.refresh_chain_mode()
        self.m_settings_panel.GetSizer().Layout()

    def on_plugin_function_toggle(self, event):
        """Handle plugin function toggle."""

        if self.m_replace_plugin_checkbox.GetValue():
            self.m_replace_label.SetLabel(REPLACE_PLUGIN)
            self.m_replace_plugin_dir_picker.Show()
            update_autocomplete(
                self.m_replace_textbox,
                "replace_plugin"
            )
        else:
            self.m_replace_label.SetLabel(REPLACE_WITH)
            self.m_replace_plugin_dir_picker.Hide()
            update_autocomplete(
                self.m_replace_textbox,
                "regex_replace" if self.m_regex_search_checkbox.GetValue() else "literal_replace"
            )
        self.m_settings_panel.GetSizer().Layout()

    def on_dir_changed(self, event):
        """Event for when the directory changes in the DirPickButton."""

        if not self.searchin_update:
            pth = event.target
            if pth is not None and os.path.exists(pth):
                self.searchin_update = True
                self.m_searchin_text.safe_set_value(pth)
                self.searchin_update = False
        event.Skip()

    def on_replace_plugin_dir_changed(self, event):
        """Handle replace plugin dir change."""

        if not self.replace_plugin_update:
            pth = event.target
            if pth is not None and os.path.exists(pth):
                self.replace_plugin_update = True
                self.m_replace_textbox.safe_set_value(pth)
                self.replace_plugin_update = False
        event.Skip()

    def on_searchin_changed(self):
        """Callback for when a directory changes via the m_searchin_text control."""

        self.check_searchin()
        self.SetTitle(self.m_searchin_text.GetValue())

    def on_save_search(self, event):
        """Open a dialog to save a search for later use."""

        search = self.m_searchfor_textbox.GetValue()
        if search == "":
            errormsg(ERR_EMPTY_SEARCH)
            return
        dlg = SaveSearchDialog(self)
        dlg.ShowModal()
        dlg.Destroy()

    def on_load_search(self, event):
        """Show dialog to pick saved a saved search to use."""

        dlg = LoadSearchDialog(self)
        dlg.ShowModal()
        dlg.Destroy()

    def on_search_click(self, event):
        """Search button click."""

        self.start_search()
        event.Skip()

    def on_replace_click(self, event):
        """Replace button click."""

        self.start_search(replace=True)
        event.Skip()

    def on_idle(self, event):
        """On idle event."""

        self.check_updates()
        event.Skip()

    def on_error_click(self, event):
        """Handle error icon click."""

        event.Skip()
        if self.error_dlg is not None:
            self.error_dlg.ShowModal()

    def on_regex_search_toggle(self, event):
        """Switch literal/regex history depending on toggle state."""

        if self.m_regex_search_checkbox.GetValue():
            if not self.m_chains_checkbox.GetValue():
                update_autocomplete(self.m_searchfor_textbox, "regex_search")
            if self.m_replace_plugin_checkbox.GetValue():
                update_autocomplete(self.m_replace_textbox, "replace_plugin")
            else:
                update_autocomplete(self.m_replace_textbox, "regex_replace")
        else:
            if not self.m_chains_checkbox.GetValue():
                update_autocomplete(self.m_searchfor_textbox, "literal_search")
            if self.m_replace_plugin_checkbox.GetValue():
                update_autocomplete(self.m_replace_textbox, "replace_plugin")
            else:
                update_autocomplete(self.m_replace_textbox, "literal_replace")

    def on_fileregex_toggle(self, event):
        """Switch literal/regex history depending on toggle state."""

        if self.m_fileregex_checkbox.GetValue():
            update_autocomplete(self.m_filematch_textbox, "regex_file_search", default=[".*"])
        else:
            update_autocomplete(self.m_filematch_textbox, "file_search", default=["*?"])
        event.Skip()

    def on_dirregex_toggle(self, event):
        """Switch literal/regex history depending on toggle state."""

        if self.m_dirregex_checkbox.GetValue():
            update_autocomplete(self.m_exclude_textbox, "regex_folder_exclude")
        else:
            update_autocomplete(self.m_exclude_textbox, "folder_exclude")
        event.Skip()

    def on_debug_console(self, event):
        """Show debug console."""

        self.toggle_debug_console()

    def on_close(self, event):
        """Ensure thread is stopped, notifications are destroyed, debug console is closed."""

        global _ABORT

        if self.thread is not None:
            _ABORT = True
        notify.destroy_notifications()
        self.close_debug_console()
        event.Skip()

    def on_test_regex(self, event):
        """Show regex test dialog."""

        tester = RegexTestDialog(self)
        tester.ShowModal()
        tester.Destroy()

    def on_export_html(self, event):
        """Export to HTML."""

        if (
            len(self.m_result_file_list.itemDataMap) == 0 and
            len(self.m_result_list.itemDataMap) == 0
        ):
            errormsg(ERR_NOTHING_TO_EXPORT)
            return
        html_file = filepickermsg(EXPORT_TO, wildcard="*.html", save=True)
        if html_file is None:
            return
        try:
            export_html.export(
                html_file,
                self.payload['chain'],
                self.m_result_file_list.itemDataMap,
                self.m_result_list.itemDataMap
            )
        except Exception:
            error(traceback.format_exc())
            errormsg(ERR_HTML_FAILED)

    def on_export_csv(self, event):
        """Export to CSV."""

        if (
            len(self.m_result_file_list.itemDataMap) == 0 and
            len(self.m_result_list.itemDataMap) == 0
        ):
            errormsg(ERR_NOTHING_TO_EXPORT)
            return
        csv_file = filepickermsg(EXPORT_TO, wildcard="*.csv", save=True)
        if csv_file is None:
            return
        try:
            export_csv.export(
                csv_file,
                self.payload['chain'],
                self.m_result_file_list.itemDataMap,
                self.m_result_list.itemDataMap
            )
        except Exception:
            error(traceback.format_exc())
            errormsg(ERR_CSV_FAILED)

    def on_hide_limit(self, event):
        """Hide limit panel."""

        self.hide_limit_panel = not self.hide_limit_panel
        self.limit_panel_hide()
        Settings.set_hide_limit(self.hide_limit_panel)
        if self.hide_limit_panel:
            self.m_hide_limit_menuitem.SetItemLabel(MENU_SHOW_LIMIT)
        else:
            self.m_hide_limit_menuitem.SetItemLabel(MENU_HIDE_LIMIT)

    def on_show_log_file(self, event):
        """Show user files in editor."""

        try:
            logfile = simplelog.get_global_log().filename
        except Exception:
            logfile = None

        if logfile is None or not os.path.exists(logfile):
            error(traceback.format_exc())
            errormsg(ERR_NO_LOG)
        else:
            open_editor.open_editor(logfile, 1, 1)

    def on_documentation(self, event):
        """Open documentation site."""

        webbrowser.open_new_tab(__meta__.__manual__)

    def on_issues(self, event):
        """Open issues site."""

        webbrowser.open_new_tab(__meta__.__help__)

    def on_about(self, event):
        """Show about dialog."""

        dlg = AboutDialog(self)
        dlg.ShowModal()
        dlg.Destroy()

    def on_exit(self, event):
        """Close dialog."""

        self.Close()
