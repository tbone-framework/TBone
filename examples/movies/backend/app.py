#!/usr/bin/env python
# encoding: utf-8

import logging
import asyncio
from aiohttp import web
from tbone.db import connect
from tbone.middlewares import database
from routes import routes


db_config = {
    'host': '127.0.0.1',
    'port': 27017,
    'name': 'movies',
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
        print(route)
        app.router.add_route(
            method=route.methods,
            path=route.path,
            handler=route.handler,
            name=route.name
        )

    return app


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    app = create_app(loop=loop)
    web.run_app(app, host='127.0.0.1', port=8000, loop=loop)
