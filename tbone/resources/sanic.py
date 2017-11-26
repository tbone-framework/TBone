#!/usr/bin/env python
# encoding: utf-8

from sanic import response
from .http import HttpResource


class SanicResource(HttpResource):
    '''
    A mixin class for adapting a ``Resource`` class to work with the Sanic webserver
    '''
    @classmethod
    def build_http_response(cls, data, status=200):
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

    @classmethod
    def route_param(cls, param, type=None):
        if type:
            return '<%s:%s>' % (param, type)
        return '<%s>' % param
