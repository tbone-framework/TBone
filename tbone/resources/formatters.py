#!/usr/bin/env python
# encoding: utf-8


import json
from tbone.utils import ExtendedJSONEncoder


class Formatter(object):
    '''
    Base class for all formatters.
    Subclass this to create custom formatters
    '''
    def parse(self, body):
        '''Parses a string data to python ``dict``. Implement in derived classes for specific transport protocols'''
        raise NotImplementedError()

    def format(self, data:dict):
        '''Formats python ``dict`` into a data string. Implement in derived classes for specific transport protocols'''
        raise NotImplementedError()


class JSONFormatter(Formatter):
    ''' Implements JSON formatting and parsing '''
    def parse(self, body):
        if isinstance(body, bytes):
            return json.loads(body.decode('utf-8'))
        return json.loads(body)

    def format(self, data):
        return json.dumps(data, cls=ExtendedJSONEncoder)
