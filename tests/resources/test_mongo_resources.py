#!/usr/bin/env python
# encoding: utf-8

import asyncio
import pytest
import re
import random
from tbone.db.models import create_collection
from tbone.resources import http
from tbone.testing.clients import *
from tbone.testing.fixtures import *
from .resources import *


@pytest.mark.asyncio
@pytest.fixture(scope='function')
async def load_account_collection(json_fixture, db):
    ''' Helper fixture for loading the accounts.json fixture into the database '''
    app = App(db=db)
    # load data
    data = json_fixture('accounts.json')
    # create collection in db and optional indices
    coll = await create_collection(db, AccountResource._meta.object_class)
    # insert raw data into collection
    if coll:
        await coll.insert_many(data)
    return app


@pytest.mark.asyncio
@pytest.fixture(scope='function')
async def load_book_collection(json_fixture, db):
    ''' Helper fixture for loading the books.json fixture into the database '''
    app = App(db=db)
    # load data
    data = json_fixture('books.json')
    # create collection in db and optional indices
    coll = await create_collection(db, BookResource._meta.object_class)
    # insert raw data into collection
    if coll:
        await coll.insert_many(data)
    return app


@pytest.mark.asyncio
async def test_mongo_resource_create(db):
    app = App(db=db)
    await create_collection(db, BookResource._meta.object_class)
    url = '/api/{}/'.format(BookResource.__name__)
    client = ResourceTestClient(app, BookResource)

    # create a new book
    new_book = {
        'isbn': '9780140815054',
        'title': 'A Tale of Two Cities',
        'author': ['Charles Dickens'],
        'publication_date': '1859-01-01T00:00:00.000+0000'
    }
    response = await client.post(url, body=new_book)
    assert response.status == http.CREATED
    data = client.parse_response_data(response)
    for key in new_book.keys():
        assert key in data


@pytest.mark.asyncio
async def test_mongo_resource_crud(json_fixture, db):
    ''' Basic tests covering CRUD operations '''
    app = App(db=db)
    data = json_fixture('books.json')
    coll = await create_collection(db, BookResource._meta.object_class)
    # insert raw data into collection
    if coll:
        await coll.insert_many(data)

    # create client
    url = '/api/{}/'.format(BookResource.__name__)
    client = ResourceTestClient(app, BookResource)

    # get all books
    response = await client.get(url)
    assert response.status == OK
    data = client.parse_response_data(response)
    assert 'meta' in data
    assert 'objects' in data

    # create a new book
    new_book = {
        'isbn': '9788408020011',
        'title': 'The Old Man and the Sea',
        'author': ['Ernest Hemingway'],
        'publication_date': '1953-01-01T00:00:00.000+0000'
    }
    response = await client.post(url, body=new_book)
    assert response.status == CREATED
    data = client.parse_response_data(response)
    for key in new_book.keys():
        assert key in data

    # create new review by performing PUT
    reviews = data.get('reviews', None) or []
    reviews.append({
        'user': 'Brian Fantana',
        'ratings': {
            'smooth_read': 2,
            'language': 4,
            'pace': 1,
            'originality': 2
        },
        'text': 'Could not finish it'
    })
    data['reviews'] = reviews

    response = await client.put(url + data['isbn'] + '/', body=data)
    assert response.status == ACCEPTED
    update_obj = client.parse_response_data(response)
    assert update_obj['resource_uri'] == data['resource_uri']
    assert len(update_obj['reviews']) == 1

    # create new review by performing PATCH
    reviews = update_obj.get('reviews', None)
    reviews.append({
        'user': 'Ron Burgundy',
        'ratings': {
            'smooth_read': 4,
            'language': 5,
            'pace': 3,
            'originality': 2
        },
        'text': 'Good read, really enjoyed it, even though it took me so long to finish'
    })

    response = await client.patch(url + data['isbn'] + '/', body={'reviews': reviews})
    assert response.status == OK
    update_obj = client.parse_response_data(response)
    assert update_obj['resource_uri'] == data['resource_uri']
    assert len(update_obj['reviews']) == 2

    # get detail
    response = await client.get(url + data['isbn'] + '/')
    assert response.status == OK
    update_obj = client.parse_response_data(response)
    assert update_obj['resource_uri'] == data['resource_uri']
    assert len(update_obj['reviews']) == 2
    # verify internal document fields were not serialized
    assert 'impressions' not in update_obj
    assert 'views' not in update_obj

    # delete the book
    response = await client.delete(url + data['isbn'] + '/')
    assert response.status == NO_CONTENT

    # fail to delete the book a 2nd time
    response = await client.delete(url + data['isbn'] + '/')
    assert response.status == NOT_FOUND


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


@pytest.mark.asyncio
async def test_mongo_collection_custom_indices(load_book_collection):
    app = load_book_collection

    assert BookResource._meta.object_class.primary_key == 'isbn'
    assert BookResource._meta.object_class.primary_key_type == str

    # create client
    url = '/api/{}/'.format(BookResource.__name__)
    client = ResourceTestClient(app, BookResource)

    # get books
    response = await client.get(url)
    # make sure we got a response object
    assert isinstance(response, Response)
    assert response.status == http.OK
    # parse response and retrieve data
    data = client.parse_response_data(response)
    for obj in data['objects']:
        # verify that the unique isbn is part of the resource uri
        assert obj['isbn'] in obj['resource_uri']

    # fail to insert a new book with existing isbn
    new_book = {
        'isbn': data['objects'][0]['isbn'],
        'title': 'fake title'
    }

    response = await client.post(url, body=new_book)
    data = client.parse_response_data(response)
    assert response.status == 400
    assert 'error' in data
    assert 'duplicate' in data['error']


@pytest.mark.asyncio
async def test_nested_resources(load_book_collection):
    app = load_book_collection
    # create client
    url = '/api/{}/'.format(BookResource.__name__)
    comment_url_template = '/api/{}/{}/reviews/add/'
    client = ResourceTestClient(app, BookResource)

    review = {
        'user': 'Ron Burgundy',
        'ratings': {
            'smooth_read': 4,
            'language': 5,
            'pace': 3,
            'originality': 2
        },
        'text': 'Good read, really enjoyed it, even though it took me so long to finish'
    }
    # get a book
    response = await client.get(url)
    assert response.status == OK
    data = client.parse_response_data(response)
    book_data = data['objects'][0]
    pk = book_data['isbn']
    # create new comment
    comment_url = comment_url_template.format(BookResource.__name__, pk)
    response = await client.post(comment_url, body=review)
    assert response.status == CREATED



