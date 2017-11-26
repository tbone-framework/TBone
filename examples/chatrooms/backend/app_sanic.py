#!/usr/bin/env python
# encoding: utf-8

import logging
import sys
from sanic import Sanic
from tbone.db import connect
from tbone.dispatch.channels.mongo import MongoChannel
from tbone.dispatch.multiplexer import WebsocketMultiplexer
from routes import chatrooms_router
from websocket_sanic import resource_event_websocket


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

root = logging.getLogger()
root.setLevel(logging.INFO)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)


CORS_ALLOW_ORIGIN = '*'
CORS_ALLOW_METHODS = ['POST', 'GET', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']
CORS_ALLOW_HEADERS = ['content-type', 'authorization']
CORS_ALLOW_CREDENTIALS = True


app = Sanic()


@app.middleware('response')
async def cors(request, response):
    if response:
        response.headers['Access-Control-Allow-Origin'] = CORS_ALLOW_ORIGIN
        response.headers['Access-Control-Allow-Methods'] = ','.join(CORS_ALLOW_METHODS)
        response.headers['Access-Control-Allow-Headers'] = ','.join(CORS_ALLOW_HEADERS)
        response.headers['Access-Control-Allow-Credentials'] = 'true' if CORS_ALLOW_CREDENTIALS else 'false'



# create DB connection with the event loop created by the sanic app
@app.listener('after_server_start')
async def startup_stuff(app, loop):
    db = connect(loop=loop, **db_config)
    if db:
        setattr(app, 'db', db)
        # create channel for websocket subscribers
        app.pubsub = MongoChannel(name='pubsub', db=db)
        app.pubsub.kickoff()
        # create websocket multiplexer
        app.multiplexer = WebsocketMultiplexer(app)
        app.multiplexer.add_router('chatrooms', chatrooms_router)


for route in chatrooms_router.urls():
    app.add_route(
        methods=route.methods,
        uri=route.path,
        handler=route.handler
    )
# add route for websockets
app.add_websocket_route(uri='/ws/', handler=resource_event_websocket)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
