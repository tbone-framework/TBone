#!/usr/bin/env python
# encoding: utf-8

import asyncio
import pytest
import random
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.errors import DuplicateKeyError
from tbone.testing import *
from tbone.testing.fixtures import *
from .models import *


COUNT = 100
PAGE = 10


@pytest.mark.asyncio
async def test_model_name_and_namespace(request, db):
    class M(BaseModel):
        name = StringField()

        class Meta:
            namespace = 'kitchen'
            name = 'hats'

    m = M({'name': 'Toque'})
    await m.save(db)
    # verify defined namespace.name exists
    names = await db.collection_names()
    assert 'kitchen.hats' in names

    class M2(BaseModel):
        name = StringField()

    m = M2({'name': 'Toque'})
    await m.save(db)
    # verify default model class name exists
    names = await db.collection_names()
    assert 'm2' in names


@pytest.mark.asyncio
async def test_model_crud_operations(request, db):

    # save model to db
    p1 = Person({'first_name': 'Ron', 'last_name': 'Burgundy'})
    await p1.save(db=db)

    # load model from db
    p2 = await Person.find_one(db, {'first_name': 'Ron'})
    assert isinstance(p2, Person)
    assert p1 == p2

    # update model in db implicit
    p2.first_name = 'Michael'
    p3 = await p2.update(db)
    assert p3
    assert p2.pk == p3.pk
    assert p3.first_name == 'Michael'

    # fail to insert model that already has a mongodb _id
    with pytest.raises(DuplicateKeyError):
        await p2.insert(db)

    # update model in db explicit
    p3 = await p3.update(db, {'first_name': 'Ron'})
    assert p3
    assert p3.first_name == 'Ron'

    # modify a model
    p4 = await Person.modify(db, p3.pk, {'first_name': 'Michael'})
    assert p4
    assert p4.first_name == 'Michael'

    # delete model from db
    await p4.delete(db)

    p5 = await Person.find_one(db=db, query={'first_name': 'Ron'})
    assert p5 is None


@pytest.mark.asyncio
async def test_model_by_pk(request, db):
    # save model to db
    p1 = Person({'first_name': 'Ron', 'last_name': 'Burgundy'})
    await p1.save(db=db)

    # load model from db
    p2 = await Person.find_one(db, {'_id': p1.pk})
    assert isinstance(p2, Person)
    assert p1 == p2


@pytest.mark.asyncio
async def test_connection_count_and_delete(request, db):
    p1 = Person({'first_name': 'Ron', 'last_name': 'Burgundy'})
    p2 = Person({'first_name': 'Brick', 'last_name': 'Tamland'})
    p3 = Person({'first_name': 'Brian', 'last_name': 'Fantana'})
    p4 = Person({'first_name': 'Champ', 'last_name': 'Kind'})

    await asyncio.wait([
        p1.save(db=db),
        p2.save(db=db),
        p3.save(db=db),
        p4.save(db=db),
    ])

    count = await Person.count(db=db)
    assert count == 4

    await Person.delete_entries(db=db, query={})
    count = await Person.count(db=db)
    assert count == 0


@pytest.mark.asyncio
async def test_collection_pagination_and_sorting(request, db):
    # create a collection with a large number of documents
    futures = []
    for i in range(COUNT):
        m = Number({'number': random.randint(1, COUNT) * 35})
        futures.append(m.save(db))
    await asyncio.wait(futures)
    # make sure the collection contains the right amount of documents
    cursor = Number.get_cursor(db=db)
    total_count = await cursor.count()
    assert total_count == COUNT

    # get objects from collection by size of page
    numbers = []
    for i in range(int(COUNT / PAGE)):
        cursor = Number.get_cursor(db=db, sort=[('number', 1)])
        cursor.skip(i * PAGE)
        cursor.limit(PAGE)
        ms = await Number.find(cursor)
        assert len(ms) == PAGE
        numbers += [m.number for m in ms]

    assert len(numbers) == COUNT
    assert numbers == sorted(numbers)


@pytest.mark.asyncio
async def test_model_custom_methods(request, db):
    ''' Test custom methods for model updating implemented in the model class '''

    # create a new book and save to DB
    book = Book({
        'isbn': '9781602523692',
        'title': 'War and Peace',
        'author': ['Leo Tolstoy'],
        'publication_date': '1869-01-01T00:00:00.000+0000'
    })
    await book.save(db)
    # create review and add, using custom method on model
    result = await book.add_review(db, {
        'user': 'Ron Burgundy',
        'ratings': {
            'smooth_read': 4,
            'language': 5,
            'pace': 3,
            'originality': 2
        },
        'text': 'Good read, really enjoyed it, even though it took me so long to finish'
    })
    assert result.matched_count == 1
    assert result.modified_count == 1
    # increment view
    result = await book.inc_number_of_views(db)
    assert result.matched_count == 1
    assert result.modified_count == 1

    new_book = Book()
    new_book = await Book.find_one(db, {book.primary_key: book.pk})
    assert len(new_book.reviews) == 1
    assert new_book.number_of_views == 1



