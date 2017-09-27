#!/usr/bin/env python
# encoding: utf-8


import asyncio
from bson.json_util import loads
from tbone.db import connect, _get_client
from tbone.db.models import create_app_collections
from app import db_config
from models import *


async def bootstrap_db():
    print('Initializing DB...')
    client = _get_client(**db_config)
    client.drop_database('weblog')

    db = connect(**db_config)
    print ('Creating collections and indices....')
    await create_app_collections(db)
    print('Loading fixture...')

    with open('./data.json') as data_file:
        data = loads(data_file.read())
        await db['entry'].insert_many(data)

    print('Done')



def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(bootstrap_db())
    loop.close()


if __name__ == "__main__":
    main()
