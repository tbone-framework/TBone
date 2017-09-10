#!/usr/bin/env python
# encoding: utf-8


import datetime
import asyncio
from bson.objectid import ObjectId
from collections import defaultdict, OrderedDict
from pymongo import CursorType


class Channel(object):
    _collection_prefix = 'tbone_channel_'
    _events = OrderedDict()

    def __init__(self, name):
        self._name = name
        self.active = True
        self._callbacks = defaultdict(list)  # create a dict of lists of callbacks

    def __repr__(self):  # pragma no cover
        return '<Channel {}>'.format(self.name)

    @property
    def name(self):
        return '{}{}'.format(self._collection_prefix, self._name)

    async def publish(self, key, data=None):
        pass

    def subscribe(self, event, callback):
        pass



class MongoChannel(Channel):
    '''
    Represents a channel for event pub/sub based on a MongoDB capped collection
    '''

    channel_lock = asyncio.Lock()

    def __init__(self, db, name):
        super(MongoChannel, self).__init__(name)
        self._db = db

    def __repr__(self):  # pragma no cover
        return '<Channel {}.{}>'.format(
            self._db.name,
            self.name
        )

    async def create_channel(self, capacity=2**15, message_size=1024):  # default size is 32kb
        with (await MongoChannel.channel_lock):
            if self.name not in (await self._db.collection_names()):
                self.collection = await self._db.create_collection(
                    self.name,
                    size=capacity * message_size,
                    max=capacity,
                    capped=True,
                    autoIndexId=False
                )
            else:
                self.collection = self._db[self.name]

    async def publish(self, key, data=None):
        document = {
            'key': key,
            'data': data
        }
        await self.collection.insert(document, manipulate=False)
        return document

    def subscribe(self, event, callback):
        # if not hasattr(callback, 'channel_callback'):
        #     raise Exception('Callback function is not decorated')
        self._callbacks[event].append(callback)

    def kickoff(self):
        asyncio.ensure_future(self._listen_to_messages())

    async def _listen_to_messages(self):
        ''' begin listening to messages that were entered after starting'''
        # begin by making sure the channel is created
        await self.create_channel()

        # get cursor method
        def create_cursor():
            now = datetime.datetime.utcnow()
            dummy_id = ObjectId.from_datetime(now)
            return self.collection.find({'_id': {'$gte': dummy_id}}, cursor_type=CursorType.TAILABLE_AWAIT)
        # get cursor and start the loop
        cursor = create_cursor()
        while self.active:
            if cursor.alive:
                if (await cursor.fetch_next):
                    message = cursor.next_object()
                    event = message['key']
                    data = message['data']
                    # now what
            else:
                await asyncio.sleep(0.1)
                cursor = create_cursor()


def channel_callback(func):
    '''
    Decorator for callback functions which are passed to the subscribe method of the Channel object.
    Turns the function into a coroutine
    '''
    func = gen.coroutine(func)
    func.channel_callback = True
    return func
