#!/usr/bin/env python
# encoding: utf-8


from aiohttp.web import Response


class AioHttpResource(object):
    def build_response(self, data, status=200):
        res = Response(status=status, text=data, content_type='application/json')
        return res

    async def request_body(self):
        ''' Returns the body of the current request. '''
        if self.request.has_body:
            return await self.request.text()
        return {}



