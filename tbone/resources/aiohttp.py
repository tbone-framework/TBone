#!/usr/bin/env python
# encoding: utf-8


from aiohttp.web import Response


class AioHttpResource(object):
    '''
    A mixin class for adapting a ``Resource`` class to work with the AioHttp webserver
    '''
    @classmethod
    def build_http_response(cls, data, status=200):
        res = Response(status=status, text=data, content_type='application/json')
        return res

    async def request_body(self):
        ''' Returns the body of the current request. '''
        if self.request.has_body:
            return await self.request.text()
        return {}

    @classmethod
    def route_methods(cls):
        '''
        Returns the relevant representation of allowed HTTP methods for a given route.
        Implemented on the http library resource sub-class to match the requirements of the HTTP library
        '''
        return '*'


    @classmethod
    def route_param(cls, param, type=str):
        return '{%s}' % param

    def request_args(self):
        '''
        Returns the arguments passed with the request in a dictionary.
        Returns both URL resolved arguments and query string arguments.
        '''
        kwargs = {}
        kwargs.update(self.request.match_info.items())
        kwargs.update(self.request.query.items())
        return kwargs


