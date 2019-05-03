#!/usr/bin/env python3
import setuptools


import skeleton


# Set package details
package_name = 'skeleton'
package_description = 'skeleton python C++ extension'
author = 'Stephen Watts'
licence = 'GPLv3'

# Set extension details
source_files = ['src/bindings.cpp', 'src/utils.cpp']
extension = setuptools.Extension(
        '_skeleton',
        source_files,
        extra_compile_args=['-Wno-maybe-uninitialized'])

# Call setup
setuptools.setup(
        name=package_name,
        version=skeleton.__version__,
        licence=licence,
        test_suite='tests',
        ext_modules=[extension],
        packages=setuptools.find_packages(),
        entry_points={
            'console_scripts': ['skeleton=skeleton.__main__:entry'],
            }
        )
