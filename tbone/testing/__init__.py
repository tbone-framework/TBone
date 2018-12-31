#!/usr/bin/env python
# encoding: utf-8

from collections import namedtuple


Response = namedtuple('Response', 'headers, payload, status')


class App(object):
    def __init__(self, db=None, **kwargs):
        self.db = db


class Request(dict):
    __slots__ = (
        'app', 'headers', 'method', 'body', 'args', 'url', 'user'
    )

    def __init__(self, app, url, method, headers, args, body):
        self.app = app
        self.method = method
        self.args = args
        self.headers = headers
        self.body = body
        self.args = args




