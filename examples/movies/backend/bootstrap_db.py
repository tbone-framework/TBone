#!/usr/bin/env python
# encoding: utf-8


import asyncio
from bson.json_util import loads
from tbone.db import connect, _get_client
from tbone.db.models import create_collections
from app import db_config
from models import *


async def bootstrap_db():
    print('Initializing DB...')
    client = _get_client(**db_config)
    client.drop_database('movies')

    db = connect(**db_config)
    print ('Creating collections and indices....')
    await create_collections(db)
    print('Loading fixture...')

    with open('./data2.json') as data_file:
        data = loads(data_file.read())
        await db['movie'].insert_many(data)

    print('Done')


async def convert():
    db = connect(**db_config)

    cursor = Movie.get_cursor(db=db, query={})
    cursor.skip(0)
    cursor.limit(1000)
    movies = await Movie.find(cursor)
    for movie in movies:
        print(movie.title)
        movie.genres2 = ', '.join(movie.genres)
        await movie.save(db)



def main():
    loop = asyncio.get_event_loop()
    # loop.run_until_complete(convert())
    loop.run_until_complete(bootstrap_db())
    loop.close()


if __name__ == "__main__":
    main()
