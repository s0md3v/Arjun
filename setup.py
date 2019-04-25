#!/usr/bin/env python3
"""Arjun setup script."""
import os
import sys

from arjun.const import __version__ as VERSION

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md'), encoding='utf-8') as readme_file:
    long_description = readme_file.read()

if sys.argv[-1] == 'publish':
    os.system('python3 setup.py sdist upload')
    sys.exit()

setup(
    name='arjun',
    version=VERSION,
    description='A HTTP parameter discovery suite',
    long_description=long_description,
    url='https://github.com/s0md3v/Arjun',
    download_url='https://github.com/s0md3v/Arjun/releases',
    author='Somdev Sangwan',
    author_email='s0md3v@gmail.com',
    maintainer='Fabian Affolter',
    maintainer_email='fabian@affolter-engineering.ch',
    install_requires=['requests'],
    packages=['arjun'],
    zip_safe=True,
    entry_points={
        'console_scripts': [
            'arjun = arjun.__main__:main'
        ]
    },
)
