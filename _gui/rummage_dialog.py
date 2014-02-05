"""
Rummage Dialog

Licensed under MIT
Copyright (c) 2011 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import re
import wx
import sys
import threading
import traceback
import webbrowser
from time import time
from os.path import abspath, exists, basename, dirname, normpath, isdir, isfile, expanduser
import wx.lib.masked as masked
import wx.lib.newevent
import version

import _lib.pygrep as pygrep
from _lib.epoch_timestamp import local_time_to_epoch_timestamp
import _lib.notify as notify
from _lib.localization import get as _

import _gui.gui as gui
import _gui.export_html as export_html
import _gui.export_csv as export_csv
from _gui.settings import Settings, _PLATFORM
from _gui.generic_dialogs import *
from _gui.custom_app import DebugFrameExtender
from _gui.custom_app import debug, error
from _gui.custom_statusbar import extend_sb, extend
from _gui.regex_test_dialog import RegexTestDialog
from _gui.autocomplete_combo import AutoCompleteCombo
from _gui.load_search_dialog import LoadSearchDialog
from _gui.save_search_dialog import SaveSearchDialog
from _gui.settings_dialog import SettingsDialog
from _gui.about_dialog import AboutDialog
from _gui.result_panels import FileResultPanel, ResultFileList, ResultContentList
from _gui.messages import dirpickermsg, filepickermsg
from _gui.messages import Error as error_icon

from _icons.rum_ico import rum_64

DirChangeEvent, EVT_DIR_CHANGE = wx.lib.newevent.NewEvent()


_LOCK = threading.Lock()
_RUNNING = False
_RESULTS = []
_COMPLETED = 0
_TOTAL = 0
_RECORDS = 0
_ERRORS = []
_ABORT = False
_RUNTIME = None

SIZE_ANY = _("any")
SIZE_GT = _("greater than")
SIZE_EQ = _("equal to")
SIZE_LT = _("less than")
TIME_ANY = _("on any")
TIME_GT = _("after")
TIME_EQ = _("on")
TIME_LT = _("before")


LIMIT_COMPARE = {
    0: "any",
    1: "gt",
    2: "eq",
    3: "lt"
}

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

SEARCH_BTN_STOP = _("Stop")
SEARCH_BTN_SEARCH = _("Search")
SEARCH_BTN_ABORT = _("Aborting")


def eng_to_i18n(string, map):
    """
    Convert english to i18n
    """

    i18n = None
    for k, v in map.items():
        if v == string:
            i18n = k
            break
    return i18n


def i18n_to_eng(string, map):
    """
    Convert i18n to english
    """

    return map.get(string, None)


def get_flags(args):
    """
    Determine pygrep flags from GrepArgs
    """

    flags = 0

    if args.regexfilepattern is not None:
        flags |= pygrep.FILE_REGEX_MATCH

    if not args.regexp:
        flags |= pygrep.LITERAL
    elif args.dotall:
        flags |= pygrep.DOTALL

    if args.ignore_case:
        flags |= pygrep.IGNORECASE

    if args.recursive:
        flags |= pygrep.RECURSIVE

    if args.regexdirpattern:
        flags |= pygrep.DIR_REGEX_MATCH

    return flags


def not_none(item, alt=None):
    """
    Return item if not None, else return the alternate
    """

    return item if item is not None else alt


def replace_with_genericdatepicker(obj, key):
    """
    Replace object with a GenericDatePickerCtrl
    """

    d = Settings.get_search_setting(key, None)
    dpc = wx.GenericDatePickerCtrl(
        obj.GetParent(), style=wx.TAB_TRAVERSAL | wx.DP_DROPDOWN | wx.DP_SHOWCENTURY | wx.DP_ALLOWNONE
    )
    if d is None:
        day = wx.DateTime()
        day.SetToCurrent()
        dpc.SetValue(day)
    else:
        day = wx.DateTime()
        saved_day = d.split("/")
        day.Set(int(saved_day[1]), int(saved_day[0]) - 1, int(saved_day[2]))
        dpc.SetValue(day)
    sz = obj.GetContainingSizer()
    sz.Replace(obj, dpc)
    obj.Destroy()
    return dpc


def replace_with_timepicker(obj, spin, key):
    """
    Replace object with TimeCtrl object
    """

    t = Settings.get_search_setting(key, wx.DateTime.Now().Format("%H:%M:%S"))
    time_picker = masked.TimeCtrl(
        obj.GetParent(), value=t, style=wx.TE_PROCESS_TAB, spinButton=spin, oob_color="white", fmt24hr=True
    )
    sz = obj.GetContainingSizer()
    sz.Replace(obj, time_picker)
    obj.Destroy()
    return time_picker


def replace_with_autocomplete(obj, key, load_last=False, changed_callback=None, default=[]):
    """
    Replace object with AutoCompleteCombo object
    """

    choices = Settings.get_search_setting(key, default)
    if choices == [] and choices != default:
        choices = default
    auto_complete = AutoCompleteCombo(obj.GetParent(), choices, load_last, changed_callback)
    sz = obj.GetContainingSizer()
    sz.Replace(obj, auto_complete)
    obj.Destroy()
    return auto_complete


def update_autocomplete(obj, key, load_last=False, default=[]):
    """
    Convienance function for updating the AutoCompleteCombo choices
    """

    choices = Settings.get_search_setting(key, default)
    if choices == [] and choices != default:
        choices = default
    obj.update_choices(choices, load_last)


def threaded_grep(
    target, pattern, file_pattern, folder_exclude,
    flags, show_hidden, all_utf8, size, modified,
    created, text, count_only, boolean
):
    """
    Threaded pygrep launcher to search desired files
    """

    global _RUNNING
    global _RUNTIME
    with _LOCK:
        _RUNTIME = ""
        _RUNNING = True
    start = time()
    try:
        grep = GrepThread(
            pygrep.Grep(
                target=target,
                pattern=pattern,
                file_pattern=file_pattern,
                folder_exclude=folder_exclude,
                flags=flags,
                show_hidden=show_hidden,
                all_utf8=all_utf8,
                modified=modified,
                created=created,
                size=size,
                text=text,
                truncate_lines=True,
                count_only=count_only,
                boolean=boolean
            )
        )
        grep.run()
    except:
        error(traceback.format_exc())
        pass
    bench = time() - start
    with _LOCK:
        _RUNTIME = _("%01.2f seconds") % bench
        _RUNNING = False


class GrepThread(object):
    def __init__(self, grep):
        """
        Set up grep thread with the pygrep object
        """

        self.grep = grep

    def run(self):
        """
        Run the grep search and store the results in a global array
        Also, store general statistics as well
        """
        global _ABORT
        global _RESULTS
        global _COMPLETED
        global _TOTAL
        global _RECORDS
        global _ERRORS
        with _LOCK:
            _RESULTS = []
            _COMPLETED = 0
            _TOTAL = 0
            _RECORDS = 0
            _ERRORS = []
        no_results = 0
        for f in self.grep.find():
            if f is None:
                pass
            elif isinstance(f, pygrep.FileRecord) and f.match is not None:
                with _LOCK:
                    _RESULTS.append(f)
            elif isinstance(f, pygrep.FileRecord) and f.error is not None:
                with _LOCK:
                    _ERRORS.append(f)
                    no_results += 1
            else:
                no_results += 1
            with _LOCK:
                _COMPLETED, _TOTAL, _RECORDS = self.grep.get_status()
                _RECORDS -= no_results
            if _ABORT:
                self.grep.abort()
                with _LOCK:
                    _ABORT = False
                break


class GrepArgs(object):
    def __init__(self):
        """
        Default the grep args on instatiation
        """

        self.reset()

    def reset(self):
        """
        Reset grep args to defaults
        """

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
        self.boolean = False


class DirPickButton(object):
    def GetPath(self):
        """
        Get current directory path
        """

        return self.directory

    def SetPath(self, directory):
        """
        Set the current directory path
        """

        if directory is not None and exists(directory) and isdir(directory):
            self.directory = directory

    def dir_init(self, default_path=None, dir_change_evt=None):
        """
        Init the DirPickButton
        """

        self.directory = expanduser("~")
        self.Bind(wx.EVT_BUTTON, self.on_dir_pick)
        self.Bind(EVT_DIR_CHANGE, self.on_dir_change)
        self.SetPath(default_path)
        self.dir_change_callback = dir_change_evt

    def on_dir_change(self, event):
        """
        If the dir has changed call the callback given
        """

        if self.dir_change_callback is not None:
            self.dir_change_callback(event)
        event.Skip()

    def on_dir_pick(self, event):
        """
        When a new directory is picked, validate it, and set it if it is good.
        Call the DirChangeEvent to do any desired callback as well.
        """

        directory = self.GetPath()
        if directory is None or not exists(directory) or not isdir(directory):
            directory = expanduser("~")
        directory = dirpickermsg(_("Select directory to rummage"), directory)
        if directory is None or directory == "":
            directory = None
        self.SetPath(directory)
        evt = DirChangeEvent(directory=directory)
        wx.PostEvent(self, evt)
        event.Skip()


class RummageFrame(gui.RummageFrame, DebugFrameExtender):
    def __init__(self, parent, script_path, start_path, open_debug=False):
        """
        Init the RummageFrame object
        """

        super(RummageFrame, self).__init__(parent)

        self.hide_limit_panel = False

        if _PLATFORM == "linux":
            self.m_progressbar.SetInitialSize(wx.Size(-1, 5))

        self.SetIcon(rum_64.GetIcon())

        self.debounce_search = False
        self.searchin_update = False
        self.tester = None
        self.checking = False
        self.kill = False
        self.script_path = script_path
        self.args = GrepArgs()
        self.thread = None

        # Setup debugging
        self.set_keybindings(
            [
                (wx.ACCEL_CMD if sys.platform == "darwin" else wx.ACCEL_CTRL, ord('A'), self.on_textctrl_selectall),
                (wx.ACCEL_NORMAL, wx.WXK_RETURN, self.on_enter_key)
            ],
            debug_event=self.on_debug_console
        )

        if open_debug:
            self.open_debug_console()

        # Setup search timer
        self.init_update_timer()

        # Extend the statusbar
        extend_sb(self.m_statusbar)
        self.m_statusbar.set_status("")

        # Extend browse button
        extend(self.m_searchin_dir_picker, DirPickButton)
        self.m_searchin_dir_picker.dir_init(dir_change_evt=self.on_dir_changed)

        # Replace result panel placeholders with new custom panels
        self.m_grep_notebook.DeletePage(2)
        self.m_grep_notebook.DeletePage(1)
        self.m_result_file_panel = FileResultPanel(self.m_grep_notebook, ResultFileList)
        self.m_result_content_panel = FileResultPanel(self.m_grep_notebook, ResultContentList)
        self.m_grep_notebook.InsertPage(1, self.m_result_file_panel, _("Files"), False)
        self.m_grep_notebook.InsertPage(2, self.m_result_content_panel, _("Content"), False)
        self.m_result_file_panel.load_table()
        self.m_result_content_panel.load_table()
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
            self.m_hide_limit_menuitem.SetItemLabel(_("Show Limit Search Panel"))

        self.init_search_path(start_path)

    def localize(self):
        self.m_search_panel.GetSizer().GetStaticBox().SetLabel(_("Search"))
        self.m_limiter_panel.GetSizer().GetStaticBox().SetLabel(_("Limit Search"))
        self.m_search_button.SetLabel(SEARCH_BTN_SEARCH)
        self.m_searchin_label.SetLabel(_("Where"))
        self.m_searchfor_label.SetLabel(_("What"))
        self.m_size_is_label.SetLabel(_("Size is"))
        self.m_modified_label.SetLabel(_("Modified"))
        self.m_created_label.SetLabel(_("Created"))
        self.m_exclude_label.SetLabel(_("Exclude folders"))
        self.m_filematch_label.SetLabel(_("Files which match"))
        self.m_regex_search_checkbox.SetLabel(_("Search with regex"))
        self.m_case_checkbox.SetLabel(_("Search case-sensitive"))
        self.m_dotmatch_checkbox.SetLabel(_("Dot matches newline"))
        self.m_utf8_checkbox.SetLabel(_("Treat all as UTF-8"))
        self.m_boolean_checkbox.SetLabel(_("Boolean match"))
        self.m_count_only_checkbox.SetLabel(_("Count only"))
        self.m_subfolder_checkbox.SetLabel(_("Include subfolders"))
        self.m_hidden_checkbox.SetLabel(_("Include hidden"))
        self.m_binary_checkbox.SetLabel(_("Include binary files"))
        self.m_dirregex_checkbox.SetLabel(_("Regex"))
        self.m_fileregex_checkbox.SetLabel(_("Regex"))
        self.m_regex_test_button.SetLabel(_("Test Regex"))
        self.m_save_search_button.SetLabel(_("Save Search"))
        self.m_load_search_button.SetLabel(_("Load Search"))
        self.m_grep_notebook.SetPageText(0, _("Search"))
        exportid = self.m_menu.FindMenuItem("File", "Export")
        self.m_menu.SetLabel(exportid, _("Export"))
        self.m_menu.SetMenuLabel(0, _("File"))
        self.m_menu.SetMenuLabel(1, _("View"))
        self.m_menu.SetMenuLabel(2, _("Help"))
        self.m_preferences_menuitem.SetItemLabel(_("&Preferences"))
        self.m_quit_menuitem.SetItemLabel(_("&Exit"))
        self.m_export_html_menuitem.SetItemLabel(_("HTML"))
        self.m_export_csv_menuitem.SetItemLabel(_("CSV"))
        self.m_hide_limit_menuitem.SetItemLabel(_("Hide Limit Search Panel"))
        self.m_about_menuitem.SetItemLabel(_("&About Rummage"))
        self.m_documentation_menuitem.SetItemLabel(_("Documentation"))
        self.m_issues_menuitem.SetItemLabel(_("Help and Support"))

        self.m_logic_choice.Clear()
        for x in [SIZE_ANY, SIZE_GT, SIZE_EQ, SIZE_LT]:
            self.m_logic_choice.Append(x)

        self.m_modified_choice.Clear()
        for x in [TIME_ANY, TIME_GT, TIME_EQ, TIME_LT]:
            self.m_modified_choice.Append(x)

        self.m_created_choice.Clear()
        for x in [TIME_ANY, TIME_GT, TIME_EQ, TIME_LT]:
            self.m_created_choice.Append(x)
        self.Fit()

    def on_enter_key(self, event):
        """
        Search on enter
        """

        obj = self.FindFocus()
        is_ac_combo = isinstance(obj, AutoCompleteCombo)
        is_date_picker = isinstance(obj, wx.GenericDatePickerCtrl)
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
        """
        Select all in the TextCtrl and AutoCompleteCombo objects
        """

        text = self.FindFocus()
        if isinstance(text, (wx.TextCtrl, AutoCompleteCombo)):
            text.SelectAll()
        event.Skip()

    def init_search_path(self, start_path):
        """
        Initialize the search path input
        """

        # Init search path with passed in path
        if start_path and exists(start_path):
            self.m_searchin_text.safe_set_value(abspath(normpath(start_path)))
        self.m_searchfor_textbox.GetTextCtrl().SetFocus()

    def optimize_size(self, first_time=False, height_only=False):
        """
        Optimally resize window
        """

        if _PLATFORM == "linux":
            self.GetSizer().Layout()
            self.Fit()
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
            if _PLATFORM == "linux" and not self.hide_limit_panel:
                self.SetMinSize(wx.Size(min_size[0], mainframe[1]))
                self.SetSize(wx.Size(mainframe[0], mainframe[1]))
            else:
                self.SetMinSize(wx.Size(min_size[0], mainframe[1] + offset + 15))
                self.SetSize(wx.Size(mainframe[0], mainframe[1] + offset + 15))
        self.Refresh()

    def setup_inputs(self):
        """
        Setup and configure input objects
        """

        self.m_regex_search_checkbox.SetValue(Settings.get_search_setting("regex_toggle", True))
        self.m_fileregex_checkbox.SetValue(Settings.get_search_setting("regex_file_toggle", False))

        self.m_logic_choice.SetStringSelection(
            eng_to_i18n(
                Settings.get_search_setting("size_compare_string", "any"),
                SIZE_LIMIT_I18N
            )
        )
        self.m_size_text.SetValue(Settings.get_search_setting("size_limit_string", "1000"))

        self.m_case_checkbox.SetValue(not Settings.get_search_setting("ignore_case_toggle", False))
        self.m_dotmatch_checkbox.SetValue(Settings.get_search_setting("dotall_toggle", False))
        self.m_utf8_checkbox.SetValue(Settings.get_search_setting("utf8_toggle", False))
        self.m_boolean_checkbox.SetValue(Settings.get_search_setting("boolean_toggle", False))
        self.m_count_only_checkbox.SetValue(Settings.get_search_setting("count_only_toggle", False))

        self.m_hidden_checkbox.SetValue(Settings.get_search_setting("hidden_toggle", False))
        self.m_subfolder_checkbox.SetValue(Settings.get_search_setting("recursive_toggle", True))
        self.m_binary_checkbox.SetValue(Settings.get_search_setting("binary_toggle", False))

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

        # GUI is built with WxFormBuilder, but it isn't easy to fill in custom objects.
        # So place holder objects are added for the sake of planning the gui, and then they
        # are replaced here with the actual objects.
        self.m_modified_date_picker = replace_with_genericdatepicker(self.m_modified_date_picker, "modified_date_string")
        self.m_created_date_picker = replace_with_genericdatepicker(self.m_created_date_picker, "created_date_string")

        self.m_modified_time_picker = replace_with_timepicker(
            self.m_modified_time_picker, self.m_modified_spin, "modified_time_string"
        )
        self.m_created_time_picker = replace_with_timepicker(
            self.m_created_time_picker, self.m_created_spin, "created_time_string"
        )

        self.m_searchin_text = replace_with_autocomplete(
            self.m_searchin_text, "target", changed_callback=self.on_searchin_changed
        )
        self.m_searchfor_textbox = replace_with_autocomplete(
            self.m_searchfor_textbox, "regex_search" if self.m_regex_search_checkbox.GetValue() else "literal_search"
        )
        self.m_exclude_textbox = replace_with_autocomplete(
            self.m_exclude_textbox, "regex_folder_exclude" if self.m_dirregex_checkbox.GetValue() else "folder_exclude"
        )
        self.m_filematch_textbox = replace_with_autocomplete(
            self.m_filematch_textbox,
            "regex_file_search" if self.m_fileregex_checkbox.GetValue() else "file_search",
            load_last=True,
            default=([".*"] if self.m_fileregex_checkbox.GetValue() else ["*?"])
        )

        # We caused some tab traversal chaos with the object replacement.
        # Fix it in platforms where it matters.
        if _PLATFORM != "osx":
            self.m_searchin_text.MoveBeforeInTabOrder(self.m_searchin_dir_picker)
            self.m_searchfor_textbox.MoveBeforeInTabOrder(self.m_regex_search_checkbox)
            self.m_modified_choice.MoveAfterInTabOrder(self.m_size_text)
            self.m_modified_date_picker.MoveAfterInTabOrder(self.m_modified_choice)
            self.m_modified_time_picker.MoveAfterInTabOrder(self.m_modified_date_picker)
            self.m_created_choice.MoveAfterInTabOrder(self.m_modified_time_picker)
            self.m_created_date_picker.MoveAfterInTabOrder(self.m_created_choice)
            self.m_created_time_picker.MoveAfterInTabOrder(self.m_created_date_picker)
            self.m_exclude_textbox.MoveBeforeInTabOrder(self.m_dirregex_checkbox)
            self.m_filematch_textbox.MoveBeforeInTabOrder(self.m_fileregex_checkbox)

    def on_preferences(self, event):
        """
        Show settings dialog, and update history of AutoCompleteCombo if the history was cleared
        """

        dlg = SettingsDialog(self)
        dlg.ShowModal()
        if dlg.history_cleared():
            update_autocomplete(self.m_searchin_text, "target")
            update_autocomplete(
                self.m_searchfor_textbox,
                "regex_search" if self.m_regex_search_checkbox.GetValue() else "search"
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

    def on_dir_changed(self, event):
        """
        Event for when the directory changes in the DirPickButton
        """

        if not self.searchin_update:
            pth = event.directory
            if pth is not None and exists(pth):
                self.searchin_update = True
                self.m_searchin_text.safe_set_value(pth)
                self.searchin_update = False
        event.Skip()

    def on_searchin_changed(self):
        """
        Callback for when a directory changes via the m_searchin_text control
        """

        self.check_searchin()

    def on_save_search(self, event):
        """
        Open a dialog to save a search for later use
        """

        search = self.m_searchfor_textbox.GetValue()
        if search == "":
            errormsg(_("There is no search to save!"))
            return
        dlg = SaveSearchDialog(self, search, self.m_regex_search_checkbox.GetValue())
        dlg.ShowModal()
        dlg.Destroy()

    def on_load_search(self, event):
        """
        Show dialog to pick saved a saved search to use
        """

        dlg = LoadSearchDialog(self)
        dlg.ShowModal()
        search, is_regex = dlg.get_search()
        dlg.Destroy()
        if search is not None and is_regex is not None:
            self.m_searchfor_textbox.SetValue(search)
            self.m_regex_search_checkbox.SetValue(regex_search)

    def limit_panel_toggle(self):
        """
        Show/Hide limit panel
        """

        if not self.hide_limit_panel:
            pth = self.m_searchin_text.GetValue()
            if isfile(pth):
                self.m_limiter_panel.Hide()
                self.m_limiter_panel.GetContainingSizer().Layout()
                self.optimize_size()
            else:
                self.m_limiter_panel.Show()
                self.m_limiter_panel.Fit()
                self.m_limiter_panel.GetSizer().Layout()
                self.m_limiter_panel.GetContainingSizer().Layout()
                self.m_settings_panel.GetSizer().Layout()
                self.optimize_size()
        else:
            self.m_limiter_panel.Hide()
            self.m_limiter_panel.GetContainingSizer().Layout()
            self.optimize_size()

    def limit_panel_hide(self):
        """
        Hide the limit panel
        """

        self.limit_panel_toggle()
        self.optimize_size(height_only=True)

    def check_searchin(self):
        """
        Determine if search in input is a file or not, and hide/show elements accordingly
        """

        self.limit_panel_toggle()

        pth = self.m_searchin_text.GetValue()
        if not self.searchin_update:
            if isdir(pth):
                self.m_searchin_dir_picker.SetPath(pth)
            elif isfile(pth):
                self.m_searchin_dir_picker.SetPath(dirname(pth))
            self.searchin_update = False

    def on_search_click(self, event):
        """
        Search button click
        """

        self.start_search()
        event.Skip()

    def start_search(self):
        """
        Initiate search or stop search depending on search state
        """

        with _LOCK:
            if self.debounce_search:
                return
        self.debounce_search = True
        if self.m_search_button.GetLabel() in [SEARCH_BTN_STOP, SEARCH_BTN_ABORT]:
            if self.thread is not None:
                self.m_search_button.SetLabel(SEARCH_BTN_ABORT)
                global _ABORT
                with _LOCK:
                    _ABORT = True
                self.kill = True
            else:
                self.stop_update_timer()
        else:
            if not self.validate_search_inputs():
                self.do_search()
            self.debounce_search = False

    def validate_search_inputs(self):
        """
        Validate the search inputs
        """

        debug("validate")
        fail = False
        msg = ""
        if self.m_regex_search_checkbox.GetValue():
            if self.m_searchfor_textbox.GetValue() == "" or self.validate_search_regex():
                msg = _("Please enter a valid search regex!")
                fail = True
        elif self.m_searchfor_textbox.GetValue() == "":
            msg = _("Please enter a valid search!")
            fail = True
        if not fail and self.m_fileregex_checkbox.GetValue():
            if self.m_filematch_textbox.GetValue().strip() == "" or self.validate_regex(self.m_filematch_textbox.Value):
                msg = "Please enter a valid file regex!"
                fail = True
        elif self.m_filematch_textbox.GetValue().strip() == "":
            msg = _("Please enter a valid file pattern!")
            fail = True
        if not fail and self.m_dirregex_checkbox.GetValue():
            if self.validate_regex(self.m_exclude_textbox.Value):
                msg = _("Please enter a valid exlcude directory regex!")
                fail = True
        if not fail and not exists(self.m_searchin_text.GetValue()):
            msg = _("Please enter a valid search path!")
            fail = True
        if (
            not fail and
            self.m_logic_choice.GetStringSelection() != "any" and
            re.match(r"[1-9]+[\d]*", self.m_size_text.GetValue()) is None
        ):
            msg = _("Please enter a valid size!")
            fail = True
        if not fail:
            try:
                self.m_modified_date_picker.GetValue().Format("%m/%d/%Y")
            except:
                msg = _("Please enter a modified date!")
                fail = True
        if not fail:
            try:
                self.m_created_date_picker.GetValue().Format("%m/%d/%Y")
            except:
                msg = _("Please enter a created date!")
                fail = True
        if fail:
            errormsg(msg)
        return fail

    def init_update_timer(self):
        """
        Init the update Timer object]
        """

        self.update_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.check_updates, self.update_timer)

    def start_update_timer(self):
        """
        Start update timer
        """

        if not self.update_timer.IsRunning():
            self.update_timer.Start(2000)
            debug("Grep timer started")

    def stop_update_timer(self):
        """
        Stop update timer
        """

        if self.update_timer.IsRunning():
            self.update_timer.Stop()
            debug("Grep timer stopped")

    def do_search(self):
        """
        Start the search
        """

        self.thread = None

        # Reset status
        self.m_progressbar.SetRange(100)
        self.m_progressbar.SetValue(0)
        self.m_statusbar.set_status("")

        # Remove errors icon in status bar
        self.m_statusbar.remove_icon("errors")

        # Change button to stop search
        self.m_search_button.SetLabel(SEARCH_BTN_STOP)

        # Init search status
        self.m_statusbar.set_status(_("Searching: 0/0 0% Matches: 0"))

        # Setup arguments
        self.set_arguments()
        self.save_history()

        # Setup search thread
        self.thread = threading.Thread(
            target=threaded_grep,
            args=(
                self.args.target,
                self.args.pattern,
                not_none(self.args.regexfilepattern, alt=not_none(self.args.filepattern)),
                not_none(self.args.directory_exclude),
                get_flags(self.args),
                self.args.show_hidden,
                self.args.all_utf8,
                self.args.size_compare,
                self.args.modified_compare,
                self.args.created_compare,
                self.args.text,
                self.args.count_only,
                self.args.boolean
            )
        )
        self.thread.setDaemon(True)

        # Reset result tables
        self.count = 0
        self.m_grep_notebook.DeletePage(2)
        self.m_grep_notebook.DeletePage(1)
        self.m_result_file_panel = FileResultPanel(self.m_grep_notebook, ResultFileList)
        self.m_result_content_panel = FileResultPanel(self.m_grep_notebook, ResultContentList)
        self.m_grep_notebook.InsertPage(1, self.m_result_file_panel, _("Files"), False)
        self.m_grep_notebook.InsertPage(2, self.m_result_content_panel, _("Content"), False)

        # Run search thread
        self.thread.start()
        self.start_update_timer()

    def set_arguments(self):
        """
        Set the search arguments
        """

        self.args.reset()
        # Path
        self.args.target = self.m_searchin_text.GetValue()

        # Search Options
        self.args.ignore_case = not self.m_case_checkbox.GetValue()
        self.args.dotall = self.m_dotmatch_checkbox.GetValue()
        self.args.regexp = self.m_regex_search_checkbox.GetValue()
        self.args.recursive = self.m_subfolder_checkbox.GetValue()
        self.args.all_utf8 = self.m_utf8_checkbox.GetValue()
        self.args.pattern = self.m_searchfor_textbox.Value
        self.args.text = self.m_binary_checkbox.GetValue()
        self.args.count_only = self.m_count_only_checkbox.GetValue()
        self.args.boolean = self.m_boolean_checkbox.GetValue()

        # Limit Options
        if isdir(self.args.target):
            self.args.show_hidden = self.m_hidden_checkbox.GetValue()
            if self.m_fileregex_checkbox.GetValue():
                self.args.regexfilepattern = self.m_filematch_textbox.Value
            elif self.m_filematch_textbox.Value:
                self.args.filepattern = self.m_filematch_textbox.Value
            if self.m_exclude_textbox.Value != "":
                self.args.directory_exclude = self.m_exclude_textbox.Value
            if self.m_dirregex_checkbox.GetValue():
                self.args.regexdirpattern = True
            cmp_size = self.m_logic_choice.GetSelection()
            if cmp_size:
                size = self.m_size_text.GetValue()
                self.args.size_compare = (LIMIT_COMPARE[cmp_size], int(size))
            else:
                self.args.size_compare = None
            cmp_modified = self.m_modified_choice.GetSelection()
            cmp_created = self.m_created_choice.GetSelection()
            if cmp_modified:
                self.args.modified_compare = (
                    LIMIT_COMPARE[cmp_modified],
                    local_time_to_epoch_timestamp(
                        self.m_modified_date_picker.GetValue().Format("%m/%d/%Y"),
                        self.m_modified_time_picker.GetValue()
                    )
                )
            if cmp_created:
                self.args.created_compare = (
                    LIMIT_COMPARE[cmp_created],
                    local_time_to_epoch_timestamp(
                        self.m_modified_date_picker.GetValue().Format("%m/%d/%Y"),
                        self.m_modified_time_picker.GetValue()
                    )
                )
        else:
            self.args.text = True

        debug(self.args.target)

    def save_history(self):
        """
        Save the current configuration of the search for the next time the app is opened
        Save a history of search directory, regex, folders, and excludes as well for use again in the future
        """

        history = [
            ("target", self.args.target),
            ("regex_search", self.args.pattern) if self.args.regexp else ("literal_search", self.args.pattern)
        ]

        if isdir(self.args.target):
            history += [
                ("regex_folder_exclude", self.args.directory_exclude) if self.m_dirregex_checkbox.GetValue() else ("folder_exclude", self.args.directory_exclude),
                ("regex_file_search", self.args.regexfilepattern),
                ("file_search", self.args.filepattern)
            ]

        toggles = [
            ("regex_toggle", self.args.regexp),
            ("ignore_case_toggle", self.args.ignore_case),
            ("dotall_toggle", self.args.dotall),
            ("utf8_toggle", self.args.all_utf8),
            ("recursive_toggle", self.args.recursive),
            ("hidden_toggle", self.args.show_hidden),
            ("binary_toggle", self.args.text),
            ("regex_file_toggle", self.m_fileregex_checkbox.GetValue()),
            ("boolean_toggle", self.args.boolean),
            ("count_only_toggle", self.args.count_only)
        ]

        eng_size = i18n_to_eng(self.m_logic_choice.GetStringSelection(), SIZE_LIMIT_I18N)
        eng_mod = i18n_to_eng(self.m_modified_choice.GetStringSelection(), TIME_LIMIT_I18N)
        eng_cre = i18n_to_eng(self.m_created_choice.GetStringSelection(), TIME_LIMIT_I18N)
        strings = [
            ("size_compare_string", eng_size),
            ("modified_compare_string", eng_mod),
            ("created_compare_string", eng_cre)
        ]

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
        update_autocomplete(
            self.m_searchfor_textbox,
            "regex_search" if self.m_regex_search_checkbox.GetValue() else "search"
        )
        update_autocomplete(
            self.m_exclude_textbox,
            "regex_folder_exclude" if self.m_dirregex_checkbox.GetValue() else "folder_exclude"
        )
        update_autocomplete(
            self.m_filematch_textbox,
            "regex_file_search" if self.m_fileregex_checkbox.GetValue() else "file_search"
        )

    def check_updates(self, event):
        """
        Check if updates to the result lists can be done
        """

        global _RESULTS
        global _ERRORS
        debug("Processing current results")
        if not self.checking:
            self.checking = True
            with _LOCK:
                running = _RUNNING
                completed = _COMPLETED
                total = _TOTAL
                records = _RECORDS
            count = self.count
            if records > count:
                with _LOCK:
                    results = _RESULTS[0:records - count]
                    _RESULTS = _RESULTS[records - count:len(_RESULTS)]
                count = self.update_table(count, completed, total, *results)
            else:
                self.m_statusbar.set_status(
                    _("Searching: %d/%d %d%% Matches: %d") % (
                        completed,
                        total,
                        int(float(completed)/float(total) * 100) if total != 0 else 0,
                        count
                    )
                )
                self.m_progressbar.SetRange(total)
                self.m_progressbar.SetValue(completed)
            self.count = count

            # Run is finished or has been terminated
            if not running:
                with _LOCK:
                    benchmark = _RUNTIME

                self.stop_update_timer()
                self.m_search_button.SetLabel(SEARCH_BTN_SEARCH)
                if self.kill:
                    self.m_statusbar.set_status(
                        _("Searching: %d/%d %d%% Matches: %d Benchmark: %s") % (
                            completed,
                            completed,
                            100,
                            count,
                            benchmark
                        )
                    )
                    self.m_progressbar.SetRange(completed)
                    self.m_progressbar.SetValue(completed)
                    if Settings.get_notify():
                        notify.error(
                            _("Search Aborted"),
                            _("\n%d matches found!") % count,
                            sound=Settings.get_alert()
                        )
                    elif Settings.get_alert():
                        notify.play_alert()
                    self.kill = False
                else:
                    self.m_statusbar.set_status(
                        _("Searching: %d/%d %d%% Matches: %d Benchmark: %s") % (
                            completed,
                            completed,
                            100,
                            count,
                            benchmark
                        )
                    )
                    self.m_progressbar.SetRange(100)
                    self.m_progressbar.SetValue(100)
                    if Settings.get_notify():
                        notify.info(
                            _("Search Completed"),
                            _("\n%d matches found!") % count,
                            sound=Settings.get_alert()
                        )
                    elif Settings.get_alert():
                        notify.play_alert()
                with _LOCK:
                    error_count = len(_ERRORS)
                    if error_count:
                        graphic = error_icon.GetImage()
                        graphic.Rescale(16, 16)
                        image = wx.BitmapFromImage(graphic)
                        self.m_statusbar.set_icon(
                            _("errors"), image,
                            msg=_("%d errors\nSee log for details.") % error_count,
                            context=[(_("View Log"), lambda e: self.open_debug_console())]
                        )
                        for e in _ERRORS:
                            error(
                                _("Cound not process %s:\n%s") % (
                                    unicode(e.info.name) if e.info is not None else _("file"), e.error
                                )
                            )
                        _ERRORS = []
                self.m_result_file_panel.load_table()
                self.m_result_content_panel.load_table()
                self.m_grep_notebook.SetSelection(1)
                wx.GetApp().Yield()
                self.debounce_search = False
            self.checking = False
        event.Skip()

    def update_table(self, count, done, total, *results):
        """
        Update the result lists with current search results
        """

        p_range = self.m_progressbar.GetRange()
        p_value = self.m_progressbar.GetValue()
        actually_done = done - 1 if done > 0 else 0
        for f in results:
            self.m_result_file_panel.set_match(f)
            if self.args.count_only or self.args.boolean:
                count += 1
                continue

            self.m_result_content_panel.set_match(f)
            count += 1

        if p_range != total:
            self.m_progressbar.SetRange(total)
        if p_value != done:
            self.m_progressbar.SetValue(actually_done)
        self.m_statusbar.set_status(
            _("Searching: %d/%d %d%% Matches: %d") % (
                actually_done, total,
                int(float(actually_done)/float(total) * 100) if total != 0 else 0,
                count
            ) if total != 0 else (0, 0, 0)
        )
        wx.GetApp().Yield()
        return count

    def on_regex_search_toggle(self, event):
        """
        Switch literal/regex history depending on toggle state
        """

        if self.m_regex_search_checkbox.GetValue():
            update_autocomplete(self.m_searchfor_textbox, "regex_search")
        else:
            update_autocomplete(self.m_searchfor_textbox, "literal_search")
        event.Skip()

    def on_fileregex_toggle(self, event):
        """
        Switch literal/regex history depending on toggle state
        """

        if self.m_fileregex_checkbox.GetValue():
            update_autocomplete(self.m_filematch_textbox, "regex_file_search", default=[".*"])
        else:
            update_autocomplete(self.m_filematch_textbox, "file_search", default=["*?"])
        event.Skip()

    def on_dirregex_toggle(self, event):
        """
        Switch literal/regex history depending on toggle state
        """

        if self.m_dirregex_checkbox.GetValue():
            update_autocomplete(self.m_exclude_textbox, "regex_folder_exclude")
        else:
            update_autocomplete(self.m_exclude_textbox, "folder_exclude")
        event.Skip()

    def validate_search_regex(self):
        """
        Validate search regex
        """

        flags = 0
        if self.m_dotmatch_checkbox.GetValue():
            flags |= re.DOTALL
        if not self.m_case_checkbox.GetValue():
            flags |= re.IGNORECASE
        return self.validate_regex(self.m_searchfor_textbox.Value, flags)

    def validate_regex(self, pattern, flags=0):
        """
        Validate regular expresion compiling
        """
        try:
            re.compile(pattern, flags)
            return False
        except:
            errormsg(_("Invalid Regular Expression!"))
            error(traceback.format_exc())
            return True

    def on_debug_console(self, event):
        """
        Show debug console
        """

        self.toggle_debug_console()

    def on_close(self, event):
        """
        Ensure thread is stopped,
        and ensure tester window, debug console is closed
        """
        if self.thread is not None:
            self.thread.abort = True
        if self.tester is not None:
            try:
                self.tester.Close()
            except:
                pass
        self.close_debug_console()
        event.Skip()

    def on_test_regex(self, event):
        """
        Show regex test dialog
        """

        self.m_regex_test_button.Enable(False)
        self.tester = RegexTestDialog(
            self,
            self.m_case_checkbox.GetValue(),
            self.m_dotmatch_checkbox.GetValue(),
            self.m_searchfor_textbox.GetValue()
        )
        self.tester.Show()

    def on_export_html(self, event):
        """
        Export to HTML
        """

        if (
            len(self.m_result_file_panel.list.itemDataMap) == 0 and
            len(self.m_result_content_panel.list.itemDataMap) == 0
        ):
            errormsg(_("There is nothing to export!"))
            return
        html_file = filepickermsg(_("Export to..."), "*.html", True)
        if html_file is None:
            return
        try:
            export_html.export(
                html_file,
                self.args.pattern,
                self.args.regexp,
                self.m_result_file_panel.list.itemDataMap,
                self.m_result_content_panel.list.itemDataMap
            )
        except:
            error(traceback.format_exc())
            errormsg(_("There was a problem exporting the HTML!  See the log for more info."))

    def on_export_csv(self, event):
        """
        Export to CSV
        """

        if (
            len(self.m_result_file_panel.list.itemDataMap) == 0 and
            len(self.m_result_content_panel.list.itemDataMap) == 0
        ):
            errormsg(_("There is nothing to export!"))
            return
        csv_file = filepickermsg(_("Export to..."), "*.csv", True)
        if csv_file is None:
            return
        try:
            export_csv.export(
                csv_file,
                self.args.pattern,
                self.args.regexp,
                self.m_result_file_panel.list.itemDataMap,
                self.m_result_content_panel.list.itemDataMap
            )
        except:
            error(traceback.format_exc())
            errormsg(_("There was a problem exporting the CSV!  See the log for more info."))

    def on_hide_limit(self, event):
        """
        Hide limit panel
        """

        self.hide_limit_panel = not self.hide_limit_panel
        self.limit_panel_hide()
        Settings.set_hide_limit(self.hide_limit_panel)
        if self.hide_limit_panel:
            self.m_hide_limit_menuitem.SetItemLabel(_("Show Limit Search Panel"))
        else:
            self.m_hide_limit_menuitem.SetItemLabel(_("Hide Limit Search Panel"))

    def on_documentation(self, event):
        """
        Open documentation site
        """

        webbrowser.open_new_tab(version.manual)

    def on_issues(self, event):
        """
        Open issues site
        """

        webbrowser.open_new_tab(version.help)

    def on_about(self, event):
        """
        Show about dialog
        """

        dlg = AboutDialog(self)
        dlg.ShowModal()
        dlg.Destroy()

    def on_exit(self, event):
        """
        Close dialog
        """

        self.Close()
