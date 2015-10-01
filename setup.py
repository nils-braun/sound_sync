#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Setup file for sound_sync.

    This file was generated with PyScaffold 2.3, a tool that easily
    puts up a scaffold for your new Python project. Learn more under:
    http://pyscaffold.readthedocs.org/
"""

import sys
from setuptools import setup, Extension


def setup_package():
    buffer_server_ext = Extension('sound_sync/buffer_server', 
                                  ['buffer_server/src/handler.cpp'], 
                                  libraries=['boost_python', 'boost_system', 'cppcms'], 
                                  extra_compile_args=["-std=c++11"])
    buffer_list_ext = Extension('sound_sync/buffer_list', 
                                  ['buffer_server/src/buffer_list.cpp'], 
                                  libraries=['boost_python', 'boost_system'], 
                                  extra_compile_args=["-std=c++11"])

    needs_pytest = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
    pytest_runner = ['pytest-runner'] if needs_pytest else []
    setup(setup_requires=['six', 'pyscaffold>=2.3rc1,<2.4a0'] + pytest_runner,
          ext_modules=[buffer_server_ext, buffer_list_ext],
          tests_require=['pytest_cov', 'pytest'],
          use_pyscaffold=True)


if __name__ == "__main__":
    setup_package()
