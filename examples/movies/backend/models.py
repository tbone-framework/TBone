#!/usr/bin/env python
# encoding: utf-8

from pymongo import TEXT
from tbone.data.models import Model
from tbone.data.fields import *
from tbone.data.fields.mongo import ObjectIdField
from tbone.db.models import MongoCollectionMixin


class Reviews(Model):
    title = StringField(required=True)
    text = StringField(required=True)
    rating = FloatField(required=True)
    user = ObjectIdField()


class Movie(Model, MongoCollectionMixin):
    _id = ObjectIdField(primary_key=True)
    title = StringField(required=True)
    plot = StringField()
    director = StringField()
    cast = ListField(StringField)
    release_date = DateField()
    runtime = IntegerField()
    poster = URLField()
    language = StringField(projection=False)
    genres = StringField()
    reviews = ListField(ModelField(Reviews))

    class Meta:
        indices = [
            {
                'name': '_fts',
                'fields': [
                    ('title', TEXT),
                    ('plot', TEXT),
                    ('cast', TEXT),
                    ('genres', TEXT)
                ]
            }
        ]
