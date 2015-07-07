#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup package."""
from setuptools import setup, find_packages
import sys

PY3 = (3, 0) <= sys.version_info < (4, 0)

LONG_DESC = '''
Rummage is a CLI and GUI tool for searching through folders and fle content.
It is built with wxPython 3.0.0+ and requires Python 2.7 or Python 3.0 for command line.

The project repo is found at:
https://github.com/facelessuser/Rummage.
'''

if PY3:
    entry_points = {
        'console_scripts': [
            'rumcl=rummage.cli:main',
            'rumcl%d.%d=rummage.cli:main' % sys.version_info[:2],
        ]
    }
else:
    entry_points = {
        'gui_scripts': [
            'rummage=rummage.__main__:main'
        ],
        'console_scripts': [
            'rumcl=rummage.cli:main',
            'rumcl%d.%d=rummage.cli:main' % sys.version_info[:2],
        ]
    }

setup(
    name='Rummage',
    version='0.3.0',
    keywords='grep search find',
    description='A gui file search app.',
    long_description=LONG_DESC,
    author='Isaac Muse',
    author_email='Isaac.Muse [at] gmail.com',
    url='https://github.com/facelessuser/Rummage',
    packages=find_packages(exclude=[]),
    install_requires=[
        "gntp>=1.0.2",
        "chardet>=2.3.0"
    ],
    zip_safe=False,
    entry_points=entry_points,
    package_data={
        'rummage.rummage.data': ['*.css', '*.js', '*.png', '*.ico', '*.icns']
    },
    license='MIT License',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
