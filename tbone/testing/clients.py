#!/usr/bin/env python
# encoding: utf-8


import re
import json
from tbone.resources.routers import Router
from . import *


class ResourceTestClient(object):
    '''
    A test client used to perform basic http requests in a test environment on a Resource.
    Initialize with an app-like object and the Resource class being tested
    '''

    def __init__(self, app, resource_class):
        self._app = app
        self._router = Router(name='api')
        self._router.register(resource_class, resource_class.__name__)

    def __del__(self):
        for endpoint in self._router.endpoints():
            self._router.unregister(endpoint)

    def parse_response_data(self, response):
        return json.loads(response.data)

    async def process_request(self, method, url, headers, args, body):
        handler = None
        # match the given url to urls in the router then activate the relevant resource
        for route in self._router.urls_regex():
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
            response = await handler(request)
            return response
        return Response(headers={}, data=None, status=404)


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
