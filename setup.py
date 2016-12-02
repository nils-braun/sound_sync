#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from setuptools import setup, find_packages


def setup_package():
    needs_pytest = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
    pytest_runner = ['pytest-runner'] if needs_pytest else []
    setup(name="sound_sync",
          version="0.1",
          packages=find_packages(),
          setup_requires=['setuptools>=17.1'] + pytest_runner,
          tests_require=['pytest', 'mock', 'pytest-cov', 'coverage'],
          )


if __name__ == "__main__":
    setup_package()
