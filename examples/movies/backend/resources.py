#!/usr/bin/env python
# encoding: utf-8


from tbone.resources.mongo import MongoResource
from tbone.resources.aiohttp import AioHttpResource
from models import *


class MovieResource(AioHttpResource, MongoResource):
    class Meta:
        object_class = Movie
