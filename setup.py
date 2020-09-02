#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  setup.py
#
#  Copyright 2020 Bruce Schubert <bruce@emxsys.com>

import os
import setuptools

# load the long_description from the README
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="callattendant",   # Add user name when uploading to TestPyPI
    version="1.0.0",        # Ensure this is in-sync with VERSION in config.py
    author="Bruce Schubert",
    author_email="bruce@emxsys.com",
    description="An automated call attendant and call blocker using a Raspberry Pi and USR-5637 modem",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://emxsys.github.io/callattendant/",
    packages=setuptools.find_packages(exclude=["tests"]),
    include_package_data=True,      # Includes files from MANIFEST.in
    install_requires=[
        "backports.functools-lru-cache>=1.6.1",
        "beautifulsoup4>=4.9.1",
        "bs4>=0.0.1",
        "click>=7.1.2",
        "colorzero>=1.1",
        "Flask>=1.1.2",
        "flask-paginate>=0.6.0",
        "future>=0.18.2",
        "gpiozero>=1.5.1",
        "iso8601>=0.1.12",
        "itsdangerous>=1.1.0",
        "Jinja2>=2.11.2",
        "lxml>=4.5.2",
        "MarkupSafe>=1.1.1",
        "pigpio>=1.46",
        "pygments",
        "pyserial>=3.4",
        "pytest>=6.0.1",
        "PyYAML>=5.3.1",
        "RPi.GPIO>=0.7.0",
        "RPIO>=0.10.0",
        "soupsieve>=1.9.6",
        "Werkzeug>=1.0.1",
    ],
    entry_points={
        "console_scripts": [
            "callattendant = callattendant.__main__:main",
        ]
    },
    scripts=[
        "bin/start-callattendant",
        "bin/stop-callattendant",
        "bin/restart-callattendant",
        "bin/monitor-callattendant",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Environment :: Other Environment",
        "Development Status :: 5 - Production/Stable",
        "Framework :: Flask",
        "Topic :: Communications :: Telephony",
        "Topic :: Home Automation",
    ],
    python_requires='>=3.5',
)
