#!/usr/bin/env python
# encoding: utf-8

import asyncio
import pytest
from pymongo.errors import ConnectionFailure
from motor.motor_asyncio import AsyncIOMotorClient


@pytest.fixture(scope='session')
def event_loop():
    return asyncio.new_event_loop()


@pytest.fixture(scope='module')
def database(request, event_loop):
    print('initialize database')
    conn = AsyncIOMotorClient(io_loop=event_loop)
    db  = conn.get_database('test_db')

    def teardown():
        print("drop database")
        conn.drop_database(db)

    request.addfinalizer(teardown)
    return db
