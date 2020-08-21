#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  __main__.py
#
#  Copyright 2020 Bruce Schubert <bruce@emxsys.com>


if __name__ == '__main__':
    import os
    import sys

    currentdir = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(currentdir)

    from app import main
    sys.exit(main(sys.argv))
