import gui
import wx
import re
from os.path import abspath, exists, basename, dirname, join, normpath, isdir, isfile
import _lib.pygrep as pygrep
from _lib.pygrep import _PLATFORM
import sys
import threading
import argparse
from time import time, sleep
from _lib.custom_app import CustomApp, DebugFrameExtender, init_app_log
from _lib.custom_app import set_debug_mode, set_debug_console, get_debug_mode, get_debug_console
from _lib.custom_app import debug, debug_struct, info, error
import _lib.messages as messages
from _lib.custom_statusbar import extend_sb
import subprocess
from _lib.json import sanitize_json
import json
# import wx.lib.agw.ultimatelistctrl as ULC

# wx.SystemOptions.SetOptionInt("mac.listctrl.always_use_generic", 0)
# import wx.lib.mixins.listctrl as listctrlmixin

__version__ = "1.0.0"

_RUNNING = False
_RESULTS = []
_COMPLETED = 0
_TOTAL = 0
_ABORT = False
SIZE_COMPARE = {
    0: "gt",
    1: "eq",
    2: "lt"
}

class Settings(object):
    filename = None
    @classmethod
    def load_settings(cls, filename):
        cls.settings_file = filename
        cls.settings = {}
        if cls.settings_file is not None:
            try:
                with open(cls.settings_file, "r") as f:
                    cls.settings = json.loads(sanitize_json(f.read(), preserve_lines=True))
            except Exception as e:
                errormsg("Failed to load settings file!\n\n%s" % str(e))

    @classmethod
    def get_editor(cls, filename, line):
        editor = cls.settings.get("editor", [])
        if isinstance(editor, dict):
            editor = editor.get(_PLATFORM, [])

        return [arg.replace("{$file}", filename).replace("{$line}", str(line)) for arg in editor]

    @classmethod
    def set_editor(cls, editor):
        cls.settings["editor"] = editor
        cls.save_settings()

    @classmethod
    def save_settings(cls):
        try:
            with open(cls.settings_file, "w") as f:
                f.write(json.dumps(cls.settings, sort_keys=True, indent=4, separators=(',', ': ')))
        except Exception as e:
            errormsg("Failed to save settings file!\n\n%s" % str(e))


def editor_open(filename, line):
    returncode = None

    cmd = Settings.get_editor(filename, line)
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


def threaded_grep(target, pattern, file_pattern, folder_exclude, flags, show_hidden, all_utf8, size):
    global _RUNNING
    _RUNNING = True
    grep = GrepThread(
        pygrep.Grep(
            target=target,
            pattern=pattern,
            file_pattern=file_pattern,
            folder_exclude=folder_exclude,
            flags=flags,
            show_hidden=show_hidden,
            all_utf8=all_utf8,
            size=size
        )
    )
    grep.run()
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
                _RESULTS.append(f)
            _COMPLETED, _TOTAL = self.grep.get_status()
            if _ABORT:
                self.grep.abort()
                _ABORT = False
                break


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

    return flags


def not_none(item, alt=None, idx=None):
    return (item if idx == None else item[idx]) if item != None else alt


class GrepArgs(object):
    def __init__(self):
        self.reset()

    def reset(self):
        self.regexp = False
        self.ignore_case = False
        self.dotall = False
        self.recursive = False
        self.directory_exclude = None
        self.regexfilepattern = None
        self.filepattern = None
        self.pattern = None
        self.target = None
        self.show_hidden = False
        self.size_compare = None


