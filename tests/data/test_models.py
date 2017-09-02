#!/usr/bin/env python
# encoding: utf-8

import pytest
import datetime
from itertools import zip_longest
from tbone.data.fields import *
from tbone.data.models import *
from tests.fixtures import event_loop


def test_model_repr():
    ''' Test Model repr function '''
    class M(Model):
        pass
    m = M()
    assert repr(m) == '<M instance>'


@pytest.mark.asyncio
async def test_model_creation_and_export():
    '''
    Simple model creation test
    '''
    class M(Model):
        name = StringField()
        age = IntegerField()
        decimal = FloatField()
        dt = DateTimeField()

    m = M({'name': 'Ron Burgundy', 'age': 45, 'decimal': '34.77', 'dt': '2017-07-25T12:34:14.414471'})

    # convert model to primitive form
    data = await m.to_data()
    # check result is dict
    assert isinstance(data, dict)
    # check keys match
    assert all(a == b for a, b in zip_longest(m._fields.keys(), data.keys(), fillvalue=None))


@pytest.mark.asyncio
async def test_model_import():
    class M(Model):
        first_name = StringField()
        last_name = StringField()

    m = M()
    m.import_data({'first_name': 'Ron', 'last_name': 'Burgundy'})
    data = await m.to_data()

    assert data['first_name'] == 'Ron'
    assert data['last_name'] == 'Burgundy'

    with pytest.raises(ValueError):
        m.import_data('Ron Burgundy')


@pytest.mark.asyncio
async def test_model_export_decorator():
    class M(Model):
        first_name = StringField()
        last_name = StringField()

        @export
        async def full_name(self):
            return '{} {}'.format(self.first_name, self.last_name)

    m = M({'first_name': 'Ron', 'last_name': 'Burgundy'})
    data = await m.to_data()

    assert data['first_name'] == 'Ron'
    assert data['last_name'] == 'Burgundy'
    assert 'full_name' in data
    assert data['full_name'] == 'Ron Burgundy'


def test_model_items():
    class M(Model):
        first_name = StringField()
        last_name = StringField()
        dob = DateTimeField()

    data = {'first_name': 'Ron', 'last_name': 'Burgundy', 'dob': datetime.datetime.now()}
    mo = M(data)
    for key, value in mo.items():
        assert value == data[key]


@pytest.mark.asyncio
async  def test_field_projection():
    class M(Model):
        first_name = StringField()
        last_name = StringField()
        dob = DateTimeField()
        number_of_views = IntegerField(default=0, projection=None)

    data = {'first_name': 'Ron', 'last_name': 'Burgundy', 'dob': datetime.datetime.now()}
    mo = M(data)

    serialized = await mo.to_data()
    for key in data.keys():
        assert key in serialized

    assert 'number_of_views' not in serialized
