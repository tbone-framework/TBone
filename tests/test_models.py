#!/usr/bin/env python
# encoding: utf-8

import pytest
import datetime
from itertools import zip_longest
from tbone.data.fields import *
from tbone.data.models import *


def test_model_repr():
    ''' Test Model repr function '''
    class M(Model):
        pass
    m = M()
    assert repr(m) == '<M instance>'


def test_model_creation_and_export():
    '''
    Simple model creation test
    '''
    class M(Model):
        name = StringField()
        age = IntegerField()
        decimal = FloatField()
        dt = DateTimeField()

    # m = M({'name': 'Ron Burgundy', 'age': 45, 'decimal': 34.77, 'dt': datetime.datetime.utcnow()})
    m = M({'name': 'Ron Burgundy', 'age': 45, 'decimal': '34.77', 'dt': '2017-07-25T12:34:14.414471'})


    import pdb; pdb.set_trace()

    # convert model to primitive form
    prim = m.to_data()
    # check result is dict
    assert isinstance(prim, dict)
    # check keys match
    assert all(a == b for a, b in zip_longest(m._fields.keys(), prim.keys(), fillvalue=None))


