#!/usr/bin/env python
# encoding: utf-8


import logging
from aiohttp import web
from tbone.dispatch.carriers.aiohttp_websocket import AioHttpWebSocketCarrier

logger = logging.getLogger(__file__)


class ResourceEventsWebSocketView(web.View):
    async def get(self):
        ws = web.WebSocketResponse()
        await ws.prepare(self.request)

        self.subscribe(self.request, ws)

        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                if msg.data == 'close':
                    await ws.close()
                    self.unsubscribe(self.request, ws)
            elif msg.type == aiohttp.WSMsgType.ERROR:
                logger.error('ws connection closed with exception %s' % ws.exception())

        self.unsubscribe(self.request, ws)
        return ws

    def subscribe(self, request, ws):
        request.app.pubsub.subscribe('resource_get_list', AioHttpWebSocketCarrier(ws))
        request.app.pubsub.subscribe('resource_create', AioHttpWebSocketCarrier(ws))
        request.app.pubsub.subscribe('resource_update', AioHttpWebSocketCarrier(ws))
        request.app.pubsub.subscribe('resource_delete', AioHttpWebSocketCarrier(ws))

    def unsubscribe(self, request, ws):
        request.app.pubsub.unsubscribe('resource_get_list', AioHttpWebSocketCarrier(ws))
        request.app.pubsub.unsubscribe('resource_create', AioHttpWebSocketCarrier(ws))
        request.app.pubsub.unsubscribe('resource_update', AioHttpWebSocketCarrier(ws))
        request.app.pubsub.unsubscribe('resource_delete', AioHttpWebSocketCarrier(ws))
