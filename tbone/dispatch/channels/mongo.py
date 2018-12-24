#!/usr/bin/env python
# encoding: utf-8

import logging
import asyncio
import datetime
import json
from bson.objectid import ObjectId
from pymongo import CursorType
from . import Channel

logger = logging.getLogger(__file__)


class MongoChannel(Channel):
    '''
    Represents a channel for event pub/sub based on a MongoDB capped collection
    '''

    channel_lock = asyncio.Lock()

    def __init__(self, **kwargs):
        self._db = kwargs.get('db', None)
        self._collection = None

    def __repr__(self):  # pragma no cover
        return '<MongoChannel {}.{}>'.format(
            self._db.name,
            self.name
        )

    async def create_channel(self, capacity=2**15, message_size=1024):  # default size is 32kb
        if self._collection:
            return
        with (await MongoChannel.channel_lock):
            if self.name not in (await self._db.list_collection_names()):
                self._collection = await self._db.create_collection(
                    self.name,
                    size=capacity * message_size,
                    max=capacity,
                    capped=True,
                    autoIndexId=False
                )
            else:
                self._collection = self._db[self.name]

    async def publish(self, key, data=None):
        # begin by making sure the channel is created
        await self.create_channel()

        document = {
            'key': key,
            'data': data
        }
        await self._collection.insert(document, manipulate=False)
        return document


    async def consume_events(self):
        ''' begin listening to messages that were entered after starting'''
        # begin by making sure the channel is created
        await self.create_channel()
        # get cursor method
        def create_cursor():
            now = datetime.datetime.utcnow()
            dummy_id = ObjectId.from_datetime(now)
            return self._collection.find({'_id': {'$gte': dummy_id}}, cursor_type=CursorType.TAILABLE_AWAIT)
        # get cursor and start the loop
        cursor = create_cursor()
        while self.active:
            if cursor.alive:
                if (await cursor.fetch_next):
                    message = cursor.next_object()
                    event = message['key']
                    data = message['data']
                    logger.debug('event: %s - %s', event, data)
                    for sub in self._subscribers[event]:
                        await sub.deliver({'type': 'event', 'payload': {'name': event, 'data': data}})
            else:
                await asyncio.sleep(0.1)
                cursor = create_cursor()
