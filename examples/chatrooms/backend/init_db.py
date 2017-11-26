#!/usr/bin/env python
# encoding: utf-8


import asyncio
from bson.json_util import loads
from tbone.db import connect, _get_client
from tbone.db.models import create_collection
from app_sanic import db_config
from models import *


async def bootstrap_db():
    print('Initializing DB...')
    client = _get_client(**db_config)
    client.drop_database('chatrooms')

    db = connect(**db_config)
    print ('Creating collections and indices....')
    
    futures = []
    for model_class in [User, Room, Entry]:
        futures.append(create_collection(db, model_class))

    await asyncio.gather(*futures)
    print('Done')



def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(bootstrap_db())
    loop.close()


if __name__ == "__main__":
    main()
