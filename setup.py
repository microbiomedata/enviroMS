import pathlib, os, sys

import setuptools
from setuptools import Command, setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="EnviroMS",
    version="4.2.1",
    description="Search and Assign Molecular Formulas for Complex Mixtures of Small Molecules",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/EMSL-Computing/EnviroMS",
    author="Corilo, Yuri",
    author_email="corilo@pnnl.gov",
    py_modules = ['enviroMS'],
    packages = find_packages(),
    license="GNU Affero General Public License v3.0",
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],

    install_requires=['Click', 'tabulate', 'CoreMS', 'requests'],
    entry_points={"console_scripts": ["enviroMS = enviroMS.cli:cli"]},

)
    