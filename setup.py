#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from setuptools import setup, Extension, find_packages


def setup_package():
    buffer_server_ext = Extension('sound_sync/buffer_server',
                                  sources=list(map(lambda filename: os.path.join("buffer_server/src/", filename), ['python.cpp', 'handler.cpp', 'buffer_list.cpp', 'server.cpp'])),
                                  libraries=['boost_python-py34', 'boost_system', 'cppcms'],
                                  extra_compile_args=["-std=c++11"])

    needs_pytest = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
    pytest_runner = ['pytest-runner'] if needs_pytest else []
    setup(name="sound_sync",
          version="0.1",
          packages=find_packages(),
          setup_requires=['setuptools>=17.1'] + pytest_runner,
          ext_modules=[buffer_server_ext],
          tests_require=['nose', 'mock'],
          test_suite="nose.collector",
          )


if __name__ == "__main__":
    setup_package()
