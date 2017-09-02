#!/usr/bin/env python
# encoding: utf-8

import pytest
import datetime
from tbone.data.fields import *
from tbone.data.models import Model
from tests.fixtures import event_loop


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
    export_data = await book.to_data()
    assert export_data == raw_data


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
