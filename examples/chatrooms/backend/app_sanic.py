#!/usr/bin/env python
# encoding: utf-8

import logging
import sys
from sanic import Sanic
from tbone.db import connect
from tbone.dispatch.channels.mongo import MongoChannel
from routes import routes
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
root.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)



app = Sanic()


# create DB connection with the event loop created by the sanic app
@app.listener('after_server_start')
async def startup_stuff(app, loop):
    db = connect(loop=loop, **db_config)
    if db:
        setattr(app, 'db', db)
        # create channel for websocket subscribers
        app.pubsub = MongoChannel(name='pubsub', db=db)
        app.pubsub.kickoff()


for route in routes:
    app.add_route(
        methods=route.methods,
        uri=route.path,
        handler=route.handler
    )
# add route for websockets
app.add_websocket_route(uri='/ws/', handler=resource_event_websocket)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)