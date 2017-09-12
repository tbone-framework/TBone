#!/usr/bin/env python
# encoding: utf-8


from datetime import datetime
from tbone.data.models import Model
from tbone.data.fields import *
from tbone.data.fields.mongo import ObjectIdField
from tbone.db.models import MongoCollectionMixin


class Comment(Model):
    timestamp = DateTimeField(default=datetime.now)
    text = StringField(required=True)
    user = StringField(required=True)


class Entry(Model, MongoCollectionMixin):
    _id = ObjectIdField(primary_key=True)
    title = StringField(required=True)
    content = StringField(required=True)
    tags = ListField(StringField)

    comments = ListField(ModelField(Comment))
