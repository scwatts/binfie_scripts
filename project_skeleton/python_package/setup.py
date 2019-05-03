#!/usr/bin/env python3
import setuptools
import sys


import skeleton


setuptools.setup(
        name='skeleton',
        version=skeleton.__version__,
        description='skeleton python package',
        author='Stephen Watts',
        license='GPLv3',
        test_suite='tests',
        packages=setuptools.find_packages(),
        entry_points={
                'console_scripts': ['skeleton=skeleton.__main__:entry'],
            }
)
