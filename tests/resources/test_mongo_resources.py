#!/usr/bin/env python
# encoding: utf-8

import asyncio
import pytest
import re
import random
from tbone.testing import *
from .resources import *
from tests.fixtures import *


@pytest.mark.asyncio
@pytest.fixture(scope='function')
async def load_account_collection(json_fixture, db):
    ''' Helper fixture for loading the accounts.json fixture into the database '''
    app = App(db=db)
    url = '/api/'

    # load data
    data = json_fixture('accounts.json')
    # create collection in db
    coll_name = AccountResource._meta.object_class.get_collection()
    coll = await db.create_collection(coll_name)
    # insert raw data into collection
    await coll.insert_many(data)
    return app


@pytest.mark.asyncio
async def test_mongo_collection_pagination_and_sorting(load_account_collection):
    app = load_account_collection
    # create client
    url = '/api/{}/'.format(AccountResource.__name__)
    client = ResourceTestClient(app, AccountResource)
    # get accounts - 0 offset
    response = await client.get(url)
    # make sure we got a response object
    assert isinstance(response, Response)
    # parse response and retrieve data
    page1 = client.parse_response_data(response)
    assert 'meta' in page1
    assert 'objects' in page1
    assert len(page1['objects']) == LIMIT
    assert 'total_count' in page1['meta']
    assert page1['meta']['offset'] == 0

    # get accounts - 10 offset
    response = await client.get(url, args={'offset': 10})
    # make sure we got a response object
    assert isinstance(response, Response)
    # parse response and retrieve data
    page2 = client.parse_response_data(response)
    assert 'meta' in page2
    assert 'objects' in page2
    assert len(page2['objects']) == LIMIT
    assert 'total_count' in page2['meta']
    assert page2['meta']['offset'] == 10
    # very offset is correct with objects
    assert page1['objects'][10] == page2['objects'][0]
    with pytest.raises(AssertionError):
        assert page1['objects'][0] == page2['objects'][0]

    # test sorting
    response = await client.get(url, args={'order_by': 'password'})  # arbitrary field sorting
    # make sure we got a response object
    assert isinstance(response, Response)
    # parse response and retrieve data
    page3 = client.parse_response_data(response)
    assert page3['meta']['offset'] == 0

    # make sure the first object in both collections are not identical
    with pytest.raises(AssertionError):
        assert page1['objects'][0] == page3['objects'][0]


@pytest.mark.asyncio
async def test_mongo_collection_with_resource_defined_query(load_account_collection):

    class PremiumAccountResource(AccountResource):
        ''' Derived account resource limited only to premium accounts '''
        class Meta(AccountResource.Meta):
            query = {'premium': True}

    app = load_account_collection
    # create client
    url = '/api/{}/'.format(PremiumAccountResource  .__name__)
    client = ResourceTestClient(app, PremiumAccountResource)

    # get all premium accounts
    response = await client.get(url, args={'limit': '0'})
    # make sure we got a response object
    assert isinstance(response, Response)
    # parse response and retrieve data
    data = client.parse_response_data(response)
    for account in data['objects']:
        assert account['premium'] is True


@pytest.mark.asyncio
async def test_mongo_collection_filtering_simple(load_account_collection):
    app = load_account_collection
    # create client
    url = '/api/{}/'.format(AccountResource.__name__)
    client = ResourceTestClient(app, AccountResource)
    # get all accounts
    response = await client.get(url)
    # make sure we got a response object
    assert isinstance(response, Response)
    # parse response and retrieve data
    data = client.parse_response_data(response)
    total_count = data['meta']['total_count']
    # get only accounts which are designated Male gender
    response = await client.get(url, args={'gender': 'Male'})
    # parse response and retrieve data
    data = client.parse_response_data(response)
    male_count = data['meta']['total_count']

    # get only accounts which are designated Female gender
    response = await client.get(url, args={'gender': 'Female'})
    # parse response and retrieve data
    data = client.parse_response_data(response)
    female_count = data['meta']['total_count']
    assert female_count + male_count <= total_count


@pytest.mark.asyncio
async def test_mongo_collection_filtering_operator(load_account_collection):
    app = load_account_collection
    # create client
    url = '/api/{}/'.format(AccountResource.__name__)
    client = ResourceTestClient(app, AccountResource)
    # get all accounts
    response = await client.get(url)
    # make sure we got a response object
    assert isinstance(response, Response)
    # parse response and retrieve data
    data = client.parse_response_data(response)
    total_count = data['meta']['total_count']
    # get only accounts which are designated Male gender
    response = await client.get(url, args={'gender': 'Male'})
    # parse response and retrieve data
    data = client.parse_response_data(response)
    male_count = data['meta']['total_count']

    # get only accounts which are designated Female gender
    response = await client.get(url, args={'gender': 'Female'})
    # parse response and retrieve data
    data = client.parse_response_data(response)
    female_count = data['meta']['total_count']
    assert female_count + male_count <= total_count

