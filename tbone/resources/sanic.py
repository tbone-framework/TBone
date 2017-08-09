#!/usr/bin/env python
# encoding: utf-8

from sanic import request
from sanic import response

class SanicResource(object):
    def build_response(self, data, status=200):
        return response.text(
            data,
            headers={'Content-Type': 'application/json'},
            status=status
        )

    async def request_body(self):
        ''' Returns the body of the current request. '''
        return self.request.body

    def request_args(self):
        ''' Returns the url arguments of the current request'''
        return self.request.args

    @classmethod
    def route_methods(cls):
        '''
        Returns the relevant representation of allowed HTTP methods for a given route.
        Implemented on the http library resource sub-class to match the requirements of the HTTP library
        '''
        return ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']
