#!/usr/bin/env python
# Copyright (C) 2022 Vincent Russell.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation, version 2.1.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  US

import os

from pssh_cli import version
from setuptools import setup, find_packages

setup(name='parallel-ssh-cli',
      version=version.VERSION,
      description='a cli wrapper around parallel-ssh',
      long_description=open('README.md').read(),
      author='Vincent Russell',
      author_email='vincent.russell@gmail.com',
      url="https://github.com/vincentrussell/parallel-ssh-cli",
      license='LGPLv2.1',
      packages=find_packages(include=['pssh_cli']),
      scripts = [os.path.join("bin", p) for p in ["parallel-ssh"]],
      platforms = ['linux'],
      install_requires=[
          'parallel-ssh>=2.12.0',
          'termcolor>=1.1.0'],
       data_files = [('/usr/share/man/man1', [ 'man/man1/parallel-ssh-cli.1' ])],    
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)',
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Topic :: System :: Networking',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Operating System :: POSIX :: Linux',
          'Operating System :: POSIX :: BSD',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: MacOS :: MacOS X',
      ],
      )
