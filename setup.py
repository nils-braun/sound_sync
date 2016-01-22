#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Setup file for sound_sync.

    This file was generated with PyScaffold 2.3, a tool that easily
    puts up a scaffold for your new Python project. Learn more under:
    http://pyscaffold.readthedocs.org/
"""

import sys
import os
from setuptools import setup, Extension


def setup_package():
    buffer_server_ext = Extension('sound_sync/buffer_server', 
                                  map(lambda filename: os.path.join("buffer_server/src/", filename), ['python.cpp', 'handler.cpp', 'buffer_list.cpp', 'server.cpp']), 
                                  libraries=['boost_python', 'boost_system', 'cppcms'], 
                                  extra_compile_args=["-std=c++11"])

    needs_pytest = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
    pytest_runner = ['pytest-runner'] if needs_pytest else []
    setup(setup_requires=['six', 'pyscaffold>=2.3rc1,<2.4a0'] + pytest_runner,
          ext_modules=[buffer_server_ext],
          tests_require=['pytest_cov', 'pytest>2.8'],
          use_pyscaffold=True)


if __name__ == "__main__":
    setup_package()
