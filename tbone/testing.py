#!/usr/bin/env python
# encoding: utf-8


import re
import json
from functools import partialmethod
from collections import namedtuple
from tbone.resources.routers import Router


App = namedtuple('Request', 'db')
Request = namedtuple('Request', 'app, method, args, url, headers, body')
Response = namedtuple('Response', 'headers, data, status')


class DummyResource(object):
    '''
    Dummy resource mixin to emulate the behavior of an async http library.
    Used for testing without Sanic or Aiohttp
    '''
    def build_response(self, data, status=200):
        return Response(
            data=data,
            headers={'Content-Type': 'application/json'},
            status=status
        )

    async def request_body(self):
        ''' Returns the body of the current request. '''
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


class ResourceTestClient(object):
    '''
    A test client used to perform basic http requests in a test environment on a Resource.
    Initialize with an app-like object and the Resource class being tested
    '''
    def __init__(self, app, resource_class):
        self._app = app
        self._router = Router(name='api')
        self._router.register(resource_class, resource_class.__name__)

    def parse_response_data(self, response):
        return json.loads(response.data)

    async def process_request(self, method, url, headers, args, body):
        hander = None
        # match the given url to urls in the router then activate the relevant resource 
        for route in self._router.urls2():
            match = re.match(route.path, url)
            if match:
                handler = route.handler
                args.update(match.groupdict())
                break
        if handler:
            # create dummy request object
            request = Request(
                app=self._app,
                method=method,
                url=url,
                args=args,
                headers=headers,
                body=body
            )
            return await handler(request)
        return Response({
            'status': 404  # not found
        })

    async def get(self, url, headers={}, args={}, body={}):
        return await self.process_request('GET', url, headers, args, body)

    async def post(self, url, headers={}, args={}, body={}):
        return await self.process_request('POST', url, headers, args, body)

    async def put(self, url, headers={}, args={}, body={}):
        return await self.process_request('PUT', url, headers, args, body)

    async def delete(self, url, headers={}, args={}, body={}):
        return await self.process_request('DELETE', url, headers, args, body)

    async def patch(self, url, headers={}, args={}, body={}):
        return await self.process_request('PATCH', url, headers, args, body)

    async def options(self, url, headers={}, args={}, body={}):
        return await self.process_request('OPTIONS', url, headers, args, body)

    async def head(self, url, headers={}, args={}, body={}):
        return await self.process_request('HEAD', url, headers, args, body)

