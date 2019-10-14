import pathlib, os, sys

import setuptools
from setuptools import Command, setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="enviroMS",
    version="1.0.a0",
    description="Search and Assign Molecular Formulas for Small Molecules ",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://gitlab.pnnl.gov/corilo/enviroms/",
    author="Corilo, Yuri",
    author_email="corilo@pnnl.gov",
    license="GNU Affero General Public License v3.0",
    classifiers=[
        "License ::GNU Affero General Public License v3.0",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],

    install_requires=['Click'],
    entry_points= '''
            [console_scripts]
            enviroMS=cli.enviroMS:cli
            ''',
)
    