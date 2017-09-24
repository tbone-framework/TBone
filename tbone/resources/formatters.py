#!/usr/bin/env python
# encoding: utf-8


import json
from tbone.utils import ExtendedJSONEncoder


class Formatter(object):
    ''' Base class for all serializers '''
    def parse(self, body):
        raise NotImplementedError()

    def format(self, data):
        raise NotImplementedError()


class JSONFormatter(Formatter):
    ''' Implements JSON serialization '''
    def parse(self, body):
        if isinstance(body, bytes):
            return json.loads(body.decode('utf-8'))
        return json.loads(body)

    def format(self, data):
        return json.dumps(data, cls=ExtendedJSONEncoder)
