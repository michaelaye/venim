#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))


with open(path.join(here, "README.rst"), encoding="utf-8") as readme_file:
    readme = readme_file.read()

with open(path.join(here, "HISTORY.rst"), encoding="utf-8") as history_file:
    history = history_file.read()

setup(
    name="venim",
    version="0.7.1",
    description="Python tools for Venus Image Analysis",
    long_description=readme + "\n\n" + history,
    long_description_content_type="text/x-rst",
    author="K.-Michael Aye",
    author_email="kmichael.aye@gmail.com",
    url="https://github.com/michaelaye/venim",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.6, <4",
    entry_points={"console_scripts": ["venim=venim.cli:main"]},
    include_package_data=True,
    install_requires=[
        "numpy",
        "pandas",
        "matplotlib",
        "planetarypy",
        "urlpath",
        "astropy",
    ],
    license="MIT license",
    # zip_safe=False,
    keywords="venus images pds data",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
    ],
)