class PyGrepFrame(gui.PyGrep, DebugFrameExtender):
    def __init__(self, parent, script_path, start_path):
        gui.PyGrep.__init__(self, parent)

        # result_list_sizer = wx.BoxSizer(wx.VERTICAL)
        # self.m_result_list = ULC.UltimateListCtrl(self.m_result_content_panel, wx.ID_ANY, agwStyle=wx.LC_REPORT | wx.LC_SINGLE_SEL | ULC.ULC_HAS_VARIABLE_ROW_HEIGHT)
        # result_list_sizer.Add(self.m_result_list, 1, wx.ALL|wx.EXPAND, 5)
        # self.m_result_content_panel.SetSizer(result_list_sizer)
        # self.m_result_content_panel.Layout()
        # self.m_result_list.Bind(wx.EVT_LEFT_DCLICK, self.on_content_dclick)

        # result_file_list_sizer = wx.BoxSizer(wx.VERTICAL)
        # self.m_result_file_list = ULC.UltimateListCtrl(self.m_result_file_panel, wx.ID_ANY, agwStyle=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        # result_file_list_sizer.Add( self.m_result_file_list, 1, wx.ALL|wx.EXPAND, 5 )
        # self.m_result_file_panel.SetSizer(result_file_list_sizer)
        # self.m_result_file_panel.Layout()
        # self.m_result_file_list.Bind(wx.EVT_LEFT_DCLICK, self.on_file_dclick)

        # self.Layout()
        # debug("Auto")
        # debug(self.m_filematch_textbox.AutoComplete(["*.*", "*.py"]))
        extend_sb(self.m_statusbar)

        self.searchin_update = False
        self.checking = False
        self.kill = False
        self.script_path = script_path
        self.args = GrepArgs()
        self.thread = None
        self.set_keybindings(debug_event=self.on_debug_console)
        if get_debug_mode():
            self.open_debug_console()
        self.reset_table()
        self.init_update_timer()
        self.m_grep_notebook.SetSelection(0)
        best = self.m_settings_panel.GetBestSize()
        current = self.m_settings_panel.GetSize()
        offset = best[1] - current[1]
        mainframe = self.GetSize()
        self.SetSize(wx.Size(mainframe[0], mainframe[1] + offset + 15))
        self.SetMinSize(self.GetSize())
        if start_path and exists(start_path):
            self.m_searchin_text.SetValue(abspath(normpath(start_path)))
            self.m_searchfor_textbox.SetFocus()

    def on_dir_changed(self, event):
        if not self.searchin_update:
            pth = self.m_searchin_dir_picker.GetPath()
            if exists(pth):
                self.searchin_update = True
                self.m_searchin_text.SetValue(pth)
                self.searchin_update = False
        event.Skip()

    def on_searchin_changed(self, event):
        pth = self.m_searchin_text.GetValue()
        if isfile(pth):
            self.m_limit_size_panel.Enable(False)
            self.m_limit_panel.Enable(False)
        else:
            self.m_limit_size_panel.Enable(True)
            self.m_limit_panel.Enable(True)
        if not self.searchin_update:
            if isdir(pth):
                self.m_searchin_dir_picker.SetPath(pth)
            self.searchin_update = False
        event.Skip()

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
        self.m_progressbar.SetRange(100)
        self.m_progressbar.SetValue(0)
        self.m_statusbar.set_status("")
        wx.GetApp().Yield()

    def open_in_editor(self, filename, line):
        editor_open(filename, line)

    def on_content_dclick(self, event):
        pos = event.GetPosition()
        item = self.m_result_list.HitTestSubItem(pos)[0]
        if item != -1:
            filename = self.m_result_list.GetItem(item, col=0).GetText()
            line = self.m_result_list.GetItem(item, col=1).GetText()
            idx = self.m_result_list.GetItemData(item)
            path = self.m_result_file_list.GetItem(idx, col=3).GetText()
            self.open_in_editor(join(normpath(path), filename), line)
        event.Skip()

    def on_file_dclick(self, event):
        pos = event.GetPosition()
        item = self.m_result_file_list.HitTestSubItem(pos)[0]
        if item != -1:
            filename = self.m_result_file_list.GetItem(item, col=0).GetText()
            path = self.m_result_file_list.GetItem(item, col=3).GetText()
            line = self.m_result_file_list.GetItemData(item)
            self.open_in_editor(join(normpath(path), filename), line)
        event.Skip()

    def on_search_click(self, event):
        if self.m_search_button.GetLabel() == "Stop":
            if self.thread is not None:
                global _ABORT
                _ABORT = True
                self.kill = True
        else:
            debug("validate")
            if self.m_search_regex_radio.GetValue():
                if self.validate_search_regex():
                    return
            if self.m_filematchregex_radio.GetValue():
                if self.validate_regex(self.m_filematch_textbox.Value):
                    return
            if self.validate_regex(self.m_exclude_textbox.Value):
                return
            if not exists(self.m_searchin_text.GetValue()):
                errormsgS("Please enter a valid search path!")
                return
            debug("search")
            self.do_search()

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
        self.args.regexp = self.m_search_regex_radio.GetValue()
        self.args.recursive = self.m_subfolder_checkbox.GetValue()
        self.args.all_utf8 = self.m_utf8_checkbox.GetValue()
        self.args.pattern = self.m_searchfor_textbox.Value

        # Limit Options
        if isdir(self.args.target):
            self.args.show_hidden = self.m_hidden_checkbox.GetValue()
            if self.m_filematchregex_radio.GetValue():
                self.args.regexfilepattern = [self.m_filematch_textbox.Value]
            elif self.m_filematch_textbox.Value:
                self.args.filepattern = [self.m_filematch_textbox.Value]
            if self.m_exclude_textbox.Value != "":
                self.args.directory_exclude = [self.m_exclude_textbox.Value]
            if self.m_size_radio.GetValue():
                size = self.m_size_text.GetValue()
                if size == "":
                    errormsg("Please enter a valid file size!")
                    return
                self.args.size_compare = (SIZE_COMPARE[self.m_logic_choice.GetSelection()], int(size))
            else:
                self.args.size_compare = None

        debug(self.args.target)

        self.current_table_idx = [-1, -1]
        self.m_search_button.SetLabel("Stop")
        self.thread = threading.Thread(
            target=threaded_grep,
            args=(
                self.args.target,
                self.args.pattern,
                not_none(self.args.regexfilepattern, alt=not_none(self.args.filepattern, idx=0), idx=0),
                not_none(self.args.directory_exclude, idx=0),
                get_flags(self.args),
                self.args.show_hidden,
                self.args.all_utf8,
                self.args.size_compare
            )
        )
        self.thread.setDaemon(True)
        self.thread.start()
        self.m_grep_notebook.SetSelection(1)
        self.start_update_timer()

    def check_updates(self, event):
        debug("timer")
        if not self.checking:
            self.checking = True
            running = _RUNNING
            completed = _COMPLETED
            total = _TOTAL
            count1 = self.current_table_idx[0] + 1
            count2 = self.current_table_idx[1] + 1
            if completed > count1:
                count1, count2 = self.update_table(count1, count2, completed, total, *_RESULTS[count1: completed])
            self.current_table_idx[0] = count1 - 1
            self.current_table_idx[1] = count2 - 1
            if not running:
                self.stop_update_timer()
                self.m_search_button.SetLabel("Search")
            if self.kill and not running:
                self.m_statusbar.set_status("Searching: %d/%d %d%%" % (completed, completed, 100))
                self.m_progressbar.SetRange(completed)
                self.m_progressbar.SetValue(completed)
                wx.GetApp().Yield()
                self.kill = False
            self.checking = False
        event.Skip()

    def update_table(self, count, count2, done, total, *results):
        self.m_result_list.Freeze()
        p_range = self.m_progressbar.GetRange()
        p_value = self.m_progressbar.GetValue()
        self.m_statusbar.set_status("Searching: %d/%d %d%%" % (done, total, int(float(done)/float(total) * 100)))
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
            self.m_result_file_list.SetItemData(count, f["results"][0]["lineno"])
            for r in f["results"]:
                self.m_result_list.InsertStringItem(count2, basename(f["name"]))
                self.m_result_list.SetStringItem(count2, 1, str(r["lineno"]))
                self.m_result_list.SetStringItem(count2, 2, r["lines"].replace("\r", "").split("\n")[0])
                self.m_result_list.SetItemData(count2, count)
                count2 += 1
            count += 1
        self.m_result_list.Thaw()
        if len(results):
            self.m_result_file_list.SetColumnWidth(0, wx.LIST_AUTOSIZE)
            self.m_result_file_list.SetColumnWidth(1, wx.LIST_AUTOSIZE)
            self.m_result_file_list.SetColumnWidth(2, wx.LIST_AUTOSIZE)
            self.m_result_file_list.SetColumnWidth(3, wx.LIST_AUTOSIZE)
            self.m_result_file_list.SetColumnWidth(4, wx.LIST_AUTOSIZE)
            self.m_result_list.SetColumnWidth(0, wx.LIST_AUTOSIZE)
            self.m_result_list.SetColumnWidth(1, wx.LIST_AUTOSIZE)
            self.m_result_list.SetColumnWidth(2, wx.LIST_AUTOSIZE)
        wx.GetApp().Yield()
        return count, count2

    def get_search_status(self):
        return self.searching

    def on_regex_enabled(self, event):
        if self.m_search_regex_radio.GetValue():
            self.validate_search_regex()

    def on_filematch_regex_enabled(self, event):
        if self.m_filematchregex_radio.GetValue():
            self.validate_regex(self.m_filematch_textbox.Value)

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


