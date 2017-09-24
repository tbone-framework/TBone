#!/usr/bin/env python
# encoding: utf-8

import logging
import sys
import asyncio
from aiohttp import web
from tbone.db import connect
from tbone.dispatch.channels.mongo import MongoChannel
from routes import routes
from websocket_aiohttp import *


db_config = {
    'host': '127.0.0.1',
    'port': 27017,
    'name': 'chatrooms',
    'username': '',
    'password': '',
    'extra': '',
    'connection_retries': 5,
    'reconnect_timeout': 2,  # in seconds
}

CORS_ALLOW_ORIGIN = '*'
CORS_ALLOW_METHODS = ['POST', 'GET', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']
CORS_ALLOW_HEADERS = ['content-type', 'authorization']
CORS_ALLOW_CREDENTIALS = True


root = logging.getLogger()
root.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)


async def cors(app, handler):
    async def middleware(request):
        response = await handler(request)
        response.headers['Access-Control-Allow-Origin'] = CORS_ALLOW_ORIGIN
        response.headers['Access-Control-Allow-Methods'] = ','.join(CORS_ALLOW_METHODS)
        response.headers['Access-Control-Allow-Headers'] = ','.join(CORS_ALLOW_HEADERS)
        response.headers['Access-Control-Allow-Credentials'] = 'true' if CORS_ALLOW_CREDENTIALS else 'false'
        return response
    return middleware


def create_app(loop):
    # create web application
    app = web.Application(loop=loop, middlewares=[cors], debug=True)  # middlewares=[database], debug=True)
    # connect database
    db = connect(**db_config)
    if db:
        setattr(app, 'db', db)
    # add routes
    for route in routes:
        app.router.add_route(
            method=route.methods,
            path=route.path,
            handler=route.handler,
            name=route.name
        )
    app.router.add_route(method='*', path='/ws/', handler=ResourceEventsWebSocketView, name='websocket')


    # create channel for websocket subscribers
    app.pubsub = MongoChannel(name='pubsub', db=db)
    app.pubsub.kickoff()

    return app


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    app = create_app(loop=loop)
    web.run_app(app, host='127.0.0.1', port=8000, loop=loop)
