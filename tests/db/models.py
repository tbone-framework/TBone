#!/usr/bin/env python
# encoding: utf-8

from tbone.data.fields import *
from tbone.data.fields.mongo import ObjectIdField
from tbone.data.models import *
from tbone.db.models import MongoCollectionMixin


class Person(Model, MongoCollectionMixin):
    _id = ObjectIdField()
    first_name = StringField(required=True)
    last_name = StringField(required=True)


class Number(Model, MongoCollectionMixin):
    _id = ObjectIdField()
    number = IntegerField()