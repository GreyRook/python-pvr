# -*- coding: utf-8 -*-
import os
import sys

from distutils.command.sdist import sdist
from setuptools import setup, find_packages
import setuptools.command.test

BASE_PATH = os.path.abspath(os.path.dirname(__file__))
version_suffix = ''


class TestCommand(setuptools.command.test.test):
    def finalize_options(self):
        setuptools.command.test.test.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        fails = []
        from tox.config import parseconfig
        from tox.session import Session

        config = parseconfig(self.test_args)
        retcode = Session(config).runcommand()
        if retcode != 0:
            fails.append('tox returned errors')

        import pep8
        style_guide = pep8.StyleGuide(config_file=BASE_PATH + '/.pep8')
        style_guide.input_dir(BASE_PATH + '/rw')
        if style_guide.options.report.get_count() != 0:
            fails.append('pep8 returned errros for rw/')

        style_guide = pep8.StyleGuide(config_file=BASE_PATH + '/.pep8')
        style_guide.input_dir(BASE_PATH + '/test')
        if style_guide.options.report.get_count() != 0:
            fails.append('pep8 returned errros for test/')

        if fails:
            print('\n'.join(fails))
            sys.exit(1)


setup(
    name="pvr",
    version="0.0.0",
    url='https://github.com/GreyRook/python-pvr',
    description='utilities to work with PVR images',
    author='Florian Ludwig',
    author_email='f.ludwig@greyrook.com',
    install_requires=['Pillow',
                      'bitstring',
                      ],
    extras_requires={
        'test': ['tox', 'pytest', 'pep8'],
        'docs': ['sphinx_rtd_theme']
    },
    packages=find_packages(exclude=['*.test', '*.test.*']),
    include_package_data=True,
    package_data={
    },
    entry_points={
        'console_scripts': [
            'pvrutil = pvr.cli:main',
        ],
    },
    cmdclass={
        'test': TestCommand
    },
    license="http://www.apache.org/licenses/LICENSE-2.0",
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
