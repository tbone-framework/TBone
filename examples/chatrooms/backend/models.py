#!/usr/bin/env python
# encoding: utf-8

import datetime
from pymongo import ASCENDING, TEXT
from tbone.data.models import Model
from tbone.data.fields import *
from tbone.data.fields.mongo import ObjectIdField, DBRefField
from tbone.db.models import MongoCollectionMixin


ACCESS_PUBLIC = 10
ACCESS_PROTECTED = 20
ACCESS_PRIVATE = 30


class BaseModel(Model, MongoCollectionMixin):
    _id = ObjectIdField(primary_key=True)

    @serialize
    async def created(self):
        return self._id.generation_time.isoformat()


class User(BaseModel):
    username = StringField(required=True)
    first_name = StringField()
    last_name = StringField()
    avatar = URLField()
    active = BooleanField(default=True)

    class Meta:
        name = 'users'

    indices = [
        {
            'name': '_username',
            'fields': [('username', ASCENDING)],
            'unique': True
        }
    ]


class Room(BaseModel):
    name = StringField(primary_key=True)
    title = StringField()
    active = BooleanField(default=True)
    access = IntegerField(default=ACCESS_PUBLIC, choices=[ACCESS_PUBLIC, ACCESS_PROTECTED, ACCESS_PRIVATE])
    owner = DBRefField(User, required=True)
    members = ListField(DBRefField(User), default=[])

    class Meta:
        name = 'rooms'

    indices = [
        {
            'name': '_name',
            'fields': [('name', ASCENDING)],
            'unique': True
        }
    ]

    async def add_member(self, db, user):
        ''' Adds a new user to the list of room members, if memeber doesn't exist already '''

        # use model's pk as query
        query = {self.primary_key: self.pk}
        # push review
        result = await db[self.get_collection_name()].update_one(
            filter=query,
            update={'$addToSet': {'members': DBRefField(User).to_python(user)}},
        )
        return result

    async def remove_member(self, db, user):
        pass


CAPACITY = 2**15
ENTRY_SIZE = 1024


class Entry(BaseModel):
    user = DBRefField(User, required=True)
    room = StringField(required=True)
    text = StringField(required=True)

    class Meta:
        name = 'entries'
        creation_args = {
            'capped': True,
            'max': CAPACITY,
            'size': CAPACITY * ENTRY_SIZE
        }

    indices = [
        {
            'name': '_user',
            'fields': [('user', ASCENDING)],
        }, {
            'name': '_room',
            'fields': [('room', ASCENDING)],
        }
    ]



