#!/usr/bin/python
"""Build an executable with PyInstaller."""
from __future__ import print_function
import sys
from os.path import dirname, abspath, join
from os import path, mkdir, chdir, listdir
import shutil
import argparse
import subprocess
import zipfile
import yaml
import codecs
import traceback

PY3 = sys.version_info >= (3, 0)
if PY3:
    unicode_str = str
else:
    unicode_str = unicode  # noqa

if sys.platform.startswith('win'):
    _PLATFORM = "windows"
elif sys.platform == "darwin":
    _PLATFORM = "osx"
else:
    _PLATFORM = "linux"

SPEC = '''# -*- mode: python -*-
a = Analysis(%(main)s,
             pathex=%(directory)s,
             hiddenimports=%(hidden)s,
             hookspath=%(hook)s,
             runtime_hooks=None)
a.datas = %(data)s
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name=%(exe)s,
          debug=False,
          strip=None,
          icon=%(icon)s,
          console=%(gui)s)
'''

OSX_GUI_SPEC = '''
app = BUNDLE(exe,
             name=%(exe)s,
             icon=%(icon)s)
'''


class BuildVars(object):

    """Build variables."""

    extras = 'buildextras.yml'
    hidden_imports_to_crawl = []
    data_to_crawl = []
    hidden_imports = []
    data = []
    hookpaths = []
    paths = []

    def crawl_data(self):
        """Crawl data."""

        for target in self.data_to_crawl:
            if path.isfile(target):
                self.data.append((target, "./%s" % target, "DATA"))
            else:
                for f in listdir(target):
                    file_path = path.join(target, f)
                    if path.isfile(file_path) and not f.startswith((".", "~")) and not f.endswith('.py'):
                        name = '/'.join([target, f])
                        self.data.append((name, "./%s" % name, "DATA"))

    def crawl_hidden_imports(self):
        """Crawl hidden imports."""

        import pkgutil
        for mod in self.hidden_imports_to_crawl:
            pkg = pkgutil.get_loader(mod)
            if getattr(pkg, 'archive', None) is None:
                folder = pkg.filename
                self.hidden_imports.append(pkg.fullname)
                for f in listdir(folder):
                    if f != "__init__.py" and f.endswith('.py'):
                        self.hidden_imports.append('.'.join([pkg.fullname, f]))
            else:
                handle_egg(pkg.archive)

    def handle_egg(archive):
        """Handle an egg import."""

        def is_egg(archive):
            """Check if is an egg that we will accept."""

            egg_extension = "py%d.%d.egg" % (sys.version_info.major, sys.version_info.minor)
            return (
                path.isfile(archive) and
                path.basename(archive).endswith(egg_extension)
            )

        def hidden_egg_modules(archive):
            """Add egg modules to hidden imports."""

            with zipfile.ZipFile(archive, 'r') as z:
                text = z.read(z.getinfo('EGG-INFO/SOURCES.txt'))
                if PY3:
                    text = text.decode('utf-8')
                for line in text.split('\n'):
                    line = line.replace('\r', '')
                    if (
                        line.endswith('.py') and
                        not line.endswith('/__init__.py') and
                        line != 'setup.py'
                    ):
                        self.hidden_imports.append(line.replace('/', '.')[:-3])

        if is_egg(archive):
            self.paths.append(archive)
            hidden_egg_modules(archive)

    def print_vars(self, label, src):
        """Print specified variable."""

        print("--- %s ---" % label)
        for s in src:
            print(s)
        print('')

    def print_all_vars(self):
        """Print all the variables."""

        print('====== Processed Spec Variables =====')
        self.print_vars('Data', self.data)
        self.print_vars('Hidden Imports', self.hidden_imports)
        self.print_vars("Paths", self.paths)
        self.print_vars("Hooks", self.hookpaths)

    def read(self):
        """Read the build vars."""

        config = None
        if path.exists(self.extras):
            try:
                with codecs.open(self.extras, 'r', encoding='utf-8') as f:
                    config = yaml.load(f.read())
            except Exception:
                print(traceback.format_exc())
                config = None

        if config is not None:
            print(config)
            self.data_to_crawl.extend(config.get('data_to_crawl', []))
            self.hidden_imports_to_crawl.extend(config.get('hidden_imports_to_crawl', []))
            self.data.extend(config.get('data', []))
            self.hidden_imports.extend(config.get('hidden_imports', []))
            self.paths.extend(config.get('paths', []))
            self.hookpaths.extend(config.get('hookpaths', []))

        self.crawl_data()
        self.crawl_hidden_imports()


def build_spec_file(obj, gui):
    """Build the spec file."""
    proj_path = path.dirname(obj.script)
    sys.path.append(proj_path)

    build_vars = BuildVars()
    build_vars.read()

    build_vars.print_all_vars()
    spec = SPEC % {
        "main": repr([obj.script]),
        "directory": repr([path.dirname(obj.script)] + build_vars.paths),
        "hidden": repr(build_vars.hidden_imports),
        "hook": repr(build_vars.hookpaths),
        "data": repr(build_vars.data),
        "exe": repr(path.basename(obj.app)),
        "icon": repr(obj.icon),
        "gui": repr(not gui)
    }

    if gui and _PLATFORM == "osx":
        spec += OSX_GUI_SPEC % {
            "icon": repr(obj.icon),
            "exe": repr(path.basename(obj.app) + '.app')
        }

    with open("%s.spec" % obj.name, "w") as f:
        f.write(spec)


