import sys
from os.path import exists, dirname, abspath, join
import sys
from os import path, mkdir
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
    def __init__(self, script, name, gui, clean, ext, icon=None):
        self.gui = bool(gui)
        self.name = name
        self.clean = bool(clean)
        self.icon = icon
        self.script = script
        self.extension = ext


class BuildParams(object):
    python_bin = None
    pyinstaller_script = None
    out_dir = None
    script = None
    copy_from = None
    copy_to = None
    name = None
    upx_bin = None
    dist_path = None


def parse_settings(obj):
    # Configure build parameters
    err = False

    script_path = dirname(abspath(sys.argv[0]))
    obj.python_bin = sys.executable
    obj.pyinstaller_script = join(script_path, "pyinstaller", "pyinstaller.py")
    obj.out_dir = join(script_path, "build")
    obj.dist_path = join(script_path, "bin")
    obj.upx_bin = None
    # obj.upx_bin = "" if _PLATFORM == "windows" else None

    # if obj.upx_bin != None and not path.exists(path.join(obj.upx_bin, "upx.exe")):
    #     print >> sys.stderr, "Could not find UPX binary!"
    #     obj.upx_bin = None
    #     err |= True
    if obj.pyinstaller_script == None or not path.exists(obj.pyinstaller_script):
        print >> sys.stderr, "Could not find pyinstaller.py!"
        err |= True
    if not path.exists(obj.out_dir):
        err |= create_dir(obj.out_dir)
    elif not path.isdir(obj.out_dir):
        print >> sys.stderr, "%s is not a directory!" % output_directory
        err |= True
    return err


def create_dir(directory):
    # Create build directory
    err = False
    try:
        print "Creating %s..." % directory
        mkdir(directory)
    except:
        print >> sys.stderr, "Could not create %s!" % directory
        err = True
    return err


def clean_build(build_dir):
    # Clean the build directory
    err = False
    try:
        print "Cleaning %s..." % build_dir
        shutil.rmtree(build_dir)
    except:
        print >> sys.stderr, "Failed to clean %s!" % build_dir
        err = True
    return err


def parse_options(args, obj):
    err = False

    # Get script to build
    obj.script = path.abspath(path.normpath(args.script))
    if not path.exists(obj.script):
        print >> sys.stderr, "Could not find %s!" % obj.script
        err = True
    else:
        # Log the name without extension for use later
        obj.name, _ = args.name

    # Parse Settings file
    if not err:
        settings = parse_settings(obj)
        err = (settings == None)

    # See if cleaning is required
    if not err and args.clean and path.exists(obj.out_dir):
        err = clean_build(obj.out_dir)

    if args.icon != None and not path.exists(args.icon):
        err = True

    # Get executable name to build
    obj.app = path.join(obj.dist_path, obj.name) + args.extension

    # Construct build params for build processs
    obj.params = (
        [obj.python_bin, obj.pyinstaller_script, '-F'] +
        (['--upx-dir=%s' % obj.upx_bin] if obj.upx_bin is not None else []) +
        (['--icon=%s' % args.icon] if args.icon is not None else []) +
        (['-w', '--workpath=%s' % obj.out_dir] if args.gui else ['--workpath=%s' % obj.out_dir]) +
        ['--distpath=%s' % obj.dist_path] +
        ['--name=%s' % args.name] +
        ['-y', obj.script]
    )
    return err


def build(obj):
    err = False

    # Setup build process
    process = subprocess.Popen(
        obj.params,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=False
    )

    # Kick off build process
    print "Building %s..." % obj.app
    output = process.communicate()

    # Chekc for bad error code
    if process.returncode:
        print >> sys.stderr, "Compilation failed!"
        err = True

    # Display output
    print output[0]

    return err

def main():
    parser = argparse.ArgumentParser(prog='PyAppBuild', description='Python App building script for Pyinstaller')
    # Flag arguments
    parser.add_argument('--version', action='version', version='%(prog)s 1.0.0')
    parser.add_argument('--clean', '-c', action='store_true', default=False, help='Clean build before re-building.')
    inputs = parser.parse_args()
    if _PLATFORM == "osx":
        args = Args("main.py", "Rummage", True, inputs.clean, ".app")

    # Parse options
    build_params = BuildParams()
    err = parse_options(args, build_params)

    # Build executable
    if not err:
        err = build(build_params)

    return err

if __name__ == "__main__":
    sys.exit(main())
