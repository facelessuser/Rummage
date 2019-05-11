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
from datetime import datetime
import wx.lib.newevent
from backrefs import bre
from .settings import Settings
from .actions import export_html
from .actions import export_csv
from .actions import fileops
from .actions import updates
from .generic_dialogs import errormsg, yesno, infomsg
from .app.custom_app import debug, error, get_log_file
from .controls import custom_statusbar
from .regex_test_dialog import RegexTestDialog
from .controls.autocomplete_combo import AutoCompleteCombo
from .load_search_dialog import LoadSearchDialog
from .save_search_dialog import SaveSearchDialog
from .search_error_dialog import SearchErrorDialog
from .search_chain_dialog import SearchChainDialog
from .export_settings_dialog import ExportSettingsDialog
from .import_settings_dialog import ImportSettingsDialog
from .support_info_dialog import SupportInfoDialog
from .checksum_dialog import ChecksumDialog  # noqa: F401
from .delete_dialog import DeleteDialog  # noqa: F401
from .column_dialog import ColumnDialog  # noqa: F401
from .settings_dialog import SettingsDialog
from . import html_dialog
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
if rumcore.REGEX_SUPPORT:
    from backrefs import bregex
else:
    bregex = None

PostResizeEvent, EVT_POST_RESIZE = wx.lib.newevent.NewEvent()

_LOCK = threading.Lock()
_RESULTS = []
_COMPLETED = 0
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

ENCODINGS = util.get_encodings()


def eng_to_i18n(string, mapping):
    """Convert English to i18n."""

    i18n = None
    for k, v in mapping.items():
        if v == string:
            i18n = k
            break
    return i18n


def i18n_to_eng(string, mapping):
    """Convert i18n to English."""

    return mapping.get(string, None)


def setup_datepicker(obj, key):
    """Setup `GenericDatePickerCtrl` object."""

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
    """Convenience function for updating the `AutoCompleteCombo` choices."""

    if default is None:
        default = []
    choices = Settings.get_search_setting(key, default)
    if choices == [] and choices != default:
        choices = default
    obj.update_choices(choices, load_last)


class RummageThread(threading.Thread):
    """Threaded Rummage."""

    def __init__(self, args):
        """Set up Rummage thread with the `rumcore` object."""

        self.localize()

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
            backup_location=args['backup_location'],
            regex_mode=args['regex_mode'],
            encoding_options=args['encoding_options']
        )

        threading.Thread.__init__(self)

    def localize(self):
        """Translate strings."""

        self.BENCHMARK_STATUS = _("%01.2f seconds")

    def not_none(self, item, alt=None):
        """Return item if not None, else return the alternate."""

        return item if item is not None else alt

    def update_status(self):
        """Update status."""

        global _COMPLETED
        global _RECORDS
        global _SKIPPED

        with _LOCK:
            _COMPLETED, _SKIPPED, _RECORDS = self.rummage.get_status()
            _RECORDS -= self.no_results

    def done(self):
        """Check if thread is done running."""

        return not self.running

    def payload(self):
        """Execute the rummage command and gather results."""

        global _RESULTS
        global _COMPLETED
        global _RECORDS
        global _ERRORS
        global _SKIPPED
        with _LOCK:
            _RESULTS = []
            _COMPLETED = 0
            _RECORDS = 0
            _SKIPPED = 0
            _ERRORS = []
        for f in self.rummage.find():
            with _LOCK:
                if isinstance(f, rumcore.FileAttrRecord) and f.skipped:
                    self.no_results += 1
                elif f.error is None and (self.file_search or f.match is not None):
                    _RESULTS.append(f)
                else:
                    if isinstance(f, rumcore.FileRecord):
                        self.no_results += 1
                    if f.error is not None:
                        _ERRORS.append(f)
                self.update_benchmark()
            self.update_status()
            wx.WakeUpIdle()

            if _ABORT:
                self.rummage.kill()

    def update_benchmark(self):
        """Update benchmark."""
        self.benchmark = time() - self.start

    def run(self):
        """Start the Rummage thread benchmark the time."""

        global _ABORT
        self.running = True
        self.start = time()
        self.benchmark = 0.0

        try:
            self.payload()
        except Exception:
            error(traceback.format_exc())

        self.update_benchmark()
        runtime = self.BENCHMARK_STATUS % self.benchmark

        self.runtime = runtime
        self.running = False
        self.update_status()
        if _ABORT:
            _ABORT = False


class RummageArgs(object):
    """Rummage argument object."""

    def __init__(self):
        """Default the rummage arguments on instantiation."""

        self.reset()

    def reset(self):
        """Reset rummage arguments to defaults."""

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
        self.follow_links = False
        self.size_compare = None
        self.modified_compare = None
        self.created_compare = None
        self.count_only = False
        self.unicode = False
        self.boolean = False
        self.backup = True
        self.backup_folder = False
        self.replace = None
        self.force_encode = None
        self.backup_location = None
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
        self.extmatch = False
        self.brace_expansion = False
        self.file_case_sensitive = False
        self.full_exclude_path = False
        self.full_file_path = False
        self.globstar = False
        self.matchbase = False
        self.encoding_options = {}


