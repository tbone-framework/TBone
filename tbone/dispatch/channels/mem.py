#!/usr/bin/env python
# encoding: utf-8

import asyncio
from . import Channel


class MemoryChannel(Channel):
    def __init__(self, **kwargs):
        self._queue = asyncio.Queue()

    async def publish(self, key, data=None):
        document = {
            'key': key,
            'data': data
        }
        await self._queue.put(document)
        return data


    async def consume_events(self):
        while True:
            data = await self._queue.get()
            print('Do your thing with the data', data)