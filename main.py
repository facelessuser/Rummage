"""
Rummage (main)

Licensed under MIT
Copyright (c) 2011 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import gui
import wx
import re
import sys
import threading
import argparse
import subprocess
import traceback
from time import time, sleep, ctime
from os.path import abspath, exists, basename, dirname, join, normpath, isdir, isfile

import _lib.pygrep as pygrep
from _lib.generic_dialogs import *
from _lib.custom_app import CustomApp, DebugFrameExtender
from _lib.custom_app import set_debug_mode, set_debug_console, get_debug_mode, get_debug_console
from _lib.custom_app import debug, debug_struct, info, error
from _lib.custom_statusbar import extend_sb, extend
from _lib.settings import Settings, _PLATFORM
from _lib.autocomplete_combo import AutoCompleteCombo
from _lib.sorted_columns import extend_list
from regex_test_dialog import RegexTestDialog
from load_search_dialog import LoadSearchDialog
from save_search_dialog import SaveSearchDialog
from settings_dialog import SettingsDialog


__version__ = "1.0.0"

_LOCK = threading.Lock()
_RUNNING = False
_RESULTS = []
_COMPLETED = 0
_TOTAL = 0
_PROCESSED = 0
_ABORT = False
_RUNTIME = None
SIZE_COMPARE = {
    0: "any",
    1: "gt",
    2: "eq",
    3: "lt"
}


def editor_open(filename, line, col):
    returncode = None

    print filename, line, col
    cmd = Settings.get_editor(filename=filename, line=line, col=col)
    if len(cmd) == 0:
        errormsg("No editor is currently set!")
        return
    debug(cmd)

    if sys.platform.startswith('win'):
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        process = subprocess.Popen(
            cmd,
            startupinfo=startupinfo,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE,
            shell=False
        )
    else:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE,
            shell=False
        )
    process.communicate()
    returncode = process.returncode
    return returncode


def get_flags(args):
    flags = 0

    if args.regexfilepattern != None:
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
    return item if item != None else alt


def update_choices(obj, key, load_last=False):
    choices = Settings.get_search_setting(key, [])
    if hasattr(obj, "update_choices"):
        obj.update_choices(choices, load_last)
    else:
        extend(obj, AutoCompleteCombo)
        obj.setup(choices, load_last)


def threaded_grep(
    target, pattern, file_pattern, folder_exclude,
    flags, show_hidden, all_utf8, size, text
):
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
                size=size,
                text=text
            )
        )
        grep.run()
    except:
        print(str(traceback.format_exc()))
        pass
    bench = time() - start
    with _LOCK:
        _RUNTIME = "%01.2f seconds" % bench
        _RUNNING = False


class GrepThread(object):
    def __init__(self, grep):
        self.grep = grep

    def run(self):
        global _ABORT
        global _RESULTS
        global _COMPLETED
        global _TOTAL
        _RESULTS = []
        _COMPLETED = 0
        _TOTAL = 0
        for f in self.grep.find():
            if f["count"] != 0:
                with _LOCK:
                    _RESULTS.append(f)
            with _LOCK:
                _COMPLETED, _TOTAL = self.grep.get_status()
            if _ABORT:
                self.grep.abort()
                with _LOCK:
                    _ABORT = False
                break


class GrepArgs(object):
    def __init__(self):
        self.reset()

    def reset(self):
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


class RummageFrame(gui.RummageFrame, DebugFrameExtender):
    def __init__(self, parent, script_path, start_path):
        super(RummageFrame, self).__init__(parent)

        extend_sb(self.m_statusbar)
        self.reset_table()
        extend_list(self.m_result_list, self.m_result_content_panel, 3)
        extend_list(self.m_result_file_list, self.m_result_file_panel, 6)

        self.debounce_search = False
        self.searchin_update = False
        self.checking = False
        self.kill = False
        self.script_path = script_path
        self.args = GrepArgs()
        self.thread = None
        self.set_keybindings(debug_event=self.on_debug_console)
        if get_debug_mode():
            self.open_debug_console()
        self.init_update_timer()
        self.m_grep_notebook.SetSelection(0)

        self.m_regex_search_checkbox.SetValue(Settings.get_search_setting("regex_toggle", True))
        self.m_fileregex_checkbox.SetValue(Settings.get_search_setting("regex_file_toggle", False))

        self.m_logic_choice.SetStringSelection(Settings.get_search_setting("size_compare_string", "greater than"))
        self.m_size_text.SetValue(Settings.get_search_setting("size_limit_string", "1000"))

        self.m_case_checkbox.SetValue(not Settings.get_search_setting("ignore_case_toggle", False))
        self.m_dotmatch_checkbox.SetValue(Settings.get_search_setting("dotall_toggle", False))
        self.m_utf8_checkbox.SetValue(Settings.get_search_setting("utf8_toggle", False))

        self.m_hidden_checkbox.SetValue(Settings.get_search_setting("hidden_toggle", False))
        self.m_subfolder_checkbox.SetValue(Settings.get_search_setting("recursive_toggle", True))
        self.m_binary_checkbox.SetValue(Settings.get_search_setting("binary_toggle", False))

        update_choices(self.m_searchin_text, "target")
        update_choices(self.m_searchfor_textbox, "regex_search" if self.m_regex_search_checkbox.GetValue() else "literal_search")
        update_choices(self.m_exclude_textbox, "regex_folder_exclude" if self.m_dirregex_checkbox.GetValue() else "folder_exclude")
        update_choices(self.m_filematch_textbox, "regex_file_search" if self.m_fileregex_checkbox.GetValue() else "file_search", load_last=True)

        if start_path and exists(start_path):
            self.m_searchin_text.SetValue(abspath(normpath(start_path)))
        self.m_searchfor_textbox.SetFocus()

        best = self.m_settings_panel.GetBestSize()
        current = self.m_settings_panel.GetSize()
        offset = best[1] - current[1]
        mainframe = self.GetSize()
        self.SetSize(wx.Size(mainframe[0], mainframe[1] + offset + 15))
        self.SetMinSize(self.GetSize())

    def on_preferences(self, event):
        dlg = SettingsDialog(self)
        dlg.ShowModal()
        dlg.Destroy()

    def on_dir_changed(self, event):
        if not self.searchin_update:
            pth = self.m_searchin_dir_picker.GetPath()
            if exists(pth):
                self.searchin_update = True
                self.m_searchin_text.SetValue(pth)
                self.searchin_update = False
        event.Skip()

    def on_searchin_enter(self, event):
        self.check_searchin()
        event.Skip()

    def on_searchin_selected(self, event):
        self.check_searchin()
        event.Skip()

    def on_searchin_changed(self, event):
        self.check_searchin()
        event.Skip()

    def on_save_search(self, event):
        search = self.m_searchfor_textbox.GetValue()
        if search == "":
            errormsg("There is no search to save!")
            return
        dlg = SaveSearchDialog(self, search, self.m_regex_search_checkbox.GetValue())
        dlg.ShowModal()
        dlg.Destroy()

    def on_load_search(self, event):
        dlg = LoadSearchDialog(self)
        dlg.ShowModal()
        search, is_regex = dlg.get_search()
        dlg.Destroy()
        if search is not None and is_regex is not None:
            self.m_searchfor_textbox.SetValue(search)
            self.m_regex_search_checkbox.SetValue(regex_search)

    def enable_panel(self, panel, enable):
        # For some odd reason, OSX panel Enable doesn't work
        # This is a work around
        if _PLATFORM == "windows":
            panel.Enable(enable)
        else:
            for child in panel.GetChildren():
                child.Enable(enable)

    def check_searchin(self):
        pth = self.m_searchin_text.GetValue()
        if isfile(pth):
            self.enable_panel(self.m_limit_size_panel, False)
            self.enable_panel(self.m_limit_panel, False)
        else:
            self.enable_panel(self.m_limit_size_panel, True)
            self.enable_panel(self.m_limit_panel, True)
        if not self.searchin_update:
            if isdir(pth):
                self.m_searchin_dir_picker.SetPath(pth)
            self.searchin_update = False

    def reset_table(self):
        self.m_result_list.ClearAll()
        self.m_result_list.InsertColumn(0, "File")
        self.m_result_list.InsertColumn(1, "Line")
        self.m_result_list.InsertColumn(2, "Context")
        self.m_result_file_list.ClearAll()
        self.m_result_file_list.InsertColumn(0, "File")
        self.m_result_file_list.InsertColumn(1, "Size")
        self.m_result_file_list.InsertColumn(2, "Matches")
        self.m_result_file_list.InsertColumn(3, "Path")
        self.m_result_file_list.InsertColumn(4, "Encoding")
        self.m_result_file_list.InsertColumn(5, "Time")
        self.m_progressbar.SetRange(100)
        self.m_progressbar.SetValue(0)
        self.m_statusbar.set_status("")
        wx.GetApp().Yield()

    def open_in_editor(self, filename, line, col):
        editor_open(filename, line, col)

    def on_content_dclick(self, event):
        pos = event.GetPosition()
        item = self.m_result_list.HitTestSubItem(pos)[0]
        if item != -1:
            filename = self.m_result_list.GetItem(item, col=0).GetText()
            line = self.m_result_list.GetItem(item, col=1).GetText()
            row = self.m_result_list.GetItemData(item)
            file_row = self.m_result_content_panel.get_map_item(row, col=3)
            col = str(self.m_result_content_panel.get_map_item(row, col=4))
            path = self.m_result_file_panel.get_map_item(file_row, col=3)
            self.open_in_editor(join(normpath(path), filename), line, col)
        event.Skip()

    def on_file_dclick(self, event):
        pos = event.GetPosition()
        item = self.m_result_file_list.HitTestSubItem(pos)[0]
        if item != -1:
            filename = self.m_result_file_list.GetItem(item, col=0).GetText()
            path = self.m_result_file_list.GetItem(item, col=3).GetText()
            row = self.m_result_file_list.GetItemData(item)
            line = str(self.m_result_file_panel.get_map_item(row, col=6))
            col = str(self.m_result_file_panel.get_map_item(row, col=7))
            self.open_in_editor(join(normpath(path), filename), line, col)
        event.Skip()

    def on_search_click(self, event):
        with _LOCK:
            if self.debounce_search:
                return
        self.debounce_search = True
        if self.m_search_button.GetLabel() == "Stop":
            if self.thread is not None:
                global _ABORT
                with _LOCK:
                    _ABORT = True
                self.kill = True
            else:
                self.stop_update_timer()
        else:
            debug("validate")
            if self.m_regex_search_checkbox.GetValue():
                if self.validate_search_regex():
                    return
            if self.m_fileregex_checkbox.GetValue():
                if self.validate_regex(self.m_filematch_textbox.Value):
                    return
            if self.m_dirregex_checkbox.GetValue():
                if self.validate_regex(self.m_exclude_textbox.Value):
                    return
            if not exists(self.m_searchin_text.GetValue()):
                errormsg("Please enter a valid search path!")
                return
            debug("search")
            self.do_search()
            self.debounce_search = False
        event.Skip()

    def init_update_timer(self):
        self.update_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.check_updates, self.update_timer)

    def start_update_timer(self):
        if not self.update_timer.IsRunning():
            self.update_timer.Start(2000)
            debug("Grep timer started")

    def stop_update_timer(self):
        if self.update_timer.IsRunning():
            self.update_timer.Stop()
            debug("Grep timer stopped")

    def do_search(self):
        self.thread = None
        self.reset_table()
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
                if size == "":
                    errormsg("Please enter a valid file size!")
                    return
                self.args.size_compare = (SIZE_COMPARE[cmp_size], int(size))
            else:
                self.args.size_compare = None
        else:
            self.args.text = True

        debug(self.args.target)

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
            ("regex_file_toggle", self.m_fileregex_checkbox.GetValue())
        ]

        strings = [
            ("size_compare_string", self.m_logic_choice.GetStringSelection()),
            ("size_limit_string", self.m_size_text.GetValue())
        ]

        Settings.add_search_settings(history, toggles, strings)

        update_choices(self.m_searchin_text, "target")
        update_choices(self.m_searchfor_textbox, "regex_search" if self.m_regex_search_checkbox.GetValue() else "search")
        update_choices(self.m_exclude_textbox, "regex_folder_exclude" if self.m_dirregex_checkbox.GetValue() else "folder_exclude")
        update_choices(self.m_filematch_textbox, "regex_file_search" if self.m_fileregex_checkbox.GetValue() else "file_search")

        self.current_table_idx = [-1, -1]
        self.m_search_button.SetLabel("Stop")
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
                self.args.text
            )
        )
        self.thread.setDaemon(True)
        self.m_result_content_panel.reset_item_map()
        self.m_result_file_panel.reset_item_map()
        with _LOCK:
            global _PROCESSED
            _PROCESSED = 0
        self.thread.start()
        self.m_grep_notebook.SetSelection(1)
        self.start_update_timer()

    def check_updates(self, event):
        global _RESULTS
        debug("timer")
        if not self.checking:
            self.checking = True
            with _LOCK:
                running = _RUNNING
                completed = _COMPLETED
                total = _TOTAL
                processed = _PROCESSED
            count1 = self.current_table_idx[0] + 1
            count2 = self.current_table_idx[1] + 1
            if completed > count1:
                with _LOCK:
                    results = _RESULTS[0:completed - count1]
                    _RESULTS = _RESULTS[completed - count1:len(_RESULTS)]
                count1, count2 = self.update_table(count1, count2, completed, total, *results)
            self.current_table_idx[0] = count1 - 1
            self.current_table_idx[1] = count2 - 1
            if not running:
                with _LOCK:
                    benchmark = _RUNTIME

                self.stop_update_timer()
                self.m_search_button.SetLabel("Search")
                if self.kill:
                    self.m_statusbar.set_status("Searching: %d/%d %d%% Matches: %d Benchmark: %s" % (completed, completed, 100, count2, benchmark))
                    self.m_progressbar.SetRange(completed)
                    self.m_progressbar.SetValue(completed)
                    self.kill = False
                else:
                    self.m_statusbar.set_status("Searching: %d/%d %d%% Matches: %d Benchmark: %s" % (completed, completed, 100, count2, benchmark))
                    self.m_progressbar.SetRange(100)
                    self.m_progressbar.SetValue(100)
                if completed > 0:
                    self.m_result_file_panel.init_sort()
                    self.m_result_content_panel.init_sort()
                wx.GetApp().Yield()
                self.debounce_search = False
            self.checking = False
        event.Skip()

    def update_table(self, count, count2, done, total, *results):
        self.m_result_list.Freeze()
        p_range = self.m_progressbar.GetRange()
        p_value = self.m_progressbar.GetValue()
        self.m_statusbar.set_status("Searching: %d/%d %d%% Matches: %d" % (done, total, int(float(done)/float(total) * 100), count2) if total != 0 else (0, 0, 0))
        if p_range != total:
            self.m_progressbar.SetRange(total)
        if p_value != done:
            self.m_progressbar.SetValue(done)

        for f in results:
            self.m_result_file_list.InsertStringItem(count, basename(f["name"]))
            self.m_result_file_list.SetStringItem(count, 1, f["size"])
            self.m_result_file_list.SetStringItem(count, 2, str(f["count"]))
            self.m_result_file_list.SetStringItem(count, 3, dirname(f["name"]))
            self.m_result_file_list.SetStringItem(count, 4, f["encode"])
            self.m_result_file_list.SetStringItem(count, 5, ctime(f["time"]))
            self.m_result_file_list.SetItemImage(count, 0)
            self.m_result_file_list.SetItemData(count, count)
            self.m_result_file_panel.set_item_map(count, basename(f["name"]), float(f["size"].strip("KB")), f["count"], dirname(f["name"]), f["encode"], f["time"], f["results"][0]["lineno"], f["results"][0]["colno"])
            for r in f["results"]:
                self.m_result_list.InsertStringItem(count2, basename(f["name"]))
                self.m_result_list.SetStringItem(count2, 1, str(r["lineno"]))
                self.m_result_list.SetStringItem(count2, 2, r["lines"].split(f["line_ending"])[0].replace("\r", ""))
                self.m_result_list.SetItemImage(count2, 0)
                self.m_result_list.SetItemData(count2, count2)
                self.m_result_content_panel.set_item_map(count2, basename(f["name"]), r["lineno"], r["lines"].replace("\r", "").split("\n")[0], count,  r["colno"])
                count2 += 1
            count += 1
        self.m_result_list.Thaw()
        if len(results):
            self.column_resize(self.m_result_file_list, 6)
            self.column_resize(self.m_result_list, 3)
        self.m_statusbar.set_status("Searching: %d/%d %d%% Matches: %d" % (done, total, int(float(done)/float(total) * 100), count2) if total != 0 else (0, 0, 0))
        wx.GetApp().Yield()
        return count, count2

    def column_resize(self, obj, count, minimum=100):
        for i in range(0, count):
            obj.SetColumnWidth(i, wx.LIST_AUTOSIZE)
            if obj.GetColumnWidth(i) < minimum:
                obj.SetColumnWidth(i, minimum)

    def get_search_status(self):
        return self.searching

    def on_regex_search_toggle(self, event):
        if self.m_regex_search_checkbox.GetValue():
            update_choices(self.m_searchfor_textbox, "regex_search")
        else:
            update_choices(self.m_searchfor_textbox, "literal_search")
        event.Skip()

    def on_fileregex_toggle(self, event):
        if self.m_fileregex_checkbox.GetValue():
            update_choices(self.m_filematch_textbox, "regex_file_search")
        else:
            update_choices(self.m_filematch_textbox, "file_search")
        event.Skip()

    def on_dirregex_toggle(self, event):
        if self.m_dirregex_checkbox.GetValue():
            update_choices(self.m_exclude_textbox, "regex_folder_exclude")
        else:
            update_choices(self.m_exclude_textbox, "folder_exclude")
        event.Skip()

    def validate_search_regex(self):
        flags = 0
        if self.m_dotmatch_checkbox.GetValue():
            flags |= re.DOTALL
        if not self.m_case_checkbox.GetValue():
            flags |= re.IGNORECASE
        return self.validate_regex(self.m_searchfor_textbox.Value, flags)

    def validate_regex(self, pattern, flags=0):
        try:
            re.compile(pattern, flags)
            return False
        except:
            errormsg("Invalid Regular Expression!")
            return True

    def on_debug_console(self, event):
        self.open_debug_console()

    def on_close(self, event):
        if self.thread is not None:
            self.thread.abort = True
        self.close_debug_console()
        event.Skip()

    def on_test_regex(self, event):
        self.m_regex_test_button.Enable(False)
        RegexTestDialog(
            self,
            self.m_case_checkbox.GetValue(),
            self.m_dotmatch_checkbox.GetValue(),
            self.m_searchfor_textbox.GetValue()
        ).Show()


def parse_arguments():
    parser = argparse.ArgumentParser(prog='Rummage', description='A python grep like tool.')
    # Flag arguments
    parser.add_argument('--version', action='version', version=('%(prog)s ' + __version__))
    parser.add_argument('--debug', '-d', action='store_true', default=False, help=argparse.SUPPRESS)
    parser.add_argument('--searchpath', '-s', nargs=1, default=None, help="Path to search.")
    return parser.parse_args()


def gui_main(script):
    Settings.load_settings()
    args = parse_arguments()
    if args.debug:
        set_debug_mode(True)
    app = CustomApp(redirect=True, single_instance_name="Rummage")
    if app.is_instance_okay() or not Settings.get_single_instance():
        RummageFrame(None, script, args.searchpath[0] if args.searchpath is not None else None).Show()
    app.MainLoop()


if __name__ == "__main__":
    if sys.platform == "darwin" and len(sys.argv) > 1 and sys.argv[1].startswith("-psn"):
        script_path = join(dirname(abspath(sys.argv[0])), "..", "..", "..")
        del sys.argv[1]
    else:
        script_path = dirname(abspath(sys.argv[0]))

    sys.exit(gui_main(script_path))
