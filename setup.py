#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup package."""
from setuptools import setup, find_packages
from setuptools.command.sdist import sdist
from setuptools.command.build_py import build_py
import sys
import os
import importlib.util


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
        """Run the `sdist` build process."""

        self._clean_mo_files("rummage/lib/gui/localization/locale")
        sdist.run(self)


def get_version():
    """Get `__version__` and `__version_info__` without importing the entire module."""

    path = os.path.join(os.path.dirname(__file__), 'rummage', 'lib', '__meta__.py')
    spec = importlib.util.spec_from_file_location("__meta__", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    vi = module.__version_info__
    return vi._get_canonical(), vi._get_dev_status()


def get_requirements(req):
    """Load list of dependencies."""

    install_requires = []
    with open(req) as f:
        for line in f:
            if not line.startswith("#"):
                install_requires.append(line.strip())
    return install_requires


def get_description():
    """Get long description."""

    with open("README.md", 'r') as f:
        desc = f.read()
    return desc


VER, DEVSTATUS = get_version()

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
    python_requires=">=3.5",
    version=VER,
    keywords='grep search find replace gui',
    description='A GUI search and replace app.',
    long_description=get_description(),
    long_description_content_type='text/markdown',
    author='Isaac Muse',
    author_email='Isaac.Muse@gmail.com',
    url='https://github.com/facelessuser/Rummage',
    packages=find_packages(exclude=['tests', 'tools']),
    setup_requires=get_requirements("requirements/setup.txt"),
    install_requires=get_requirements("requirements/project.txt"),
    extras_require={
        'extras': get_requirements("requirements/extras.txt")
    },
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
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
