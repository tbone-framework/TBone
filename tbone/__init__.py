#!/usr/bin/env python
# encoding: utf-8

VERSION = (0, 5, 0, 4)

__short_version__ = '.'.join(map(str, VERSION[0:2]))
__version__ = ''.join(['.'.join(map(str, VERSION[0:4])), ''.join(VERSION[4:])])
