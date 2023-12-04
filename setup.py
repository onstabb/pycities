# -*- coding: utf-8 -*-
from pathlib import Path
from setuptools import setup, find_packages


setup(
    name="pycities",
    version="0.1.3",
    description="A lightweight local city database library in Python with multilanguage support.",
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    author="Vladyslav Kliuchko",
    author_email="kliuchkovladyslav@gmail.com",
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent"
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=find_packages(exclude=("tests", "examples")),
    include_package_data=True,
    tests_require=['pytest~=7.4.3'],
    test_suite='tests',
)
