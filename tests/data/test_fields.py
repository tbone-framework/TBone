#!/usr/bin/env python
# encoding: utf-8

import pytest
import datetime
from tbone.data.fields import *
from tbone.data.models import Model
from tests.fixtures import event_loop


def test_field_meta():
    ''' Test custom FieldMeta class to make sure field data is managed for all base classes '''
    class SomeField(BaseField):
        ERRORS = {
            'first': 'First Error'
        }

    f = SomeField()
    assert len(f._errors) == len(SomeField.ERRORS) + len(BaseField.ERRORS)


def test_string_field():
    s = StringField()
    assert s.to_data(None) is None


def test_datetime_field():
    dt = datetime.datetime.now()
    assert DateTimeField()(dt.isoformat()) == dt


def test_date_field():
    da = datetime.date.today()
    assert DateField()(da.isoformat()) == da

    df = DateField()
    res = df.to_python('2017.01.01')
    assert isinstance(res, datetime.date)


def test_time_field():
    tn = datetime.time(hour=17, minute=26)
    assert TimeField()(tn.isoformat()) == tn

    df = TimeField()
    res = df.to_python('21:34')
    assert isinstance(res, datetime.time)


def test_default():
    number = IntegerField(default=5)
    assert number.to_data(None) == 5

    class M(Model):
        number = IntegerField(default=5)

    m = M()
    assert m.number == 5


def test_choices():
    number = IntegerField(choices=[1, 3, 5, 7, 9])
    number.validate(7)
    with pytest.raises(ValueError):
        number.validate(6)

    country = StringField(choices=['CA', 'US', 'MX', 'DE', 'UK', 'JP'])
    country.validate('US')
    with pytest.raises(ValueError):
        country.validate('NP')


def test_required():
    number = IntegerField(required=True)

    with pytest.raises(Exception):
        number.to_data(None)

    assert 5 == number.to_data(5)

    with pytest.raises(AttributeError):
        number = IntegerField(required=True, default=0)


@pytest.mark.asyncio
async def test_field_projection():
    class M(Model):
        name = StringField(default='Ron Burgundy')
        number = IntegerField(projection=False)
        age = IntegerField(projection=None)

    m = M()
    ser = await m.to_data()
    assert 'name' in ser
    assert 'number' not in ser
    assert 'age' not in ser

    m = M({'number': 40})
    ser = await m.to_data()
    assert 'name' in ser
    assert 'number' in ser
    assert 'age' not in ser


def test_integer_field_validation():
    def validate_positive(value):
        if value < 0:
            raise ValueError('Value should be positive')
    # check validate range
    f = IntegerField(min=5, max=10, validators=[validate_positive])
    f.validate(7)
    with pytest.raises(ValueError):
        f.validate(18)

    with pytest.raises(ValueError):
        f.validate(-8)


def test_email_field_validation():
    f = EmailField()
    f.validate('ron@channel4.com')

    with pytest.raises(ValueError):
        f.validate('r.channel4.com')
        f.validate('r@channel4')
