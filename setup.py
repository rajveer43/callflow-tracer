#!/usr/bin/env python3
"""
Setup script for callflow-tracer.
This file provides package configuration for building and installing.
"""

import re
import os
from setuptools import setup, find_packages

def get_version():
    """Get version from __init__.py"""
    version_file = os.path.join('callflow_tracer', '__init__.py')
    with open(version_file, 'r', encoding='utf-8') as f:
        content = f.read()
        version_match = re.search(r'^__version__ = ["\']([^"\']+)["\']',
                                content, re.MULTILINE)
        if version_match:
            return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

# Read the README for long description
try:
    with open('README.md', 'r', encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "A lightweight Python library for tracing function call relationships"

setup(
    name="callflow-tracer",
    version=get_version(),
    author="Rajveer Rathod",
    author_email="rathodrajveer1311@gmail.com",
    description="A lightweight Python library for tracing function call relationships, performance profiling, and visualizing them as interactive graphs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rajveer43/callflow-tracer",
    packages=find_packages(include=['callflow_tracer*']),
    package_data={
        'callflow_tracer': ['templates/*.html'],
    },
    python_requires='>=3.8',  # Required for tracemalloc and cProfile features
    install_requires=[
        'networkx>=2.6',
        'numpy>=1.21.0',  # For array operations in examples
    ],
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov',
            'black',
            'flake8'
        ],
    },
    entry_points={
        'console_scripts': [
            'callflow-tracer=callflow_tracer.cli:main',
            'callflow=callflow_tracer.cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Debugging',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Testing',
        'Topic :: System :: Monitoring',
        'Operating System :: OS Independent'
    ],
)
