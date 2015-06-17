"""
Rummage (main).

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
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
from . import version
import sys
import argparse
import os
from .gui.settings import Settings

Settings.load_settings()  # noqa

from .gui.rummage_app import set_debug_mode, RummageApp, RummageFrame, RegexTestDialog


def parse_arguments():
    """Parse the arguments."""

    parser = argparse.ArgumentParser(prog=version.app, description='A python grep like tool.')
    # Flag arguments
    parser.add_argument('--version', action='version', version=('%(prog)s ' + version.version))
    parser.add_argument('--show_log', '-l', action='store_true', default=False, help="Open log on startup")
    parser.add_argument('--searchpath', '-s', nargs=1, default=None, help="Path to search.")
    parser.add_argument('--regextool', '-r', action='store_true', default=False, help="Open just the regex tester.")
    return parser.parse_args()


def main(script):
    """Configure environment, start the app, and launch the appropriate frame."""

    args = parse_arguments()
    if args.show_log:
        set_debug_mode(True)

    if Settings.get_single_instance():
        app = RummageApp(redirect=True, single_instance_name="Rummage", pipe_name=Settings.get_fifo())
    else:
        app = RummageApp(redirect=True)

    if not Settings.get_single_instance() or (Settings.get_single_instance() and app.is_instance_okay()):
        if args.regextool:
            RegexTestDialog(None, False, False, stand_alone=True).Show()
        else:
            RummageFrame(
                None, script,
                args.searchpath[0] if args.searchpath is not None else None,
                open_debug=args.show_log
            ).Show()
    app.MainLoop()


def cli():
    """Command line interface."""

    script_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    sys.exit(main(script_path))
