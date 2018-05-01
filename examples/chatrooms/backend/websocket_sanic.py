#!/usr/bin/env python
# encoding: utf-8

import logging
from tbone.dispatch.carriers.sanic_websocket import SanicWebSocketCarrier
from tbone.resources.formatters import JSONFormatter

logger = logging.getLogger(__file__)


def subscribe(request, ws):
    request.app.pubsub.subscribe('resource_get_list', SanicWebSocketCarrier(ws))
    request.app.pubsub.subscribe('resource_create', SanicWebSocketCarrier(ws))
    request.app.pubsub.subscribe('resource_update', SanicWebSocketCarrier(ws))
    request.app.pubsub.subscribe('resource_delete', SanicWebSocketCarrier(ws))


def unsubscribe(request, ws):
    request.app.pubsub.unsubscribe('resource_get_list', SanicWebSocketCarrier(ws))
    request.app.pubsub.unsubscribe('resource_create', SanicWebSocketCarrier(ws))
    request.app.pubsub.unsubscribe('resource_update', SanicWebSocketCarrier(ws))
    request.app.pubsub.unsubscribe('resource_delete', SanicWebSocketCarrier(ws))



async def resource_event_websocket(request, ws):
    waiting = True

    # subscribe(request, ws)
    while waiting:
        # data was received from the client
        data = await ws.recv()
        if data == 'close':
            waiting = False
        else:
            await request.app.multiplexer.dispatch(SanicWebSocketCarrier(ws), data)

    unsubscribe(request, ws)


