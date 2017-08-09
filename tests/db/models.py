#!/usr/bin/env python
# encoding: utf-8

from tbone.data.fields import *
from tbone.data.fields.mongo import ObjectIdField
from tbone.data.models import *
from tbone.db.models import MongoDBMixin


class Person(Model, MongoDBMixin):
    _id = ObjectIdField()
    first_name = StringField(required=True)
    last_name = StringField(required=True)


class Number(Model, MongoDBMixin):
    _id = ObjectIdField()
    number = IntegerField()