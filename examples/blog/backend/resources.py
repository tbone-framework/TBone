#!/usr/bin/env python
# encoding: utf-8


from tbone.resources.mongo import MongoResource
from tbone.resources.sanic import SanicResource
from models import *


class EntryResource(SanicResource, MongoResource):
    class Meta:
        object_class = Entry