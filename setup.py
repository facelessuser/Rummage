#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup package."""
from setuptools import setup, find_packages
import os
import imp
import traceback


def get_version():
    """Get version and version_info without importing the entire module."""

    devstatus = {
        'alpha': '3 - Alpha',
        'beta': '4 - Beta',
        'candidate': '4 - Beta',
        'final': '5 - Production/Stable'
    }
    path = os.path.join(os.path.dirname(__file__), 'rummage', 'rummage')
    fp, pathname, desc = imp.find_module('__version__', [path])
    try:
        v = imp.load_module('__version__', fp, pathname, desc)
        return v.version, devstatus[v.version_info[3]]
    except Exception:
        print(traceback.format_exc())
    finally:
        fp.close()


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
        'rummage=rummage.__main__:main'
    ]
}

setup(
    name='rummage',
    version=VER,
    keywords='grep search find replace gui',
    description='A GUI search and replace app.',
    long_description=LONG_DESC,
    author='Isaac Muse',
    author_email='Isaac.Muse@gmail.com',
    url='https://github.com/facelessuser/Rummage',
    packages=find_packages(exclude=['tests', 'tools']),
    install_requires=[
        "gntp>=1.0.2",
        "chardet>=3.0.4",
        "backrefs>=1.0.1",
        "regex",
        "wxpython>=4.0.0a3"
    ],
    zip_safe=False,
    entry_points=entry_points,
    package_data={
        'rummage.rummage.data': ['*.css', '*.js', '*.png', '*.ico', '*.icns']
    },
    license='MIT License',
    classifiers=[
        'Development Status :: %s' % DEVSTATUS,
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
