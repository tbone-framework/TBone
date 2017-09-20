#!/usr/bin/env python
# encoding: utf-8

from collections import namedtuple


App = namedtuple('Request', 'db')
Request = namedtuple('Request', 'app, method, args, url, headers, body')
Response = namedtuple('Response', 'headers, data, status')

