"""
Module to install the X-Track Engine module that the tool uses to offer its functionalities.
"""

from setuptools import setup, find_packages
from typing import Tuple


def read_requirements(requirements_fname : str = 'requirements.txt') -> Tuple[str, ...]:
    """
    Function to read the requirements file
    """
    with open(requirements_fname) as req:
        return req.read().splitlines()


setup(
    name = 'xtrack_engine',
    version = '1.0.0',
    description = 'The engine that X-TRACK uses to provide its computational capabilities.',
    url = 'https://github.com/paumnz/X-Track/',
    packages = find_packages(include=['xtrack_engine', 'xtrack_engine.*']),
    install_requires=read_requirements(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.11',
)
