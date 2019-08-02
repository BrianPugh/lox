#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

import os, sys
from setuptools import setup, find_packages
from setuptools.command.install import install

version='0.6.1'

class VerifyVersionCommand(install):
    """Custom command to verify that the git tag matches our version

    https://circleci.com/blog/continuously-deploying-python-packages-to-pypi-with-circleci/
    """

    description = 'verify that the git tag matches our version'

    def run(self):
        tag = os.getenv('CIRCLE_TAG')

        if tag != 'v'+version:
            info = "Git tag: \"{0}\" does not match the version of this app: \"{1}\"".format(
                tag, version
            )
            sys.exit(info)

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest', ]

setup(
    author="Brian Pugh",
    author_email='bnp117@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Threading and Multiprocessing for every project.",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    long_description_content_type='text/x-rst',
    include_package_data=True,
    keywords='lox',
    name='lox',
    packages=find_packages(include=['lox']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/BrianPugh/lox',
    version=version,
    zip_safe=False,
    cmdclass={
        'verify': VerifyVersionCommand,
    }
)
