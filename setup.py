#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os
from setuptools import setup

NAME = 'Spytrack'
DESCRIPTION = 'Automatic time tracker'
URL = 'https://github.com/2e3s/spytrack'
EMAIL = '2e3s19@gmail.com'
AUTHOR = '2e3s'
REQUIRES_PYTHON = '>=3.6.0'
VERSION = '0.0.1'

REQUIRED = [
    'aw-core',
    'aw-client',
    'aw-server',
    'aw-watcher-afk',
    'aw-watcher-window',
    'pyyaml',
    'PyQt5',
    'PyQtChart',
]
REQUIRED_LINKS = [
    'git+https://github.com/ActivityWatch/aw-core@master#egg=aw-core',
    'git+https://github.com/ActivityWatch/aw-client@master#egg=aw-client',
    'git+https://github.com/ActivityWatch/aw-server.git@master#egg=aw-server',
    'git+https://github.com/ActivityWatch/aw-watcher-afk.git@master#egg=aw-watcher-afk',
    'git+https://github.com/ActivityWatch/aw-watcher-window.git@master#egg=aw-watcher-window',
]

EXTRAS = {}

here = os.path.abspath(os.path.dirname(__file__))

try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=['spytrack'],
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    license='COPYING',
    entry_points={
        # "console_scripts": ['spytrack_tray = spytrack.runner'],
        "gui_scripts": ['spytrack = spytrack:main'],
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Topic :: Utilities',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Operating System :: POSIX :: Linux',
        # 'Operating System :: Microsoft :: Windows',
        # 'Operating System :: MacOS',
    ],
)
