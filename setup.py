#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import io
from setuptools import setup, find_packages
from os import path
this_directory = path.abspath(path.dirname(__file__))
with io.open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    desc = f.read()

setup(
    name='arjun',
    version=__import__('arjun').__version__,
    description='HTTP parameter discovery suite',
    long_description=desc,
    long_description_content_type='text/markdown',
    author='Somdev Sangwan',
    author_email='s0md3v@gmail.com',
    license='GNU General Public License v3 (GPLv3)',
    url='https://github.com/s0md3v/Arjun',
    download_url='https://github.com/s0md3v/Arjun/archive/v%s.zip' % __import__('arjun').__version__,
    zip_safe=False,
    packages=find_packages(),
    package_data={'arjun': ['db/*']},
    install_requires=[
        'requests',
        'dicttoxml',
        'ratelimit'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Operating System :: OS Independent',
        'Topic :: Security',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Programming Language :: Python :: 3.4',
    ],
    entry_points={
        'console_scripts': [
            'arjun = arjun.__main__:main'
        ]
    },
    keywords=['arjun', 'bug bounty', 'http', 'pentesting', 'security'],
)
