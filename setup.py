import os
import sys

from setuptools import find_packages, setup
from setuptools.command.install import install

version = "1.0.0"


with open("README.rst") as readme_file:
    readme = readme_file.read()
readme = readme.replace(
    "assets/lox_200w.png",
    "https://raw.githubusercontent.com/BrianPugh/lox/main/assets/lox_200w.png",
)

with open("HISTORY.rst") as history_file:
    history = history_file.read()

setup(
    author="Brian Pugh",
    author_email="bnp117@gmail.com",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    description="Threading and Multiprocessing for every project.",
    install_requires=[],
    extras_require={
        "multiprocessing": ["pathos"],
    },
    license="MIT license",
    long_description=readme + "\n\n" + history,
    long_description_content_type="text/x-rst",
    include_package_data=True,
    keywords="lox",
    name="lox",
    packages=find_packages(include=["lox"]),
    test_suite="tests",
    url="https://github.com/BrianPugh/lox",
    version=version,
    zip_safe=False,
)
