#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  __main__.py
#
#  Copyright 2020 Bruce Schubert <bruce@emxsys.com>

import os
import sys


def main():

    # Ensure the top-level package is on the path
    currentdir = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(currentdir)

    # Launch the app with the command line args.
    from app import main
    sys.exit(main(sys.argv))


if __name__ == '__main__':

    sys.exit(main())
