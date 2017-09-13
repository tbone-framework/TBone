#!/usr/bin/env python
# encoding: utf-8

import json
from tbone.resources import Resource, http
from tbone.resources.mongo import *
from tbone.resources.routers import Route
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

    @classmethod
    def nested_routes(cls, base_url):
        return [
            Route(
                path=base_url + '/(?P<pk>[\w\d_.-]+)/reviews/add/',
                handler=cls.add_review,
                methods='POST',
                name='add_review')
        ]

    @classmethod
    async def add_review(cls, request, **kwargs):
        try:
            if 'pk' not in request.args:
                raise Exception('Object pk not provided')
            # add a new review to the document using a custom Model method which pushes the new review to the document
            book = Book({Book.primary_key: request.args['pk']})
            update_result = await book.add_review(request.app.db, request.body)
            if update_result.matched_count != 1 or update_result.modified_count != 1:
                raise Exception('Database update failed. Unexpected update results')
            return cls.build_response(None, http.CREATED)
        except Exception as ex:
            return cls.build_response({'error': ex}, http.BAD_REQUEST)
