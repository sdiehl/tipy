#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='tipy',
    version='0.1.0',
    author='Stephen Diehl',
    author_email='stephen.m.diehl@gmail.com.com',
    description='Python preprocessor',
    packages=find_packages(),
    install_requires=[],
    data_files=[],
    entry_points={
        'console_scripts': [
            'tipy = tipy.pyshell:main',
        ]
    },
)
