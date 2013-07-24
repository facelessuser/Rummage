#!/usr/bin/python
import sys
from os.path import exists, dirname, abspath, join
from os import path, mkdir, chdir
import shutil
import argparse
import subprocess

if sys.platform.startswith('win'):
    _PLATFORM = "windows"
elif sys.platform == "darwin":
    _PLATFORM = "osx"
else:
    _PLATFORM = "linux"


class Args(object):
    def __init__(self, script, name, gui, clean, ext, icon=None, portable=False, imports=[]):
        """
        Build arguments
        """

        self.gui = bool(gui)
        self.name = name
        self.clean = bool(clean)
        self.icon = icon
        self.script = script
        self.extension = ext
        self.portable = portable
        self.imports = imports


class BuildParams(object):
    """
    Build parametes
    """

    python_bin_path = None
    python_executable = None
    pyinstaller_script = None
    out_dir = None
    script = None
    upx_bin = None
    dist_path = None
    name = None
    clean = None
    extension = None
    icon = None
    portable = None
    imports = None


def parse_settings(args, obj):
    """
    Configure build parameters based on arguments
    """

    err = False

    script_path = dirname(abspath(sys.argv[0]))
    obj.python_bin_path = dirname(sys.executable)
    obj.python_bin = sys.executable
    obj.pyinstaller_script = join(script_path, "pyinstaller", "pyinstaller.py")
    obj.out_dir = join(script_path, "build")
    obj.dist_path = join(script_path, "dist")
    obj.upx_bin = None
    obj.name = args.name
    obj.extension = args.extension
    obj.script = path.abspath(path.normpath(args.script))
    obj.icon = args.icon
    obj.clean = args.clean
    obj.portable = args.portable
    obj.imports = args.imports

    if not path.exists(obj.script):
        print >> sys.stderr, "Could not find %s!" % obj.script
        err = True
    elif args.icon != None and not path.exists(args.icon):
        print >> sys.stderr, "Could not find %s!" % obj.icon
        err = True
    elif obj.pyinstaller_script == None or not path.exists(obj.pyinstaller_script):
        print >> sys.stderr, "Could not find pyinstaller.py!"
        err |= True

    if not path.exists(obj.out_dir):
        err |= create_dir(obj.out_dir)
    elif not path.isdir(obj.out_dir):
        print >> sys.stderr, "%s is not a directory!" % output_directory
        err |= True

    # Get executable name to build
    if not err:
        obj.app = path.join(obj.dist_path, obj.name) + obj.extension
    return err


def create_dir(directory):
    """
    Create build directory
    """

    err = False
    try:
        print "Creating %s..." % directory
        mkdir(directory)
    except:
        print >> sys.stderr, "Could not create %s!" % directory
        err = True
    return err


def clean_build(build_dir):
    """
    Clean the build directory
    """

    err = False
    try:
        print "Cleaning %s..." % build_dir
        shutil.rmtree(build_dir)
    except:
        print >> sys.stderr, "Failed to clean %s!" % build_dir
        err = True
    return err


def get_hidden_imports(imports):
    """
    Return list of hidden imports
    """

    hidden_imports = []
    for i in imports:
        hidden_imports.append('--hidden-import=%s' % i)
    return hidden_imports


def parse_options(args, obj):
    """
    Parse the build parameters and build the pyinstaller build command
    """

    err = False

    # Parse Settings file
    if not err:
        err = parse_settings(args, obj)

    # See if cleaning is required
    if not err and args.clean and path.exists(obj.out_dir):
        err = clean_build(obj.out_dir)

    # Construct build params for build processs
    if not err:
        obj.params = (
            [("python" if obj.portable else obj.python_bin), obj.pyinstaller_script, '-F'] +
            (['--upx-dir=%s' % obj.upx_bin] if obj.upx_bin is not None else []) +
            (['--icon=%s' % args.icon] if args.icon is not None else []) +
            (['--clean'] if args.clean is not None else []) +
            (['-w', '--workpath=%s' % obj.out_dir] if args.gui else ['--workpath=%s' % obj.out_dir]) +
            ['--distpath=%s' % obj.dist_path] +
            get_hidden_imports(obj.imports) +
            ['--name=%s' % args.name] +
            ['-y', obj.script]
        )
    return err


def build(obj):
    """
    Launch the build process
    """

    err = False

    if obj.portable:
        chdir(obj.python_bin_path)
    # Setup build process
    process = subprocess.Popen(
        obj.params,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=False
    )

    # Kick off build process
    print "Building %s..." % obj.app
    print "Please be patient; this might take a while.\nResults and/or errors will be posted when complete."
    output = process.communicate()

    # Check for bad error code
    if process.returncode:
        print >> sys.stderr, "Compilation failed!"
        err = True

    # Display output
    print output[0]

    return err

def main():
    """
    Setup the build process and initiate it
    """

    parser = argparse.ArgumentParser(prog='Build', description='Python script for building apps for Pyinstaller')
    # Flag arguments
    parser.add_argument('--version', action='version', version='%(prog)s 1.0.0')
    parser.add_argument('--clean', '-c', action='store_true', default=False, help='Clean build before re-building.')
    parser.add_argument('--portable', '-p', action='store_true', default=False, help='Build with portable python (windows)')
    parser.add_argument('name', default=None, help='Name of app')
    inputs = parser.parse_args()
    if _PLATFORM == "osx":
        args = Args("Rummage.py", inputs.name, True, inputs.clean, ".app", abspath("_icons/rummage.icns"))
    elif _PLATFORM == "windows":
        args = Args("Rummage.py", inputs.name, True, inputs.clean, ".exe", abspath("_icons\\rummage.ico"), args.portable)
    else:
        args = Args(
            "Rummage.py", inputs.name, True, inputs.clean, "",
            imports=[
                "gobject", "glib", "glib._glib", "glib.option", "object.constants",
                "gobject._gobject", "gobject.propertyhelper", "gtk", "gtk._gtk"
            ]
        )

    # Parse options
    build_params = BuildParams()
    err = parse_options(args, build_params)

    # Build executable
    if not err:
        err = build(build_params)

    return err

if __name__ == "__main__":
    sys.exit(main())
