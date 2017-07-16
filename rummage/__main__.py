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
from __future__ import unicode_literals
from __future__ import absolute_import
import argparse
import sys
from .lib import util
from .lib import __meta__
from .lib.gui import rummage_dialog
from .lib.gui.app import rummage_app
from .lib.gui.settings import Settings


def parse_arguments():
    """Parse the arguments."""

    parser = argparse.ArgumentParser(prog=__meta__.__app__, description='A python grep like tool.')
    # Flag arguments
    parser.add_argument('--version', action='version', version=('%(prog)s ' + __meta__.__version__))
    parser.add_argument('--debug', action='store_true', default=False, help=argparse.SUPPRESS)
    parser.add_argument('--no-redirect', action='store_true', default=False, help=argparse.SUPPRESS)
    parser.add_argument('--path', default=None, help="Path to search.")
    return parser.parse_args(util.to_unicode_argv()[1:])


def run():
    """Configure environment, start the app, and launch the appropriate frame."""

    args = parse_arguments()

    Settings.load_settings(args.debug)
    single_instance = Settings.get_single_instance()

    if args.debug:
        rummage_app.set_debug_mode(True)

    app = rummage_app.RummageApp(
        redirect=not args.no_redirect,
        single_instance_name="Rummage" if single_instance else None,
        pipe_name=Settings.get_fifo() if single_instance else None
    )

    if not single_instance or app.is_instance_okay():
        rummage_dialog.RummageFrame(
            None,
            args.path if args.path is not None else None,
            debug_mode=args.debug
        ).Show()

    app.MainLoop()

    Settings.unload()

    return 0


def main():
    """Main entry point."""

    sys.exit(run())


if __name__ == "__main__":
    main()
