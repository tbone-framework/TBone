#!/usr/bin/env python
# encoding: utf-8

import pytest
import datetime
from tbone.data.fields import *
from tbone.data.models import Model

def test_field_meta():
    ''' Test custom FieldMeta class to make sure field data is managed for all base classes '''
    class SomeField(BaseField):
        ERRORS = {
            'first': 'First Error'
        }

    f = SomeField()
    assert len(f._errors) == len(SomeField.ERRORS) + len(BaseField.ERRORS)


# def test_datetime_field():
#     dt = datetime.datetime.now()

#     f = DateTimeField()


def test_datetime_field():
    dt = datetime.datetime.now()
    assert DateTimeField()(dt.isoformat()) == dt



def test_default():
    class M(Model):
        number = IntegerField(default=5)

    m = M()
    assert m.number == 5
