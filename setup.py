#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages
import requirements

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

setup_requirements = []
with open('requirements/prod.txt', 'r') as fd:
    for req in requirements.parse(fd):
        setup_requirements.append(req.name)

test_requirements = []
with open('requirements/test.txt', 'r') as fd:
    for req in requirements.parse(fd):
        test_requirements.append(req.name)

setup(
    name='venim',
    version='0.1.0',
    description="Python tools for Venus Image Analysis",
    long_description=readme + '\n\n' + history,
    author="K.-Michael Aye",
    author_email='kmichael.aye@gmail.com',
    url='https://github.com/michaelaye/venim',
    packages=find_packages(include=['venim']),
    entry_points={
        'console_scripts': [
            'venim=venim.cli:main'
        ]
    },
    package_dir={'venim':
                 'venim'},
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='venim',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
