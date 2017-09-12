#!/usr/bin/env python
# encoding: utf-8

from sanic import Sanic
from tbone.db import connect
from routes import routes


db_config = {
    'host': '127.0.0.1',
    'port': 27017,
    'name': 'weblog',
    'username': '',
    'password': '',
    'extra': '',
    'connection_retries': 5,
    'reconnect_timeout': 2,  # in seconds
}


app = Sanic()


# create DB connection with the event loop created by the sanic app
@app.listener('after_server_start')
async def connect_to_db(app, loop):
    db = connect(loop=loop, **db_config)
    if db:
        setattr(app, 'db', db)

for route in routes:
    app.add_route(
        methods=route.methods,
        uri=route.path,
        handler=route.handler
    ) 


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
