#!/usr/bin/env python
# encoding: utf-8


import pytest
from tbone.dispatch.channels.mem import MemoryChannel
from tbone.testing.fixtures import event_loop


@pytest.mark.asyncio
async def test_memory_channel(event_loop):
    
    channel = MemoryChannel(name='pubsub')

    await channel.publish('some_event', {'name': 'ron burgundy'})