class RummageFrame(gui.RummageFrame):
    """Rummage Frame."""

    def __init__(self, parent, start_path, debug_mode=False):
        """Initialize the Rummage frame object."""

        super(RummageFrame, self).__init__(parent)
        self.maximized = False
        if util.platform() == "windows":
            self.m_settings_panel.SetDoubleBuffered(True)
        self.localize()

        self.SetIcon(
            data.get_image('rummage_large.png').GetIcon()
        )

        self.last_pattern_search = ""
        self.no_pattern = False
        self.client_size = wx.Size(-1, -1)
        self.paylod = {}
        self.error_dlg = None
        self.doc_dlg = None
        self.debounce_search = False
        self.searchin_update = False
        self.replace_plugin_update = False
        self.checking = False
        self.kill = False
        self.thread = None
        self.last_update = 0.0
        last = Settings.get_last_update_check()
        try:
            self.last_update_check = datetime.strptime(last, "%Y-%m-%d %H:%M") if last is not None else last
        except Exception:
            self.last_update_check = None
        self.allow_update = False
        self.checking_updates = False
        self.imported_plugins = {}
        if start_path is None:
            start_path = os.getcwd()

        # Setup debugging
        self.set_keybindings(
            [
                (wx.ACCEL_CMD if util.platform() == "osx" else wx.ACCEL_CTRL, ord('A'), self.on_textctrl_selectall),
                (wx.ACCEL_NORMAL, wx.WXK_RETURN, self.on_enter_key),
                (wx.ACCEL_NORMAL, wx.WXK_ESCAPE, self.on_esc_key)
            ]
        )

        # Update status on when idle
        self.Bind(wx.EVT_IDLE, self.on_idle)
        self.Bind(wx.EVT_SIZE, self.on_resize)
        self.Bind(EVT_POST_RESIZE, self.on_post_resize)

        # Extend the status bar
        custom_statusbar.extend_sb(self.m_statusbar)
        self.m_statusbar.set_status("")

        self.m_options_collapse.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.on_options_collapse)
        self.m_limit_collapse.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.on_limit_collapse)

        self.m_options_collapse.workaround()
        self.m_limit_collapse.workaround()

        # Extend browse button
        pick_button.pick_extend(self.m_searchin_dir_picker, pick_button.PickButton)
        self.m_searchin_dir_picker.pick_init(
            pick_button.PickButton.DIR_TYPE,
            self.DIRECTORY_SELECT,
            pick_change_evt=self.on_dir_changed
        )
        pick_button.pick_extend(self.m_replace_plugin_dir_picker, pick_button.PickButton)
        self.m_replace_plugin_dir_picker.pick_init(
            pick_button.PickButton.FILE_TYPE,
            self.SCRIPT_SELECT,
            default_path=os.path.join(Settings.get_config_folder(), 'plugins'),
            pick_change_evt=self.on_replace_plugin_dir_changed
        )

        # Replace result panel placeholders with new custom panels
        self.m_result_file_list.set_international_time(Settings.get_international_time())
        self.m_result_file_list.set_wait_lock(_LOCK)
        self.m_result_list.set_wait_lock(_LOCK)
        self.m_result_file_list.set_hidden_columns(Settings.get_hide_cols_file())
        self.m_result_list.set_hidden_columns(Settings.get_hide_cols_content())
        self.m_result_file_list.load_list(True)
        self.m_result_list.load_list(True)
        self.m_result_file_list.update_virtual(Settings.get_pos_cols_file())
        self.m_result_list.update_virtual(Settings.get_pos_cols_content())
        self.m_grep_notebook.SetSelection(0)

        self.refresh_localization()

        # Setup the inputs history and replace
        # placeholder objects with actual objects
        self.setup_inputs()

        self.init_search_path(start_path)

        self.refresh_regex_options()
        self.refresh_chain_mode()

        if util.platform() != "linux":
            self.finalize_size()
        self.m_searchfor_textbox.SetFocus()

        # So this is to fix some platform specific issues.
        # We will wait until we are sure we are loaded, then
        # We will fix mac focusing random elements, and we will
        # process and resize the window to fix Linux tab issues.
        # Linux seems to need the resize to get its control tab
        # order right as we are hiding some items, but doing it
        # now won't work, so we delay it.
        self.call_later = wx.CallLater(500, self.on_loaded)
        self.call_later.Start()

    def localize(self):
        """Translate strings."""

        # Combo options
        self.SIZE_ANY = _("any")
        self.SIZE_GT = _("greater than")
        self.SIZE_EQ = _("equal to")
        self.SIZE_LT = _("less than")

        self.TIME_ANY = _("on any")
        self.TIME_GT = _("after")
        self.TIME_EQ = _("on")
        self.TIME_LT = _("before")

        # Search/replace button states
        self.SEARCH_BTN_STOP = _("Stop")
        self.SEARCH_BTN_SEARCH = _("Search")
        self.SEARCH_BTN_ABORT = _("Aborting")
        self.REPLACE_BTN_REPLACE = _("Replace")

        # Picker/Save messages
        self.DIRECTORY_SELECT = _("Select directory to rummage")
        self.SCRIPT_SELECT = _("Select replace script")
        self.EXPORT_TO = _("Export to...")
        self.IMPORT_FROM = _("Import from...")

        # Dialog messages
        self.MSG_REPLACE_WARN = _("Are you sure you want to replace all instances?")
        self.MSG_BACKUPS_DISABLED = _("Backups are currently disabled.")

        # Notifications
        self.NOTIFY_SEARCH_ABORTED = _("Search Aborted")
        self.NOTIFY_SEARCH_COMPLETED = _("Search Completed")
        self.NOTIFY_MATCHES_FOUND = _("\n%d matches found!")

        # ERRORS
        self.ERR_NO_LOG = _("Cannot find log file!")
        self.ERR_EMPTY_SEARCH = _("There is no search to save!")
        self.ERR_HTML_FAILED = _("There was a problem exporting the HTML!  See the log for more info.")
        self.ERR_CSV_FAILED = _("There was a problem exporting the CSV!  See the log for more info.")
        self.ERR_NOTHING_TO_EXPORT = _("There is nothing to export!")
        self.ERR_SETUP = _("There was an error in setup! Please check the log.")
        self.ERR_UPDATE = _("There was an error checking for updates!")
        self.ERR_INVALID_SEARCH_PTH = _("Please enter a valid search path!")
        self.ERR_INVALID_SEARCH = _("Please enter a valid search!")
        self.ERR_EMPTY_CHAIN = _("There are no searches in this this chain!")
        self.ERR_MISSING_SEARCH = _("'%s' is not found in saved searches!")
        self.ERR_INVALID_CHAIN = _("Please enter a valid chain!")
        self.ERR_INVALID_CHAIN_SEARCH = _("Saved search '%s' does not contain a valid search pattern!")
        self.ERR_INVALID_FILE_SEARCH = _("Please enter a valid file pattern!")
        self.ERR_INVALID_EXCLUDE = _("Please enter a valid exlcude directory regex!")
        self.ERR_INVLAID_SIZE = _("Please enter a valid size!")
        self.ERR_INVALID_MDATE = _("Please enter a modified date!")
        self.ERR_INVALID_CDATE = _("Please enter a created date!")
        self.ERR_IMPORT = _("There was an error attempting to read the settings file!")

        # Status
        self.INIT_STATUS = _("Searched: 0 Skipped: 0 Matches: 0")
        self.UPDATE_STATUS = _("Searched: %d Skipped: %d Matches: %d")
        self.FINAL_STATUS = _("Searched: %d Skipped: %d Matches: %d Benchmark: %s")

        # Status bar popup
        self.SB_ERRORS = _("errors")
        self.SB_TOOLTIP_ERR = _("%d errors\nClick to see errors.")

        # Controls
        self.SEARCH_REPLACE = _("Search and Replace")
        self.LIMIT_SEARCH = _("File search options")
        self.SEARCH_IN = _("Search in")
        self.SEARCH_FOR = _("Search for")
        self.SEARCH_CHAIN = _("Search chain")
        self.REPLACE_WITH = _("Replace with")
        self.REPLACE_PLUGIN = _("Replace plugin")
        self.SIZE_IS = _("Size is")
        self.MODIFIED = _("Modified")
        self.CREATED = _("Created")
        self.EXCLUDE = _("Exclude folders")
        self.FILE_MATCH = _("Files which match")
        self.SEARCH_WITH_REGEX = _("Search with regex")
        self.CASE = _("Search case-sensitive")
        self.DOTALL = _("Dot matches newline")
        self.UNICODE = _("Use Unicode properties")
        self.BOOLEAN = _("Boolean match")
        self.COUNT_ONLY = _("Count only")
        self.CREATE_BACKUPS = _("Create backups")
        self.FORCE = _("Force")
        self.USE_CHAIN = _("Use chain search")
        self.USE_PLUGIN = _("Use plugin replace")
        self.BESTMATCH = _("Best fuzzy match")
        self.FUZZY_FIT = _("Improve fuzzy fit")
        self.WORD = _("Unicode word breaks")
        self.REVERSE = _("Search backwards")
        self.POSIX = _("Use POSIX matching")
        self.FORMAT = _("Format style replacements")
        self.CASEFOLD = _("Full case-folding")
        self.SUBFOLDERS = _("Include subfolders")
        self.HIDDEN = _("Include hidden")
        self.SYMLINK = _("Follow symlinks")
        self.INCLUDE_BINARY = _("Include binary files")
        self.USE_REGEX = _("Regex")
        self.TEST_REGEX = _("Test Regex")
        self.SAVE_SEARCH = _("Save Search")
        self.LOAD_SEARCH = _("Load Search")
        self.SEARCH = _("Search")
        self.UP_TO_DATE = _("Current version is %s. Rummage is up to date!")
        self.NOT_UP_TO_DATE = _("There is an update available: %s.")
        self.OPTIONS = _("Text search options")

        # Menu
        self.MENU_EXPORT_RESULTS = _("Export Results")
        self.MENU_EXPORT_SETTINGS = _("Export Settings")
        self.MENU_IMPORT_SETTINGS = _("Import Settings")
        self.MENU_FILE = _("File")
        self.MENU_VIEW = _("View")
        self.MENU_HELP = _("Help")
        self.MENU_PREFERENCES = _("&Preferences")
        self.MENU_EXIT = _("&Exit")
        self.MENU_HTML = _("HTML")
        self.MENU_CSV = _("CSV")
        self.MENU_OPEN_LOG = _("Open Log File")
        self.MENU_ABOUT = _("&About Rummage")
        self.MENU_UPDATE = _("Check for Updates")
        self.MENU_DOCUMENTATION = _("Documentation")
        self.MENU_CHANGELOG = _("Changelog")
        self.MENU_LICENSE = _("License")
        self.MENU_HELP_SUPPORT = _("Help and Support")

        # Combo values
        self.SIZE_LIMIT_I18N = {
            self.SIZE_ANY: "any",
            self.SIZE_GT: "greater than",
            self.SIZE_EQ: "equal to",
            self.SIZE_LT: "less than"
        }

        self.TIME_LIMIT_I18N = {
            self.TIME_ANY: "on any",
            self.TIME_GT: "after",
            self.TIME_EQ: "on",
            self.TIME_LT: "before"
        }

    def get_dialog(self, name):
        """Get dialog."""

        return globals()[name]

    def refresh_localization(self):
        """Localize."""

        self.m_search_button.SetLabel(self.SEARCH_BTN_SEARCH)
        self.m_replace_button.SetLabel(self.REPLACE_BTN_REPLACE)
        self.m_searchin_label.SetLabel(self.SEARCH_IN)
        self.m_searchfor_label.SetLabel(self.SEARCH_FOR)
        self.m_replace_label.SetLabel(self.REPLACE_WITH)
        self.m_size_is_label.SetLabel(self.SIZE_IS)
        self.m_modified_label.SetLabel(self.MODIFIED)
        self.m_created_label.SetLabel(self.CREATED)
        self.m_exclude_label.SetLabel(self.EXCLUDE)
        self.m_filematch_label.SetLabel(self.FILE_MATCH)
        self.m_options_collapse.SetLabel(self.OPTIONS)
        self.m_regex_search_checkbox.SetLabel(self.SEARCH_WITH_REGEX)
        self.m_case_checkbox.SetLabel(self.CASE)
        self.m_dotmatch_checkbox.SetLabel(self.DOTALL)
        self.m_unicode_checkbox.SetLabel(self.UNICODE)
        self.m_force_encode_choice.SetSelection(0)
        self.m_boolean_checkbox.SetLabel(self.BOOLEAN)
        self.m_count_only_checkbox.SetLabel(self.COUNT_ONLY)
        self.m_backup_checkbox.SetLabel(self.CREATE_BACKUPS)
        self.m_force_encode_checkbox.SetLabel(self.FORCE)
        self.m_force_encode_choice.Clear()
        for x in ENCODINGS:
            self.m_force_encode_choice.Append(x)
        self.m_chains_checkbox.SetLabel(self.USE_CHAIN)
        self.m_replace_plugin_checkbox.SetLabel(self.USE_PLUGIN)
        self.m_bestmatch_checkbox.SetLabel(self.BESTMATCH)
        self.m_enhancematch_checkbox.SetLabel(self.FUZZY_FIT)
        self.m_word_checkbox.SetLabel(self.WORD)
        self.m_reverse_checkbox.SetLabel(self.REVERSE)
        self.m_posix_checkbox.SetLabel(self.POSIX)
        self.m_format_replace_checkbox.SetLabel(self.FORMAT)
        self.m_fullcase_checkbox.SetLabel(self.CASEFOLD)
        self.m_limit_collapse.SetLabel(self.LIMIT_SEARCH)
        self.m_subfolder_checkbox.SetLabel(self.SUBFOLDERS)
        self.m_hidden_checkbox.SetLabel(self.HIDDEN)
        self.m_symlinks_checkbox.SetLabel(self.SYMLINK)
        self.m_binary_checkbox.SetLabel(self.INCLUDE_BINARY)
        self.m_dirregex_checkbox.SetLabel(self.USE_REGEX)
        self.m_fileregex_checkbox.SetLabel(self.USE_REGEX)
        self.m_regex_test_button.SetLabel(self.TEST_REGEX)
        self.m_save_search_button.SetLabel(self.SAVE_SEARCH)
        self.m_load_search_button.SetLabel(self.LOAD_SEARCH)
        self.m_grep_notebook.SetPageText(0, self.SEARCH)
        exportid = self.m_menu.FindMenuItem("File", "Export Results")
        self.m_menu.SetLabel(exportid, self.MENU_EXPORT_RESULTS)
        self.m_menu.SetMenuLabel(0, self.MENU_FILE)
        self.m_menu.SetMenuLabel(1, self.MENU_HELP)
        self.m_preferences_menuitem.SetItemLabel(self.MENU_PREFERENCES)
        self.m_quit_menuitem.SetItemLabel(self.MENU_EXIT)
        self.m_export_html_menuitem.SetItemLabel(self.MENU_HTML)
        self.m_export_csv_menuitem.SetItemLabel(self.MENU_CSV)
        self.m_export_settings_menuitem.SetItemLabel(self.MENU_EXPORT_SETTINGS)
        self.m_import_settings_menuitem.SetItemLabel(self.MENU_IMPORT_SETTINGS)
        self.m_log_menuitem.SetItemLabel(self.MENU_OPEN_LOG)
        self.m_about_menuitem.SetItemLabel(self.MENU_ABOUT)
        self.m_update_menuitem.SetItemLabel(self.MENU_UPDATE)
        self.m_documentation_menuitem.SetItemLabel(self.MENU_DOCUMENTATION)
        self.m_changelog_menuitem.SetItemLabel(self.MENU_CHANGELOG)
        self.m_license_menuitem.SetItemLabel(self.MENU_LICENSE)
        self.m_issues_menuitem.SetItemLabel(self.MENU_HELP_SUPPORT)

        self.m_logic_choice.Clear()
        for x in [self.SIZE_ANY, self.SIZE_GT, self.SIZE_EQ, self.SIZE_LT]:
            self.m_logic_choice.Append(x)

        self.m_modified_choice.Clear()
        for x in [self.TIME_ANY, self.TIME_GT, self.TIME_EQ, self.TIME_LT]:
            self.m_modified_choice.Append(x)

        self.m_created_choice.Clear()
        for x in [self.TIME_ANY, self.TIME_GT, self.TIME_EQ, self.TIME_LT]:
            self.m_created_choice.Append(x)

    def set_international_time_output(self, itime):
        """Set international time output."""

        self.m_result_file_list.set_international_time(itime)

    def set_keybindings(self, keybindings=None):
        """
        Method to easily set key bindings.

        Also sets up debug key bindings and events.
        """

        if keybindings is None:
            keybindings = []

        # Add key bindings.
        tbl = []
        bindings = keybindings
        for binding in keybindings:
            keyid = wx.NewId()
            self.Bind(wx.EVT_MENU, binding[2], id=keyid)
            tbl.append((binding[0], binding[1], keyid))

        if len(bindings):
            self.SetAcceleratorTable(wx.AcceleratorTable(tbl))

    def init_search_path(self, start_path):
        """Initialize the search path input."""

        # Initialize search path with passed in path
        if start_path and os.path.exists(start_path):
            self.m_searchin_text.safe_set_value(os.path.abspath(os.path.normpath(start_path)))

    def optimize_size(self, first_time=False, minimize_height=False):
        """Optimally resize window."""

        best = self.m_settings_panel.GetBestSize()
        current = self.m_settings_panel.GetSize()
        offset = best[1] - current[1]
        mainframe = self.GetSize()

        # Get this windows useable display size
        display = wx.Display()
        index = display.GetFromWindow(self)
        if index != wx.NOT_FOUND:
            display = wx.Display(index)
            rect = display.GetClientArea()

        if first_time:
            debug('----Intial screen resize----')
            debug('Screen Index: %d' % index)
            debug('Screen Client Size: %d x %d' % (rect.GetWidth(), rect.GetHeight()))
            width = mainframe[0]
            height = mainframe[1] + offset
            debug('Window Size: %d x %d' % (width, height))
            sz = wx.Size(width, height)
            self.SetMinSize(sz)
            self.SetSize(sz)
        else:
            increase_width = False
            increase_height = False

            min_size = self.GetMinSize()
            min_width, min_height = min_size[0], mainframe[1] + offset
            width, height = mainframe[0], mainframe[1]

            if min_width > width:
                increase_width = True
                width = min_width

            if min_height > height:
                increase_height = True
                height = min_height

            if increase_width or increase_height:
                self.SetMinSize(wx.Size(-1, -1))
                self.SetSize(wx.Size(width, height))

            self.SetMinSize(wx.Size(min_width, min_height))

            if minimize_height:
                self.SetSize(wx.Size(width, min_height))

        self.Refresh()

    def setup_inputs(self):
        """Setup and configure input objects."""

        self.m_regex_search_checkbox.SetValue(Settings.get_search_setting("regex_toggle", True))
        self.m_fileregex_checkbox.SetValue(Settings.get_search_setting("regex_file_toggle", False))
        self.m_dirregex_checkbox.SetValue(Settings.get_search_setting("regex_dir_toggle", False))

        self.m_logic_choice.SetStringSelection(
            eng_to_i18n(
                Settings.get_search_setting("size_compare_string", "any"),
                self.SIZE_LIMIT_I18N
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
        encode_val = util.normalize_encoding_name(Settings.get_search_setting("force_encode", "ASCII"))
        if encode_val is None:
            encode_val == "ASCII"
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
        self.m_symlinks_checkbox.SetValue(Settings.get_search_setting("symlink_toggle", False))
        self.m_subfolder_checkbox.SetValue(Settings.get_search_setting("recursive_toggle", True))
        self.m_binary_checkbox.SetValue(Settings.get_search_setting("binary_toggle", False))
        self.m_chains_checkbox.SetValue(Settings.get_search_setting("chain_toggle", False))
        self.m_replace_plugin_checkbox.SetValue(Settings.get_search_setting("replace_plugin_toggle", False))

        option_collapse = Settings.get_search_setting('option_collapse', False)
        self.m_options_collapse.Collapse(option_collapse)
        limit_collapse = Settings.get_search_setting('limit_collapse', False)
        self.m_limit_collapse.Collapse(limit_collapse)

        self.m_modified_choice.SetStringSelection(
            eng_to_i18n(
                Settings.get_search_setting("modified_compare_string", "on any"),
                self.TIME_LIMIT_I18N
            )
        )
        self.m_created_choice.SetStringSelection(
            eng_to_i18n(
                Settings.get_search_setting("created_compare_string", "on any"),
                self.TIME_LIMIT_I18N
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
            self.m_replace_label.SetLabel(self.REPLACE_PLUGIN)
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

        if setup and setup not in chains:
            setup = chains[0] if chains else ""

        self.m_searchfor_textbox.update_choices(chains)
        self.m_searchfor_textbox.SetValue(setup)

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
            if mode == rumcore.BRE_MODE:
                self.m_format_replace_checkbox.Show()
            else:
                self.m_format_replace_checkbox.Hide()
            self.m_fullcase_checkbox.Hide()
        self.m_options_panel.GetSizer().Layout()
        self.m_options_collapse.GetPane().GetSizer().Layout()
        self.m_settings_panel.GetSizer().Layout()

    def on_options_collapse(self, event):
        """Handle on collapse for options panel."""

        self.m_options_panel.GetSizer().Layout()
        self.m_options_collapse.GetPane().GetSizer().Layout()
        self.m_settings_panel.GetSizer().Layout()
        Settings.set_toggles([("option_collapse", self.m_options_collapse.IsCollapsed())])
        minimize = not self.IsMaximized()
        self.optimize_size(minimize_height=minimize)

    def on_limit_collapse(self, event):
        """Handle on collapse for limit panel."""

        self.m_limit_panel.GetSizer().Layout()
        self.m_limit_collapse.GetPane().GetSizer().Layout()
        self.m_settings_panel.GetSizer().Layout()
        Settings.set_toggles([("limit_collapse", self.m_limit_collapse.IsCollapsed())])
        minimize = not self.IsMaximized()
        self.optimize_size(minimize_height=minimize)

    def refresh_chain_mode(self):
        """Refresh chain mode."""

        if self.m_chains_checkbox.GetValue():
            self.last_pattern_search = self.m_searchfor_textbox.Value
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

            self.m_searchfor_label.SetLabel(self.SEARCH_CHAIN)
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

            self.m_searchfor_label.SetLabel(self.SEARCH_FOR)
            self.m_replace_label.Enable(True)
            self.m_replace_textbox.Enable(True)
            self.m_replace_plugin_dir_picker.Enable(True)

            self.m_save_search_button.Enable(True)
            update_autocomplete(
                self.m_searchfor_textbox,
                "regex_search" if self.m_regex_search_checkbox.GetValue() else "literal_search"
            )
            self.m_searchfor_textbox.SetValue(self.last_pattern_search)
            return False

    def abort_search(self, is_replacing):
        """Abort search."""

        global _ABORT
        aborted = False
        if self.thread is not None and not self.kill:
            if is_replacing:
                self.m_replace_button.SetLabel(self.SEARCH_BTN_ABORT)
            else:
                self.m_search_button.SetLabel(self.SEARCH_BTN_ABORT)
            _ABORT = True
            self.kill = True
            aborted = True
        return aborted

    def start_search(self, replace=False):
        """Initiate search or stop search depending on search state."""

        global _ABORT
        if self.debounce_search:
            return
        self.debounce_search = True

        is_replacing = self.m_replace_button.GetLabel() in [self.SEARCH_BTN_STOP, self.SEARCH_BTN_ABORT]
        is_searching = self.m_search_button.GetLabel() in [self.SEARCH_BTN_STOP, self.SEARCH_BTN_ABORT]

        if is_searching or is_replacing:
            # Handle a search or replace request when a search or replace is already running

            if not self.abort_search(is_replacing):
                self.debounce_search = False
        else:
            # Handle a search or a search & replace request

            if replace:
                message = [self.MSG_REPLACE_WARN]
                if not self.m_backup_checkbox.GetValue():
                    message.append(self.MSG_BACKUPS_DISABLED)

                if not yesno(' '.join(message)):
                    self.debounce_search = False
                    return

            is_chain = self.m_chains_checkbox.GetValue()
            chain = self.m_searchfor_textbox.Value if is_chain else None

            if is_chain and (not chain.strip() or chain not in Settings.get_chains()):
                errormsg(self.ERR_INVALID_CHAIN)
            elif not self.validate_search_inputs(replace=replace, chain=chain):
                self.do_search(replace=replace, chain=chain is not None)
            self.debounce_search = False

    def do_search(self, replace=False, chain=None):
        """Start the search."""

        self.thread = None

        # Reset status
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
            errormsg(self.ERR_SETUP)
            return

        # Change button to stop search
        if replace:
            self.m_replace_button.SetLabel(self.SEARCH_BTN_STOP)
            self.m_search_button.Enable(False)
        else:
            self.m_search_button.SetLabel(self.SEARCH_BTN_STOP)
            self.m_replace_button.Enable(False)

        # Initialize search status
        self.m_statusbar.set_status(self.INIT_STATUS)

        # Setup search thread
        self.thread = RummageThread(self.payload)
        self.thread.setDaemon(True)

        # Reset result tables
        self.last_update = 0.0
        self.m_grep_notebook.SetSelection(1)
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

        if regex_mode in rumcore.FORMAT_MODES:
            if "F" in string:
                flags |= rumcore.FORMATREPLACE

        return flags

    def get_flags(self, args):
        """Determine `rumcore` flags from `RummageArgs`."""

        flags = rumcore.MULTILINE | rumcore.TRUNCATE_LINES

        if args.regex_mode in rumcore.REGEX_MODES:
            if args.regex_version == 1:
                flags |= rumcore.VERSION1
            else:
                flags |= rumcore.VERSION0
                if args.fullcase:
                    flags |= rumcore.FULLCASE

        if args.extmatch:
            flags |= rumcore.EXTMATCH

        if args.brace_expansion:
            flags |= rumcore.BRACE

        if args.file_case_sensitive:
            flags |= rumcore.FILECASE

        if args.full_exclude_path:
            flags |= rumcore.DIRPATHNAME

        if args.full_file_path:
            flags |= rumcore.FILEPATHNAME

        if args.globstar:
            flags |= rumcore.GLOBSTAR

        if args.matchbase:
            flags |= rumcore.MATCHBASE

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

        if args.follow_links:
            flags |= rumcore.FOLLOW_LINKS

        if args.process_binary:
            flags |= rumcore.PROCESS_BINARY

        if args.count_only:
            flags |= rumcore.COUNT_ONLY

        if args.boolean:
            flags |= rumcore.BOOLEAN

        if args.backup:
            flags |= rumcore.BACKUP

        if args.backup_folder:
            flags |= rumcore.BACKUP_FOLDER

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

        if args.regex_mode in rumcore.FORMAT_MODES:
            if args.formatreplace:
                flags |= rumcore.FORMATREPLACE

        return flags

    def set_chain_arguments(self, chain, replace, mode):
        """Set the search arguments."""

        search_chain = rumcore.Search(replace)
        searches = Settings.get_search()
        for search_name in Settings.get_chains()[chain]:
            search_obj = searches[search_name]
            if search_obj['is_function'] and replace:
                replace_obj = self.import_plugin(search_obj['replace'])
            elif replace:
                replace_obj = search_obj['replace']
            else:
                replace_obj = None

            flags = self.chain_flags(search_obj['flags'], search_obj['is_regex'])
            is_literal = (flags & rumcore.LITERAL)

            if replace_obj is not None:
                if mode == rumcore.REGEX_MODE and (flags & rumcore.FORMATREPLACE) and not is_literal:
                    replace_obj = util.preprocess_replace(replace_obj, True)
                elif mode == rumcore.RE_MODE and not is_literal:
                    replace_obj = util.preprocess_replace(replace_obj)

            search_chain.add(
                search_obj['search'],
                replace_obj,
                flags
            )

        debug(search_chain)

        return search_chain

    def import_plugin(self, script):
        """Import replace plugin."""

        import imp

        if script not in self.imported_plugins:
            module = imp.new_module(os.path.splitext(os.path.basename(script))[0])
            module.__dict__['__file__'] = script
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
            if args.regex_version == 0:
                args.fullcase = self.m_fullcase_checkbox.GetValue()
        if args.regex_mode in rumcore.FORMAT_MODES:
            args.formatreplace = self.m_format_replace_checkbox.GetValue()
        args.boolean = self.m_boolean_checkbox.GetValue()
        args.backup = self.m_backup_checkbox.GetValue()
        args.backup_folder = bool(Settings.get_backup_type())
        args.force_encode = None
        if self.m_force_encode_checkbox.GetValue():
            args.force_encode = self.m_force_encode_choice.GetStringSelection()
        args.backup_location = Settings.get_backup_folder() if Settings.get_backup_type() else Settings.get_backup_ext()
        args.recursive = self.m_subfolder_checkbox.GetValue()
        args.pattern = self.m_searchfor_textbox.Value
        args.replace = self.m_replace_textbox.Value if replace else None
        args.encoding_options = Settings.get_encoding_options()

        # Limit Options
        if os.path.isdir(args.target):
            args.process_binary = self.m_binary_checkbox.GetValue()
            args.show_hidden = self.m_hidden_checkbox.GetValue()
            args.follow_links = self.m_symlinks_checkbox.GetValue()
            args.extmatch = bool(Settings.get_extmatch())
            args.brace_expansion = bool(Settings.get_brace_expansion())
            args.file_case_sensitive = bool(Settings.get_file_case_sensitive())
            args.full_exclude_path = bool(Settings.get_full_exclude_path())
            args.full_file_path = bool(Settings.get_full_file_path())
            args.globstar = bool(Settings.get_globstar())
            args.matchbase = bool(Settings.get_matchbase())

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
            search_chain = self.set_chain_arguments(args.pattern, replace, args.regex_mode)
        else:
            search_chain = rumcore.Search(args.replace is not None)
            if not self.no_pattern:
                if self.m_replace_plugin_checkbox.GetValue() and replace:
                    repl_obj = self.import_plugin(args.replace)
                    search_chain.add(args.pattern, repl_obj, flags & rumcore.SEARCH_MASK)
                else:
                    replace_pattern = args.replace
                    if replace_pattern is not None:
                        if args.regex_mode == rumcore.REGEX_MODE and (flags & rumcore.FORMATREPLACE) and args.regexp:
                            replace_pattern = util.preprocess_replace(args.replace, True)
                        elif args.regex_mode == rumcore.RE_MODE and args.regexp:
                            replace_pattern = util.preprocess_replace(args.replace)
                    search_chain.add(
                        args.pattern,
                        replace_pattern,
                        flags & rumcore.SEARCH_MASK
                    )

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
            'backup_location': args.backup_location,
            'regex_mode': args.regex_mode,
            'encoding_options': args.encoding_options
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
            ("symlink_toggle", args.follow_links),
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
            ('replace_plugin_toggle', self.m_replace_plugin_checkbox.GetValue()),
        ]

        if Settings.get_regex_version() == 0:
            toggles.append(("fullcase_toggle", args.fullcase))

        eng_size = i18n_to_eng(self.m_logic_choice.GetStringSelection(), self.SIZE_LIMIT_I18N)
        eng_mod = i18n_to_eng(self.m_modified_choice.GetStringSelection(), self.TIME_LIMIT_I18N)
        eng_cre = i18n_to_eng(self.m_created_choice.GetStringSelection(), self.TIME_LIMIT_I18N)
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

    def check_progress(self):
        """Check if updates to the result lists can be done."""

        if not self.checking and self.allow_update:
            self.checking = True
            is_complete = self.thread.done()
            debug("Processing current results")
            results = []
            with _LOCK:
                completed = _COMPLETED
                records = _RECORDS
                skipped = _SKIPPED
                count = self.count
                if records > count:
                    results = _RESULTS[0:records - count]
                    del _RESULTS[0:records - count]
            if results or not is_complete:
                count = self.update_table(count, *results)
                if (self.thread.benchmark - self.last_update) > 1.0:
                    self.m_result_file_list.load_list()
                    self.m_result_list.load_list()
                    # self.m_result_file_list.Refresh()
                    # self.m_result_list.Refresh()
                    self.thread.update_benchmark()
                    self.last_update = self.thread.benchmark

                    self.m_statusbar.set_status(
                        self.UPDATE_STATUS % (
                            completed,
                            skipped,
                            count
                        )
                    )

            self.count = count

            # Run is finished or has been terminated
            if is_complete:
                kill = self.kill
                benchmark = self.thread.runtime
                self.m_search_button.SetLabel(self.SEARCH_BTN_SEARCH)
                self.m_replace_button.SetLabel(self.REPLACE_BTN_REPLACE)
                self.m_search_button.Enable(True)
                self.m_replace_button.Enable(True)
                self.clear_plugins()
                if self.kill:
                    self.kill = False
                    global _ABORT
                    if _ABORT:
                        _ABORT = False
                with _LOCK:
                    errors = _ERRORS[:]
                    del _ERRORS[:]
                if errors:
                    self.error_dlg = SearchErrorDialog(self, errors)
                    self.m_statusbar.set_icon(
                        self.SB_ERRORS,
                        data.get_bitmap('error.png'),
                        msg=self.SB_TOOLTIP_ERR % len(errors),
                        click_left=self.on_error_click
                    )
                self.m_result_file_list.load_list(True)
                self.m_result_list.load_list(True)
                self.debounce_search = False
                self.allow_update = False
                self.thread = None

                self.m_statusbar.set_status(
                    self.FINAL_STATUS % (
                        completed,
                        skipped,
                        count,
                        benchmark
                    )
                )

                if Settings.get_notify():
                    message_type = 'error' if kill else 'info'
                    getattr(notify, message_type)(
                        (self.NOTIFY_SEARCH_ABORTED if kill else self.NOTIFY_SEARCH_COMPLETED),
                        self.NOTIFY_MATCHES_FOUND % count,
                        sound=Settings.get_alert()
                    )
                elif Settings.get_alert():
                    notify.play_alert()

            self.checking = False

    def update_table(self, count, *results):
        """Update the result lists with current search results."""

        for f in results:
            self.m_result_file_list.set_match(f, self.no_pattern)
            if (self.is_count_only or self.is_boolean or self.payload['chain'].is_replace() or self.no_pattern):
                count += 1
                continue

            self.m_result_list.set_match(f)
            count += 1

        return count

    def validate_search_inputs(self, replace=False, chain=None):
        """Validate the search inputs."""

        debug("validate")
        fail = False
        msg = ""

        if not fail and not os.path.exists(self.m_searchin_text.GetValue()):
            msg = self.ERR_INVALID_SEARCH_PTH
            fail = True

        if chain is None:
            if not fail and self.m_regex_search_checkbox.GetValue():
                if (self.m_searchfor_textbox.GetValue() == "" and replace) or self.validate_search_regex():
                    msg = self.ERR_INVALID_SEARCH
                    fail = True
            elif not fail and self.m_searchfor_textbox.GetValue() == "" and replace:
                msg = self.ERR_INVALID_SEARCH
                fail = True
        else:
            chain_searches = Settings.get_chains().get(chain, {})
            if not chain_searches:
                msg = self.ERR_EMPTY_CHAIN
                fail = True
            else:
                searches = Settings.get_search()
                for search in chain_searches:
                    s = searches.get(search)
                    if s is None:
                        msg = self.ERR_MISSING_SEARCH % search
                        fail = True
                        break
                    if self.validate_chain_regex(s['search'], self.chain_flags(s['flags'], s['is_regex'])):
                        msg = self.ERR_INVALID_CHAIN_SEARCH % search
                        fail = True
                        break

        if not fail and not os.path.isfile(self.m_searchin_text.GetValue()):
            if not fail and self.m_fileregex_checkbox.GetValue():
                if self.validate_regex(self.m_filematch_textbox.Value):
                    msg = self.ERR_INVALID_FILE_SEARCH
                    fail = True
            if not fail and self.m_dirregex_checkbox.GetValue():
                if self.validate_regex(self.m_exclude_textbox.Value):
                    msg = self.ERR_INVALID_EXCLUDE
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
                msg = self.ERR_INVLAID_SIZE
                fail = True
            if not fail:
                try:
                    self.m_modified_date_picker.GetValue().Format("%m/%d/%Y")
                except Exception:
                    msg = self.ERR_INVALID_MDATE
                    fail = True
            if not fail:
                try:
                    self.m_created_date_picker.GetValue().Format("%m/%d/%Y")
                except Exception:
                    msg = self.ERR_INVALID_CDATE
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

        return self.validate_regex(pattern, flags)

    def validate_regex(self, pattern, flags=0):
        """Validate regular expression compiling."""

        try:
            mode = Settings.get_regex_mode()
            if mode == rumcore.BREGEX_MODE:
                if flags == 0:
                    flags = bregex.ASCII
                bregex.compile(pattern, flags)
            elif mode == rumcore.REGEX_MODE:
                import regex
                if flags == 0:
                    flags = regex.ASCII
                regex.compile(pattern, flags)
            elif mode == rumcore.BRE_MODE:
                bre.compile(pattern, flags)
            else:
                re.compile(pattern, flags)
            return False
        except Exception:
            debug('Pattern: %s' % pattern)
            debug('Flags: %s' % hex(flags))
            debug(traceback.format_exc())
            return True

    def finalize_size(self):
        """Finalize size."""

        self.Fit()
        self.m_settings_panel.Fit()
        self.m_settings_panel.GetSizer().Layout()
        self.m_main_panel.Fit()
        self.m_main_panel.GetSizer().Layout()
        self.optimize_size(first_time=True)

    def on_loaded(self):
        """
        Stupid workarounds on load.

        Focus after loaded (stupid macOS workaround) and select the appropriate entry.
        Resize window after we are sure everything is loaded (stupid Linux workaround) to fix tab order stuff.
        """

        self.call_later.Stop()

        if util.platform() == "osx":
            self.m_searchfor_textbox.SetFocus()

        self.Refresh()

        if util.platform() == "linux":
            self.finalize_size()

        if tuple(Settings.get_current_version()) < __meta__.__version_info__:
            Settings.set_current_version(__meta__.__version_info__)
            dlg = html_dialog.HTMLDialog(self, 'changelog.html', self.MENU_CHANGELOG)
            dlg.ShowModal()
            dlg.Destroy()

    def on_notebook_changed(self, event):
        """
        Handle when notebook tab changes.

        On Linux, GTK seems to force the first tab start every time
        the notebook page is changed.  Here we will detect the notebook
        page change for the search tab, and force the more sensible "search for"
        to be selected.
        """

        if util.platform() == "linux":
            new = event.GetSelection()
            old = event.GetOldSelection()
            if new != old and new == 0:
                self.call_later = wx.CallLater(100, self.m_searchfor_textbox.SetFocus)
                self.call_later.Start()
        event.Skip()

    def on_resize(self, event):
        """
        On resize check if the client size changed between.

        If the client size changed during resize (or sometime before)
        it might be because we entered full screen mode.  Maybe we
        adjusted the windows minimum size during full screen and it is wrong.
        So check if client size changed, and if so, run optimize size
        to be safe.
        """

        event.Skip()
        display = wx.Display()
        index = display.GetFromWindow(self)
        if index != wx.NOT_FOUND:
            display = wx.Display(index)
            rect = display.GetClientArea()
            client_size = wx.Size(rect.GetWidth(), rect.GetHeight())

            if (
                client_size[0] != self.client_size[0] or client_size[1] != self.client_size[1] or
                (self.maximized and not self.IsMaximized())
            ):
                self.client_size = client_size
                evt = PostResizeEvent()
                self.QueueEvent(evt)
        if self.IsMaximized():
            self.maximized = True
            debug('maximized')

    def on_post_resize(self, event):
        """Handle after resize event."""

        self.optimize_size()

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

    def on_esc_key(self, event):
        """Abort on escape."""

        if self.thread is not None and not self.kill:
            self.abort_search(self.m_replace_button.GetLabel() in (self.SEARCH_BTN_STOP, self.SEARCH_BTN_ABORT))

        event.Skip()

    def on_textctrl_selectall(self, event):
        """Select all in the `TextCtrl` and `AutoCompleteCombo` objects."""

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

    def on_preferences(self, event):
        """Show settings dialog, and update history of `AutoCompleteCombo` if the history was cleared."""

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
        self.optimize_size()

    def on_chain_toggle(self, event):
        """Handle chain toggle event."""

        self.refresh_chain_mode()
        self.m_settings_panel.GetSizer().Layout()

    def on_plugin_function_toggle(self, event):
        """Handle plugin function toggle."""

        if self.m_replace_plugin_checkbox.GetValue():
            self.m_replace_label.SetLabel(self.REPLACE_PLUGIN)
            self.m_replace_plugin_dir_picker.Show()
            update_autocomplete(
                self.m_replace_textbox,
                "replace_plugin"
            )
        else:
            self.m_replace_label.SetLabel(self.REPLACE_WITH)
            self.m_replace_plugin_dir_picker.Hide()
            update_autocomplete(
                self.m_replace_textbox,
                "regex_replace" if self.m_regex_search_checkbox.GetValue() else "literal_replace"
            )
        self.m_settings_panel.GetSizer().Layout()

    def on_dir_changed(self, event):
        """Event for when the directory changes in the `DirPickButton`."""

        if not self.searchin_update:
            pth = event.target
            if pth is not None and os.path.exists(pth):
                self.searchin_update = True
                self.m_searchin_text.safe_set_value(pth)
                self.searchin_update = False
        event.Skip()

    def on_replace_plugin_dir_changed(self, event):
        """Handle replace plugin directory change."""

        if not self.replace_plugin_update:
            pth = event.target
            if pth is not None and os.path.exists(pth):
                self.replace_plugin_update = True
                self.m_replace_textbox.safe_set_value(pth)
                self.replace_plugin_update = False
        event.Skip()

    def on_searchin_changed(self):
        """Callback for when a directory changes via the `m_searchin_text` control."""

        self.SetTitle(self.m_searchin_text.GetValue())

    def on_save_search(self, event):
        """Open a dialog to save a search for later use."""

        search = self.m_searchfor_textbox.GetValue()
        if search == "":
            errormsg(self.ERR_EMPTY_SEARCH)
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

        if not self.checking_updates and not self.allow_update:
            self.checking_updates = True
            check = False
            current = datetime.now()
            if self.last_update_check is None:
                check = True
            else:
                diff = current - self.last_update_check
                if diff.days >= 1:
                    check = True
            if check:
                check_updates, prerelease = Settings.get_update_options()
                if check_updates:
                    self.update_request(prerelease, True)
                else:
                    Settings.set_last_update_check(current.strftime("%Y-%m-%d %H:%M"))
                    self.last_update_check = current
            self.checking_updates = False

        # Update progress
        self.check_progress()
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

    def on_close(self, event):
        """Ensure thread is stopped, notifications are destroyed."""

        global _ABORT

        if self.thread is not None:
            _ABORT = True
        if self.doc_dlg is not None:
            self.doc_dlg.Destroy()
            self.doc_dlg = None
        if self.error_dlg is not None:
            self.error_dlg.Destroy()
            self.error_dlg = None
        self.m_result_list.destroy()
        self.m_result_file_list.destroy()
        self.m_statusbar.tear_down()
        notify.destroy_notifications()
        event.Skip()

    def on_test_regex(self, event):
        """Show regex test dialog."""

        tester = RegexTestDialog(self)
        tester.ShowModal()
        tester.Destroy()

    def on_export_html(self, event):
        """Export to HTML."""

        if not self.m_result_list.complete or not self.m_result_list.complete:
            return

        if (
            len(self.m_result_file_list.itemDataMap) == 0 and
            len(self.m_result_list.itemDataMap) == 0
        ):
            errormsg(self.ERR_NOTHING_TO_EXPORT)
            return
        html_file = filepickermsg(self.EXPORT_TO, wildcard="*.html", save=True)
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
            errormsg(self.ERR_HTML_FAILED)

    def on_export_csv(self, event):
        """Export to CSV."""

        if not self.m_result_list.complete or not self.m_result_list.complete:
            return

        if (
            len(self.m_result_file_list.itemDataMap) == 0 and
            len(self.m_result_list.itemDataMap) == 0
        ):
            errormsg(self.ERR_NOTHING_TO_EXPORT)
            return
        csv_file = filepickermsg(self.EXPORT_TO, wildcard="*.csv", save=True)
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
            errormsg(self.ERR_CSV_FAILED)

    def on_export_settings(self, event):
        """Export settings."""

        exporter = ExportSettingsDialog(self)
        exporter.ShowModal()
        exporter.Destroy()

    def on_import_settings(self, event):
        """Import settings."""

        filename = filepickermsg(self.IMPORT_FROM, wildcard="(*.json;*.settings)|*.json;*.settings", save=False)
        if filename is None:
            return

        obj = util.read_json(filename)
        if obj is None:
            errormsg(self.ERR_IMPORT)
            return

        importer = ImportSettingsDialog(self, obj)
        importer.ShowModal()
        importer.Destroy()

    def on_show_log_file(self, event):
        """Show user files in editor."""

        try:
            logfile = get_log_file()
        except Exception:
            logfile = None

        if logfile is None or not os.path.exists(logfile):
            error(traceback.format_exc())
            errormsg(self.ERR_NO_LOG)
        else:
            fileops.open_editor(logfile, 1, 1)

    def update_request(self, prerelease, hide_no_update=False):
        """Perform update request."""

        current = datetime.now()
        failed = False
        Settings.set_last_update_check(current.strftime("%Y-%m-%d %H:%M"))
        self.last_update_check = current

        try:
            new_ver = updates.check_update(pre=prerelease)
        except Exception:
            error(traceback.format_exc())
            new_ver = None
            failed = True

        if new_ver is None and not hide_no_update:
            if failed:
                errormsg(self.ERR_UPDATE)
            else:
                infomsg(self.UP_TO_DATE % __meta__.__version__)
        elif new_ver is not None:
            infomsg(self.NOT_UP_TO_DATE % new_ver)

    def on_check_update(self, event):
        """Check for update."""

        self.checking_updates = True
        self.update_request(Settings.get_prerelease())
        self.check_updates = False

    def on_documentation(self, event):
        """Open documentation site."""

        if self.doc_dlg is None:
            self.doc_dlg = html_dialog.HTMLDialog(None, 'sitemap.html', self.MENU_DOCUMENTATION)
            self.doc_dlg.Show()
        else:
            self.doc_dlg.load('sitemap.html', self.MENU_DOCUMENTATION)
            self.doc_dlg.Show()

    def on_changelog(self, event):
        """Open documentation site."""

        dlg = html_dialog.HTMLDialog(self, 'changelog.html', self.MENU_CHANGELOG)
        dlg.ShowModal()
        dlg.Destroy()

    def on_license(self, event):
        """Open documentation site."""

        dlg = html_dialog.HTMLDialog(self, 'license.html', self.MENU_CHANGELOG)
        dlg.ShowModal()
        dlg.Destroy()

    def on_support(self, event):
        """Open support information dialog."""

        dlg = SupportInfoDialog(self)
        dlg.ShowModal()
        dlg.Destroy()

    def on_issues(self, event):
        """Open issues site."""

        webbrowser.open_new_tab(__meta__.__help__)

    def on_about(self, event):
        """Show about dialog."""

        title = _("About")
        version = _("Version: %s %s")
        developers = _("Developer(s)")

        md = (
            '<style>\n'
            '.markdown {text-align: center;}\n'
            'img {display: inline; padding: 0; margin: 0; height: 64px; width: 64px; vertical-align: bottom;}\n'
            '.markdown h2 {font-size: 48px;}\n'
            '</style>\n\n'
            '## ![Logo](images/rummage.png) Rummage\n\n'
            '%s\n\n'
            '### %s\n\n'
            '%s\n'
        ) % (
            version % (__meta__.__version__, __meta__.__status__),
            developers,
            "\n".join(["%s - %s  " % (m[0], m[1]) for m in __meta__.__maintainers__])
        )

        dlg = html_dialog.HTMLDialog(
            self, md, title, content_type=html_dialog.webview.MARKDOWN_STRING, min_width=400, min_height=350
        )
        dlg.ShowModal()
        dlg.Destroy()

    def on_exit(self, event):
        """Close dialog."""

        self.Close()