class Args(object):

    """Argument object."""

    def __init__(self, script, name, **kwargs):
        """Build arguments."""

        icon = kwargs.get('icon', None)

        self.gui = bool(kwargs.get('gui', False))
        self.name = name
        self.clean = bool(kwargs.get('clean', False))
        self.icon = abspath(icon) if icon is not None else icon
        self.script = script
        self.extension = kwargs.get('ext', '')
        self.portable = kwargs.get('portable', False)


class BuildParams(object):

    """Build parametes."""

    python_bin_path = None
    python_executable = None
    pyinstaller_script = None
    out_dir = None
    script = None
    dist_path = None
    name = None
    clean = None
    extension = None
    icon = None
    portable = None
    spec_path = None


def parse_settings(args, obj):
    """Configure build parameters based on arguments."""

    err = False

    script_path = dirname(abspath(sys.argv[0]))
    obj.python_bin_path = dirname(sys.executable)
    obj.python_bin = sys.executable
    obj.pyinstaller_script = join(script_path, "pyinstaller", "pyinstaller.py")
    obj.out_dir = join(script_path, "build")
    obj.dist_path = join(script_path, "dist")
    obj.name = args.name
    obj.extension = args.extension
    obj.script = path.abspath(path.normpath(args.script))
    obj.icon = args.icon
    obj.clean = args.clean
    obj.portable = args.portable
    obj.spec = path.join(path.dirname(obj.script), '%s.spec' % obj.name)

    if not path.exists(obj.script):
        print("Could not find %s!" % obj.script)
        err = True
    elif args.icon is not None and not path.exists(args.icon):
        print("Could not find %s!" % obj.icon)
        err = True
    elif obj.pyinstaller_script is None or not path.exists(obj.pyinstaller_script):
        print("Could not find pyinstaller.py!")
        err |= True

    if not path.exists(obj.out_dir):
        err |= create_dir(obj.out_dir)
    elif not path.isdir(obj.out_dir):
        print("%s is not a directory!" % obj.out_dir)
        err |= True

    # Get executable name to build
    if not err:
        obj.app = path.join(obj.dist_path, obj.name) + obj.extension
    return err


def create_dir(directory):
    """Create build directory."""

    err = False
    try:
        print("Creating %s..." % directory)
        mkdir(directory)
    except:
        print("Could not create %s!" % directory)
        err = True
    return err


def clean_build(build_dir):
    """Clean the build directory."""

    err = False
    try:
        print("Cleaning %s..." % build_dir)
        shutil.rmtree(build_dir)
    except:
        print("Failed to clean %s!" % build_dir)
        err = True
    return err


def parse_options(args, obj):
    """Parse the build parameters and build the pyinstaller build command."""

    err = False

    # Parse Settings file
    if not err:
        err = parse_settings(args, obj)

    # See if cleaning is required
    if not err and args.clean and path.exists(obj.out_dir):
        err = clean_build(obj.out_dir)

    if not err:
        build_spec_file(obj, args.gui)

    # Construct build params for build processs
    if not err:
        obj.params = (
            [("python" if obj.portable else obj.python_bin), obj.pyinstaller_script, '-F'] +
            (['--clean'] if args.clean is not None else []) +
            (['-w', '--workpath=%s' % obj.out_dir] if args.gui else ['--workpath=%s' % obj.out_dir]) +
            ['--distpath=%s' % obj.dist_path] +
            ['-y', obj.spec]
            # ['--log-level=DEBUG']
        )
    return err


def build(obj):
    """Launch the build process."""

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

    for line in iter(process.stdout.readline, b''):
        sys.stdout.write(line.decode('utf-8') if PY3 else line)
    process.communicate()

    # Check for bad error code
    if process.returncode:
        print("Compilation failed!")
        err = True

    return err


def main():
    """Setup the build process and initiate it."""

    parser = argparse.ArgumentParser(prog='Build', description='Python script for building apps for Pyinstaller')
    # Flag arguments
    parser.add_argument('--version', action='version', version='%(prog)s 1.0.0')
    parser.add_argument('--clean', '-c', action='store_true', default=False, help='Clean build before re-building.')
    parser.add_argument('--gui', '-g', action='store_true', default=True, help='GUI app')
    parser.add_argument(
        '--portable', '-p',
        action='store_true', default=False,
        help='Build with portable python (windows)'
    )
    # parser.add_argument('--icon', '-i', default=None, nargs="?", help='App icon')
    parser.add_argument('--script', default="Rummage.py", help='Main script')
    parser.add_argument('--name', default="Rummage", help='Name of app')
    inputs = parser.parse_args()
    if _PLATFORM == "windows":
        args = Args(
            inputs.script, inputs.name, gui=inputs.gui, clean=inputs.clean,
            ext=".exe", icon=path.abspath("_icons\\rummage.ico"), portable=inputs.portable
        )
    elif _PLATFORM == "osx":
        args = Args(
            inputs.script, inputs.name, gui=inputs.gui, clean=inputs.clean,
            ext='', icon=path.abspath("_icons/rummage.icns")
        )
    else:
        args = Args(
            inputs.script, inputs.name, gui=inputs.gui, clean=inputs.clean,
            ext='', icon=inputs.icon
            # imports=[
            #     "gobject", "glib", "glib._glib", "glib.option", "object.constants",
            #     "gobject._gobject", "gobject.propertyhelper", "gtk", "gtk._gtk"
            # ]
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
