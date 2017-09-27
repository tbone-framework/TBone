#!/usr/bin/env python
# encoding: utf-8

import pytest
from tbone.testing.fixtures import *
from models import *


@pytest.mark.asyncio
async def test_room_model(request, db):
    # create owner
    owner = User({
        'username': 'rburgundy',
        'first_name': 'Ron',
        'last_name': 'Burgundy'
    })
    await owner.save(db)
    # create room with assigned owner
    room = Room({
        'name': 'Channel 4',
        'title': 'All the latest news',
        'owner': owner
    })
    await room.save(db)
    # create memebers
    mem1 = User({
        'username': 'bfan',
        'first_name': 'Brian',
        'last_name': 'Fantana'
    })
    mem2 = User({
        'username': 'champ',
        'first_name': 'Champion',
        'last_name': 'Kind'
    })
    mem3 = User({
        'username': 'brick',
        'first_name': 'Brick',
        'last_name': 'Tamland'
    })
    futures = []
    futures.append(mem1.save(db))
    futures.append(mem2.save(db))
    futures.append(mem3.save(db))
    await asyncio.gather(*futures)
    
    # add users as memebers to room
    futures = []
    futures.append(room.add_member(db, mem1))
    futures.append(room.add_member(db, mem2))
    futures.append(room.add_member(db, mem3))
    await asyncio.gather(*futures)

    # add existing user as member to room - this should be ignored as this user already exists
    await room.add_member(db, mem1)

    same_room = await Room.find_one(db, {'_id': room._id})
    assert same_room.owner == room.owner
    assert len(same_room.members) == 3


