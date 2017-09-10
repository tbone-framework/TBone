#!/usr/bin/env python
# encoding: utf-8

import json
from tbone.resources import Resource
from tbone.resources.mongo import *
from tbone.resources.http import *
from tbone.testing import DummyResource
from tests.db.models import Account, Book


class PersonResource(DummyResource, Resource):
    '''
    Used during resource tests.
    Implements a poor-man's RESTful API over an in-memory fixture loaded during creation
    '''
    limit = 10
    pk_type = int
    pk = 'id'

    async def list(self, *args, **kwargs):
        offset = kwargs.get('offset', 0)
        limit = kwargs.get('limit', self.limit)
        return {
            'meta': {
                'total_count': len(self.request.app.db),
                'limit': self.limit,
                'offset': 0
            },
            'objects': self.request.app.db[offset:limit]
        }

    async def detail(self, *args, **kwargs):
        pk = kwargs.get('pk')
        if pk:
            obj = next(filter(lambda x: x['id'] == self.pk_type(pk), self.request.app.db), None)
            if obj:
                return obj
        raise NotFound('Object matching the given {} with value {} was not found'.format(self.pk, self.pk_type(pk)))

    async def create(self, *args, **kwargs):
        new_obj = self.request.body
        new_obj['id'] = new_id = len(self.request.app.db) + 1
        self.request.app.db.append(new_obj)
        return new_obj

    async def update(self, *args, **kwargs):
        raise MethodNotImplemented()

    async def delete(self, *args, **kwargs):
        raise MethodNotImplemented()


class AccountResource(DummyResource, MongoResource):
    '''
    Used for testing MongoResource functionality over a real MongoDB databse .
    Data fixtures are loaded for each test
    '''
    class Meta:
        object_class = Account


class BookResource(DummyResource, MongoResource):
    class Meta:
        object_class = Book
