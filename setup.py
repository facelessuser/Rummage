#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup package."""
from setuptools import setup, find_packages

LONG_DESC = '''
Rummage is a GUI tool for searching through folders and fle content.
It is built with wxPython 2.9.4 and requires Python 2.7.

The project repo is found at:
https://github.com/facelessuser/Rummage.
'''

setup(
    name='Rummage',
    version='0.3.0',
    keywords='grep search find',
    description='A gui file search app.',
    long_description=LONG_DESC,
    author='Isaac Muse',
    author_email='Isaac.Muse [at] gmail.com',
    url='https://github.com/facelessuser/Rummage',
    packages=find_packages(exclude=['pyinstaller*']),
    install_requires=[
        "gntp>=1.0.2"
    ],
    zip_safe=False,
    entry_points={
        'gui_scripts': [
            'rummage=rummage.rummage:cli'
        ]
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
