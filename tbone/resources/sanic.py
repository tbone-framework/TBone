#!/usr/bin/env python
# encoding: utf-8

from sanic import request
from sanic import response

class SanicResource(object):
    def build_response(self, data, status=200):
        return response.json(
            data,
            status=status
        )

    async def request_body(self):
        ''' Returns the body of the current request. '''
        import pdb; pdb.set_trace()
        if self.request.has_body:
            return await self.request.text()
        return {}