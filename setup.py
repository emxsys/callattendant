#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  setup.py
#
#  Copyright 2020 Bruce Schubert <bruce@emxsys.com>

import setuptools

# load the long_description from the README
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="callattendant-emxsys", # Replace with your own username
    version="0.5.0",
    author="Bruce Schubert",
    author_email="bruce@emxsys.com",
    description="Automated call attendant and call blocker using a Raspberry Pi and USR-5637 modem",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/emxsys/callattendant",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Environment :: Other Environment",
        "Development Status :: 4 - Beta",
        "Framework :: Flask",
        "Topic :: Communications :: Telephony",
        "Topic :: Home Automation"
    ],
    python_requires='>=3.5',
)
