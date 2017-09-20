#!/usr/bin/env python
# encoding: utf-8

import pytest
import datetime
from tbone.data.fields import *
from tbone.data.fields.mongo import *
from tbone.data.models import Model
from tests.fixtures import *
from .models import BaseModel, Person


def test_objectid_field():
    obj = ObjectId()
    obj_str = str(obj)
    f = ObjectIdField()

    assert isinstance(f.to_python(obj), ObjectId)
    assert isinstance(f.to_python(obj_str), ObjectId)
    assert f.to_python(obj_str) == obj
    assert isinstance(f.to_data(obj), str)
    assert f.to_data(obj) == str(obj)



@pytest.mark.asyncio
async def test_dbref_field(request, db):
    class Book(BaseModel):
        title = StringField()
        author = DBRefField(Person)

    author = Person({'first_name': 'Lewis', 'last_name': 'Carroll'})
    await author.save(db)

    book = Book({
        'title': "Alice's Adventures in Wonderland",
        'author': author
    })
    await book.save(db)
    assert book._id

    same_book = await Book.find_one(db, {'_id': book._id})
    data = same_book.export_data(native=False)
    # create book from raw data
    new_book = Book(data)
    assert new_book.author == book.author


@pytest.mark.asyncio
async def test_dbref_field_in_list(request, db):
    class Book(BaseModel):
        title = StringField()
        authors = ListField(DBRefField(Person))

    author1 = Person({'first_name': 'Stephen', 'last_name': 'King'})
    author2 = Person({'first_name': 'Peter', 'last_name': 'Straub'})

    await asyncio.gather(author1.save(db), author2.save(db))
    assert author1._id is not None
    assert author2._id is not None

    book = Book({
        'title': "The Talisman",
        'authors': [author1, author2]
    })
    await book.save(db)
    assert book._id

    same_book = await Book.find_one(db, {'_id': book._id})
    assert same_book.authors == book.authors


@pytest.mark.asyncio
async def test_dbref_field_in_dict(request, db):
    class Book(BaseModel):
        title = StringField()
        authors = DictField(DBRefField(Person))

    author1 = Person({'first_name': 'Stephen', 'last_name': 'King'})
    author2 = Person({'first_name': 'Peter', 'last_name': 'Straub'})

    await asyncio.gather(author1.save(db), author2.save(db))
    assert author1._id is not None
    assert author2._id is not None

    book = Book({
        'title': "The Talisman",
        'authors': {'first': author1, 'second': author2}
    })
    await book.save(db)
    assert book._id

    same_book = await Book.find_one(db, {'_id': book._id})
    assert same_book.authors == book.authors










