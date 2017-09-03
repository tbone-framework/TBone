#!/usr/bin/env python
# encoding: utf-8

import asyncio
import pytest
import json
from bson.json_util import loads
from pymongo.errors import ConnectionFailure
from motor.motor_asyncio import AsyncIOMotorClient


@pytest.fixture(scope='session')
def event_loop():
    '''
    Fixture for creating a single event loop for the entire test loop
    '''
    return asyncio.new_event_loop()


@pytest.fixture(scope='function')
def json_fixture():
    '''
    Fixture for loading json fixture files
    '''
    def _method(filename):
        with open('tests/fixtures/{}'.format(filename)) as data_file:
            data = loads(data_file.read())
        return data
    return _method


@pytest.fixture(scope='module')
def create_database(request, event_loop):
    '''
    Fixture for creating a mongodb database before all tests are run in the db module
    '''
    client = AsyncIOMotorClient(io_loop=event_loop)
    db = client.get_database('test_db')

    def teardown():
        client.drop_database(db)

    request.addfinalizer(teardown)
    return db


@pytest.mark.asyncio
@pytest.fixture(scope='function')
async def db(request, create_database):
    '''
    Clears the database before every test so all tests start in a known db state
    '''
    colls = await create_database.collection_names()
    for coll in colls:
        await create_database.drop_collection(coll)
    return create_database
