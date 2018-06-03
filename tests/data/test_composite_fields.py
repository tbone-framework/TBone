#!/usr/bin/env python
# encoding: utf-8

import pytest
import datetime
from tbone.data.fields import *
from tbone.data.models import Model
from tbone.testing.fixtures import event_loop


def test_list_field():
    data = ['one', 'two', 'three']

    class M(Model):
        numbers = ListField(StringField, required=True)

    obj = M({'numbers': data})
    assert obj.numbers == data

    numbers = ListField(StringField)
    assert len(numbers.to_python(data)) == len(data)

    # check None works on data export
    assert numbers.to_data(None) is None

    # check default value
    names = ListField(StringField, default=[])
    assert names.to_python(None) == []
    assert names.to_data(None) == []


def test_model_field():
    class Comment(Model):
        text = StringField()
        ts = DateTimeField(default=datetime.datetime.utcnow)

    # create model field
    f = ModelField(Comment)
    # create model and convert data with field
    raw_data = {
        'text': 'great book',
        'ts': datetime.datetime.utcnow().isoformat()
    }
    comment = Comment(raw_data)
    data = f.to_data(comment)
    # verify conversion
    assert isinstance(data, dict)
    assert raw_data == data

    data = f.to_data(raw_data)
    assert isinstance(data, dict)
    assert raw_data == data

    # verify conversion fails with incompatible data type
    with pytest.raises(ValueError):
        f.to_data(6)

    # convert to python
    data = f.to_python(raw_data)
    assert isinstance(data, dict)
    assert isinstance(data['ts'], datetime.datetime)


@pytest.mark.asyncio
async def test_model_field_complete():
    class Person(Model):
        first_name = StringField(required=True)
        last_name = StringField(required=True)

    class Book(Model):
        title = StringField(required=True)
        isbn = StringField()
        author = ModelField(Person)
        language = StringField(choices=['en', 'de', 'fr'])
        publication_date = DateField()

    raw_data = {
        'author': {
            'first_name': 'Herman',
            'last_name': 'Melville'
        },
        'title': 'Moby-Dick',
        'isbn': '978-1542049054',
        'language': 'en',
        'publication_date': '1851-10-18'
    }

    book = Book(raw_data)
    export_data = await book.serialize()
    assert export_data == raw_data

    # change embedded model
    book.author.first_name = 'Herman J.'
    export_data = await book.serialize()
    assert export_data['author']['first_name'] == 'Herman J.'

    # create book without an author
    r = {}
    r.update(raw_data)
    del r['author']
    anonymous_book = Book(r)
    assert anonymous_book.author is None
    assert anonymous_book.export_data()['author'] is None


@pytest.mark.asyncio
async def test_nested_model_serialization():

    class Person(Model):
        '''Model for holding a person's name with serialization for full name only '''
        first_name = StringField(required=True, projection=None)
        last_name = StringField(required=True, projection=None)

        @serialize
        async def full_name(self):
            return '{} {}'.format(self.first_name, self.last_name)

    class Trip(Model):
        participants = ListField(ModelField(Person), default=[])
        destination = StringField(required=True)
        date = DateTimeField(required=True)

    class Journey(Model):
        participants = DictField(ModelField(Person), default={})
        destination = StringField(required=True)
        date = DateTimeField(required=True)

    trip = Trip()
    trip.destination = 'Florida'
    trip.date = datetime.datetime.utcnow()
    trip.participants = [
        Person({'first_name': 'Ron', 'last_name': 'Burgundy'}),
        Person({'first_name': 'Brian', 'last_name': 'Fantana'})
    ]

    data = await trip.serialize()

    assert 'participants' in data
    assert isinstance(data['participants'], list)
    for p in data['participants']:
        assert 'full_name' in p
        assert 'first_name' not in p
        assert 'last_name' not in p

    journey = Journey()
    journey.destination = 'Florida'
    journey.date = datetime.datetime.utcnow()
    journey.participants = {
        'first': Person({'first_name': 'Ron', 'last_name': 'Burgundy'}),
        'second': Person({'first_name': 'Brian', 'last_name': 'Fantana'})
    }

    data = await journey.serialize()
    assert 'participants' in data
    assert isinstance(data['participants'], dict)
    for key, value in data['participants'].items():
        assert 'full_name' in value
        assert 'first_name' not in p
        assert 'last_name' not in p


def test_list_of_models():
    class Comment(Model):
        text = StringField()

    # create list of model field
    f = ListField(ModelField(Comment))

    raw_data = [
        Comment({'text': 'one'}),
        Comment({'text': 'two'}),
        Comment({'text': 'three'}),
        Comment({'text': 'four'})
    ]

    data_list = f.to_data(raw_data)
    # check that return value is list
    assert isinstance(data_list, list)
    # check that eash item in list matches the expected result
    for item in data_list:
        assert isinstance(item, dict)


def test_poly_model_field():
    class Book(Model):
        title = StringField()
        author = StringField()
        number_of_pages = IntegerField()

    class Film(Model):
        title = StringField()
        director = StringField()
        actors = ListField(StringField)

    class Product(Model):
        sku = StringField(required=True)
        media = PolyModelField([Book, Film], required=True)

    book_data = {
        'title': 'The Adventures of Sherlock Holmes',
        'author': 'Arthur Conan Doyle',
        'number_of_pages': 455
    }

    book = Book(book_data)
    # serialize book object
    f = PolyModelField([Book, Film])
    data = f.to_data(book)
    assert isinstance(data, dict)
    assert data.keys() == {'type', 'data'}
    assert data['type'] == Book.__name__
    assert data['data'] == book.export_data(native=False)

    # deserialize book object
    new_book = f.to_python(data)
    assert isinstance(new_book, Book)

    # fail to assign data to a none model
    with pytest.raises(ValueError):
        data = f.to_data(2)

    # fail to assign data to a model not previously defined
    with pytest.raises(ValueError):
        class AnotherBook(Book):
            pass
        another_book = AnotherBook(book_data)
        data = f.to_data(another_book)





    # p = Product()
    # p.sku = '9781408436011'
    # p.media = book


