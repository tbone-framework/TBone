#!/usr/bin/env python
# encoding: utf-8

from tbone.data.fields import ListField, StringField
from tbone.data.models import Model


def test_list_field():
    data = ['one', 'two', 'three']
    class M(Model):
        numbers = ListField(StringField, required=True)

    obj = M({'numbers': data})

    assert obj.numbers == data
