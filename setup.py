#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup package."""
from setuptools import setup, find_packages
from setuptools.command.sdist import sdist
from setuptools.command.build_py import build_py
import sys
import os
import imp
import traceback


class BuildPy(build_py):
    """Custom ``build_py`` command to always build mo files for wheels."""

    def run(self):
        """Run the python build process."""

        self.run_command('compile_catalog')
        build_py.run(self)


class Sdist(sdist):
    """Custom `sdist` command to ensure that we don't include `.m0` files in source."""

    def _clean_mo_files(self, path):
        for root, dirs, files in os.walk(path):
            for f in files:
                if f.lower().endswith('.mo'):
                    os.remove(os.path.join(root, f))

    def run(self):
        """Run the sdist build process."""

        self._clean_mo_files("rummage/lib/gui/localization/locale")
        sdist.run(self)


def get_version():
    """Get version and version_info without importing the entire module."""

    devstatus = {
        'alpha': '3 - Alpha',
        'beta': '4 - Beta',
        'candidate': '4 - Beta',
        'final': '5 - Production/Stable'
    }
    path = os.path.join(os.path.dirname(__file__), 'rummage', 'lib')
    fp, pathname, desc = imp.find_module('__version__', [path])
    try:
        v = imp.load_module('__version__', fp, pathname, desc)
        return v.version, devstatus[v.version_info[3]]
    except Exception:
        print(traceback.format_exc())
    finally:
        fp.close()


def get_requirements(req):
    """Load list of dependencies."""

    install_requires = []
    with open(req) as f:
        for line in f:
            if not line.startswith("#"):
                install_requires.append(line.strip())
    return install_requires


VER, DEVSTATUS = get_version()

LONG_DESC = '''
Rummage is a GUI tool for searching and replacing texst in files.
It is built with wxPython 4.0.0+ and requires Python 2.7 or 3.4+.
You can learn more about using Rummage by `reading the docs`_.

.. _`reading the docs`: http://facelessuser.github.io/Rummage/

Support
=======

Help and support is available here at the repository's `bug tracker`_.
Please read about `support and contributing`_ before creating issues.

.. _`bug tracker`: https://github.com/facelessuser/rummage/issues
.. _`support and contributing`: http://facelessuser.github.io/rummage/contributing/
'''

entry_points = {
    'gui_scripts': [
        'rummage=rummage.__main__:main',
        'rummage%d.%d=rummage.__main__:main' % sys.version_info[:2]
    ]
}

setup(
    name='rummage',
    cmdclass={
        'build_py': BuildPy,
        'sdist': Sdist
    },
    python_requires=">=3.4",
    version=VER,
    keywords='grep search find replace gui',
    description='A GUI search and replace app.',
    long_description=LONG_DESC,
    author='Isaac Muse',
    author_email='Isaac.Muse@gmail.com',
    url='https://github.com/facelessuser/Rummage',
    packages=find_packages(exclude=['tests', 'tools']),
    setup_requires=get_requirements("requirements/setup.txt"),
    install_requires=get_requirements("requirements/project.txt"),
    zip_safe=False,
    entry_points=entry_points,
    include_package_data=True,
    license='MIT License',
    classifiers=[
        'Development Status :: %s' % DEVSTATUS,
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
