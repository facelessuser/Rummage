"""
Rummage (main)

Licensed under MIT
Copyright (c) 2011 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import wx
import sys
import argparse
import traceback
from os.path import abspath, exists, basename, dirname, join, normpath, isdir, isfile
import os
import wx.lib.newevent
import time
import thread

from _lib.settings import Settings, _PLATFORM

from _gui.custom_app import CustomApp, set_debug_mode
from _gui.custom_app import debug, debug_struct, info, error
from _gui.rummage_dialog import RummageFrame
from _gui.regex_test_dialog import RegexTestDialog

__version__ = "1.0.0"

PipeEvent, EVT_PIPE_ARGS = wx.lib.newevent.NewEvent()


class ArgPipeThread(object):
    def __init__(self, app, pipe_name):
        self.app = app
        self.pipe_name = pipe_name

    def Start(self):
        self.check_pipe = True
        self.running = True
        thread.start_new_thread(self.Run, ())

    def Stop(self):
        self.check_pipe = False
        if not os.path.exists(self.pipe_name):
            os.mkfifo(self.pipe_name)
        pid = os.fork()
        with open(self.pipe_name, "w") as pipeout:
            pipeout.write('\n')
            pipeout.flush()

    def IsRunning(self):
        return self.running

    def Run(self):
        if not os.path.exists(self.pipe_name):
            os.mkfifo(self.pipe_name)

        pid = os.fork()
        while self.check_pipe:
            with open(self.pipe_name, "r") as pipein:
                line = pipein.readline()[:-1]
                if line != "":
                    evt = PipeEvent(data=line)
                    wx.PostEvent(self.app, evt)
                time.sleep(0.2)
        self.running = False


def parse_arguments():
    parser = argparse.ArgumentParser(prog='Rummage', description='A python grep like tool.')
    # Flag arguments
    parser.add_argument('--version', action='version', version=('%(prog)s ' + __version__))
    parser.add_argument('--debug', '-d', action='store_true', default=False, help=argparse.SUPPRESS)
    parser.add_argument('--searchpath', '-s', nargs=1, default=None, help="Path to search.")
    parser.add_argument('--regextool', '-r', action='store_true', default=False, help="Open just the regex tester.")
    return parser.parse_args()


class PipeApp(CustomApp):
    def __init__(self, *args, **kwargs):
        self.active_pipe = False
        self.pipe_thread = None
        self.pipe_name = kwargs.get("pipe_name", None)
        if "pipe_name" in kwargs:
            del kwargs["pipe_name"]
        super(PipeApp, self).__init__(*args, **kwargs)

    def OnInit(self):
        super(PipeApp, self).OnInit()
        self.Bind(EVT_PIPE_ARGS, self.on_pipe_args)
        if self.pipe_name is not None and _PLATFORM is not "windows":
            if self.is_instance_okay():
                self.receive_arg_pipe()
            else:
                self.send_arg_pipe()
                return False
        return True

    def send_arg_pipe(self):
        if len(sys.argv) > 1:
            if not os.path.exists(self.pipe_name):
                os.mkfifo(self.pipe_name)

            pid = os.fork()
            with open(self.pipe_name, "w") as pipeout:
                argv = iter(sys.argv[1:])
                args = []
                for a in argv:
                    args.append(a)
                    if a == "-s":
                        try:
                            args.append(abspath(normpath(argv.next())))
                        except StopIteration:
                            break
                pipeout.write('|'.join(args) + '\n')
                pipeout.flush()

    def receive_arg_pipe(self):
        self.active_pipe = True
        self.pipe_thread = ArgPipeThread(self, self.pipe_name)
        self.pipe_thread.Start()

    def OnExit(self):
        if self.active_pipe:
            wx.Yield()
            self.pipe_thread.Stop()
            running = True
            while running:
                running = self.pipe_thread.IsRunning()
                time.sleep(0.1)
        super(PipeApp, self).OnExit()

    def on_pipe_args(self, event):
        frame = self.GetTopWindow()
        if frame is not None and isinstance(frame, RummageFrame):
            args = iter(event.data.split("|"))
            filename = None
            for a in args:
                if a == "-s":
                    try:
                        a = args.next()
                        filename = a
                        break
                    except StopIteration:
                        break
            frame.m_searchin_text.SetValue(filename)
            if frame.IsIconized():
                frame.Iconize(False)
            if not frame.IsShown():
                frame.Show(True)
            frame.Raise()


def gui_main(script):
    Settings.load_settings()
    args = parse_arguments()
    if args.debug:
        set_debug_mode(True)

    if Settings.get_single_instance():
        app = PipeApp(redirect=True, single_instance_name="Rummage", pipe_name=Settings.get_fifo())
    else:
        app = PipeApp(redirect=True)

    if not Settings.get_single_instance() or (Settings.get_single_instance() and app.is_instance_okay()):
        if args.regextool:
            RegexTestDialog(None, False, False, stand_alone=True).Show()
        else:
            RummageFrame(None, script, args.searchpath[0] if args.searchpath is not None else None).Show()
    app.MainLoop()


if __name__ == "__main__":
    if sys.platform == "darwin" and len(sys.argv) > 1 and sys.argv[1].startswith("-psn"):
        script_path = join(dirname(abspath(sys.argv[0])), "..", "..", "..")
        del sys.argv[1]
    else:
        script_path = dirname(abspath(sys.argv[0]))

    sys.exit(gui_main(script_path))