#################################################
# Basic Dialogs
#################################################
def yesno(question, title='Yes or no?', bitmap=None, yes="Okay", no="Cancel"):
    return messages.promptmsg(question, title, bitmap, yes, no)


def infomsg(msg, title="INFO", bitmap=None):
    messages.infomsg(msg, title, bitmap)


def errormsg(msg, title="ERROR", bitmap=None):
    error(msg)
    messages.errormsg(msg, title, bitmap)


def warnmsg(msg, title="WARNING", bitmap=None):
    messages.warnmsg(msg, title, bitmap)


def parse_arguments():
    parser = argparse.ArgumentParser(prog='Rummage', description='A python grep like tool.')
    # Flag arguments
    parser.add_argument('--version', action='version', version=('%(prog)s ' + __version__))
    parser.add_argument('--debug', '-d', action='store_true', default=False, help=argparse.SUPPRESS)
    parser.add_argument('--searchpath', '-s', nargs=1, default=None, help="Path to search.")
    return parser.parse_args()


def gui_main(script):
    init_app_log(join(script, "pygrep.log"))
    args = parse_arguments()
    if args.debug:
        set_debug_mode(True)
    app = CustomApp(redirect=args.debug)
    Settings.load_settings(join(script, "pygrep.settings"))
    PyGrepFrame(None, script, args.searchpath[0] if args.searchpath is not None else None).Show()
    app.MainLoop()


if __name__ == "__main__":
    if sys.platform == "darwin" and len(sys.argv) > 1 and sys.argv[1].startswith("-psn"):
        script_path = join(dirname(abspath(sys.argv[0])), "..", "..", "..")
        del sys.argv[1]
    else:
        script_path = dirname(abspath(sys.argv[0]))

    sys.exit(gui_main(script_path))
