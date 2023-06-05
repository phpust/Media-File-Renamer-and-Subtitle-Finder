#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: fenc=utf-8 ts=4 et sw=4 sts=4

# This file is part of Media File Renamer and Subtitle Finder.
#
# Media File Renamer and Subtitle Finder is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Media File Renamer and Subtitle Finder is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
setup for Media File Renamer and Subtitle Finder
"""

from setuptools import setup, find_packages

description = readme = 'python scrapper for renaming movies and finding subtitles.'
requirements = []
try:
    with open('README','r') as f:
        readme = f.read()
    with open('requirements.txt') as f:
        requirements = f.read().splitlines()
except Exception:
    pass

setup(
    name='Media-File-Renamer-and-Subtitle-Finder',
    version='1.0.0',
    description=description,
    long_description=readme,
    author='Seyyed Sajjad Kashizadeh',
    author_email='s.kashizadeh@gmail.com',
    url='https://github.com/phpust/Media-File-Renamer-and-Subtitle-Finder',
    license='GNU General Public License v3 or later',
    keywords = 'subf2m scrapper file-renamer python3',
    install_requires=requirements,
    packages=['subf2m'],
    classifiers = [
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Topic :: Software Development',
        'Topic :: Internet :: WWW/HTTP',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Development Status :: 5 - Production/Stable'
        ]
)

