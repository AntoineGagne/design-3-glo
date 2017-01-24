#!/usr/bin/env python

import os
from setuptools import setup


def read(file_name):
    return open(os.path.join(os.path.dirname(__file__), file_name)).read()


setup(
    name='design',
    version='0.0.0.0',
    description='A package for the course *Design III*',
    author=('Antoine Gagne'
            'Nadia Chicoine <nadia.chicoine.2@ulaval.ca>,'
            'Alexandre Tremblay <alexandre.tremblay.18@ulaval.ca>,'
            'Imen Daagi <imen.daagi.1@ulaval.ca>'),
    keywords='robotics numeric vision socket programming',
    author_email='antoine.gagne.2@ulaval.ca',
    url='https://github.com/AntoineGagne/design-3-glo',
    packages=['design'],
    long_description=read('README.md'),
    setup_requires=['pytest-runner', 'flake8'],
    tests_require=['pytest'],
    test_suite='tests'
)
