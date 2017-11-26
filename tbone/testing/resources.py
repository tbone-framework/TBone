#!/usr/bin/env python
# encoding: utf-8


import json
from . import *


class DummyResource(object):
    '''
    Dummy resource mixin to emulate the behavior of an async http library.
    Used for testing without Sanic or Aiohttp
    '''
    @classmethod
    def build_http_response(cls, data, status=200):
        return Response(
            data=data,
            headers={'Content-Type': 'application/json'},
            status=status
        )

    async def request_body(self):
        '''
        Returns the body of the current request.
        The resource expects a text-formatted body
        '''
        if isinstance(self.request.body, dict):
            return json.dumps(self.request.body)
        return self.request.body

    def request_args(self):
        ''' Returns the url arguments of the current request'''
        return self.request.args

    @classmethod
    def route_methods(cls):
        '''
        Returns the relevant representation of allowed HTTP methods for a given route.
        '''
        return '*'
