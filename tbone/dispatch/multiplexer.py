#!/usr/bin/env python
# encoding: utf-8

import asyncio
from tbone.resources.formatters import JSONFormatter


def wrap_response(data):
    ''' Passed to the resource dispatch method to wrap the response with websocket meta data'''
    return{
        'type': 'response',
        'payload': data
    }

class WebsocketMultiplexer(object):
    '''
    Creates a single bridge between a websocket handler and one or more resource routers.
    '''

    def __init__(self, app):
        self.app = app
        self.routers = {}
        self.formatter = JSONFormatter()

    def add_router(self, name, router):
        self.routers[name] = router

    def remove_router(self, name):
        del self.routers[name]

    async def dispatch(self, carrier, data):
        # parse the data
        try:
            payload = self.formatter.parse(data)
            # process payload based on the type
            ptype = payload.get('type', None)
            if ptype == 'request':  # send request to all resource routers and pickup one result
                tasks = [router.dispatch(self.app, payload, wrap_response) for router in self.routers.values()]
                results = await asyncio.gather(*tasks)
                # get the response from the one relevant router
                result = next(item for item in results if item is not None)
                await carrier.deliver(result.body)
            elif ptype == 'ping':  # reply directly with pong
                pass
            else:
                pass

        except Exception as ex:
            import pdb; pdb.set_trace()
            print(ex)
