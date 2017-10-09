#!/usr/bin/env python
# encoding: utf-8

import asyncio
import logging
from functools import singledispatch
from bson.objectid import ObjectId
from bson.errors import InvalidId
from tbone.db.models import post_save
from tbone.dispatch.channels.mongo import MongoChannel
from tbone.resources import ModelResource
from tbone.resources.http import *
from tbone.resources.signals import *

LIMIT = 20
OFFSET = 0

logger = logging.getLogger(__file__)


class MongoResource(ModelResource):
    '''
    A specialized ``Resource`` subclass used for creating API endpoints coupled to a MongoDB collection.
    Provides basic CRUD operations using standard HTTP verbs.
    '''
    class Meta:
        channel_class = MongoChannel

    @property
    def limit(self):
        return LIMIT

    @property
    def offset(self):
        return OFFSET

    @classmethod
    async def emit(cls, db, key, data):
        pubsub = cls._meta.channel_class(name='pubsub', db=db)
        await pubsub.publish(key, data)

    # ---------- receivers ------------ #

    @classmethod
    @receiver(post_save)
    async def post_save(cls, sender, db, instance, created):
        if instance.pk is None:
            return

        async def _emit(event_name):
            resource = cls()
            obj = await instance.serialize()
            if cls._meta.add_resource_uri is True:
                obj['resource_uri'] = '{}{}/'.format(resource.get_resource_uri(), instance.pk)
            await resource.emit(db, event_name, obj)

        if created is True and 'created' in cls._meta.outgoing_detail:
            await _emit('resource_create')
        elif created is False and 'updated' in cls._meta.outgoing_detail:
            await _emit('resource_update')

    @classmethod
    @receiver(resource_post_list)
    async def post_list(cls, sender, db, instances):
        '''
        Hook to capture the results of a list query.
        Useful when wanting to know when certain documents have come up in a query.
        Implement in resource subclasses to provide domain-specific behavior
        '''
        serialized_objects = await asyncio.gather(*[obj.serialize() for obj in instances])
        await cls.emit(db, 'resource_get_list', serialized_objects)

    # ------------- resource overrides ---------------- #

    async def list(self, *args, **kwargs):
        '''
        Corresponds to GET request without a resource identifier, fetching documents from the database
        '''
        limit = int(kwargs.pop('limit', self.limit))
        limit = 1000 if limit == 0 else limit  # lets not go crazy here
        offset = int(kwargs.pop('offset', self.offset))
        projection = None
        # perform full text search or standard filtering
        if self._meta.fts_operator in kwargs.keys():
            filters = {
                '$text': {'$search': kwargs[self._meta.fts_operator]}
            }
            projection = {'score': {'$meta': 'textScore'}}
            sort = [('score', {'$meta': 'textScore'}, )]
        else:
            # build filters from query parameters
            filters = self.build_filters(**kwargs)
            # add custom query defined in resource meta, if exists
            if isinstance(self._meta.query, dict):
                filters.update(self._meta.query)
            # build sorts from query parameters
            sort = self.build_sort(**kwargs)
            if isinstance(self._meta.sort, list):
                sort.extend(self._meta.sort)
        cursor = self._meta.object_class.get_cursor(db=self.db, query=filters, projection=projection, sort=sort)
        cursor.skip(offset)
        cursor.limit(limit)
        total_count = await cursor.count()
        object_list = await self._meta.object_class.find(cursor)
        # serialize results
        serialized_objects = await asyncio.gather(*[obj.serialize() for obj in object_list])
        # signal post list
        asyncio.ensure_future(resource_post_list.send(
            sender=self._meta.object_class,
            db=self.db,
            instances=object_list)
        )
        return {
            'meta': {
                'total_count': total_count,
                'limit': limit,
                'offset': offset
            },
            'objects': serialized_objects
        }

    async def detail(self, **kwargs):
        '''
        Corresponds to GET request with a resource unique identifier, fetching a single document from the database
        '''
        try:
            pk = self.pk_type(kwargs.get('pk'))
            obj = await self._meta.object_class.find_one(self.db, {self.pk: pk})
            if obj:
                return await obj.serialize()
            raise NotFound('Object matching the given {} with value {} was not found'.format(self.pk, str(pk)))
        except InvalidId:
            raise NotFound('Invalid ID')

    async def create(self, **kwargs):
        '''
        Corresponds to POST request without a resource identifier, inserting a document into the database
        '''
        try:
            # create model
            obj = self._meta.object_class()
            # deserialize data from request body
            self.data.update(kwargs)
            await obj.deserialize(self.data)
            # create document in DB
            await obj.insert(db=self.db)
            # serialize object for response
            return await obj.serialize()
        except Exception as ex:
            logger.exception(ex)
            raise BadRequest(ex)

    async def modify(self, **kwargs):
        '''
        Corresponds to PATCH request with a resource identifier, modifying a single document in the database
        '''
        try:
            pk = self.pk_type(kwargs['pk'])
            # modify is a class method on MongoCollectionMixin
            result = await self._meta.object_class.modify(self.db, key=pk, data=self.data)
            if result is None:
                raise NotFound('Object matching the given {} was not found'.format(self.pk))
            return await result.serialize()
        except Exception as ex:
            logger.exception(ex)
            raise BadRequest(ex)

    async def update(self, **kwargs):
        '''
        Corresponds to PUT request with a resource identifier, updating a single document in the database
        '''
        try:
            self.data[self.pk] = self.pk_type(kwargs['pk'])
            updated_obj = await self._meta.object_class().update(self.db, data=self.data)
            if updated_obj is None:
                raise NotFound('Object matching the given {} was not found'.format(self.pk))
            return await updated_obj.serialize()
        except Exception as ex:
            logger.exception(ex)
            raise BadRequest(ex)

    async def delete(self, *args, **kwargs):
        '''
        Corresponds to DELETE request with a resource identifier, deleting a single document from the database
        '''
        pk = self.pk_type(kwargs['pk'])
        result = await self._meta.object_class.delete_entries(db=self.db, query={self.pk: pk})
        if result.acknowledged:
            if result.deleted_count == 0:
                raise NotFound()
        else:
            raise BadRequest('Failed to delete object')

    def build_filters(self, **kwargs):
        ''' Break url parameters and turn into filters '''
        filters = {}
        for param, value in kwargs.items():
            # break each url parameter to key + operator (if exists)
            pl = dict(enumerate(param.split('__')))
            key = pl[0]
            operator = pl.get(1, None)
            if key in self._meta.object_class.fields():
                if isinstance(value, list) and operator == 'in':
                    value = [convert_value(v) for v in value]
                else:
                    value = convert_value(value)
                # assign operator, if applicable
                filters[key] = {'${}'.format(operator): value} if operator else value
            elif key == 'created':  # special case where we map `created` key to mongo's _id which also contains a creation timestamp
                dt = parser.parse(convert_value(value))
                dummy_id = ObjectId.from_datetime(dt)
                filters['_id'] = {'${}'.format(operator): dummy_id} if operator else dummy_id
        return filters

    def build_sort(self, **kwargs):
        ''' Break url parameters and turn into sort arguments '''
        sort = []
        order = kwargs.get('order_by', None)
        if order:
            if type(order) is list:
                order = order[0]
            if order[:1] == '-':
                sort.append((order[1:], -1))
            else:
                sort.append((order, 1))
        return sort


@singledispatch
def convert_value(value):
    ''' Utility functions to convert url params to mongodb filter operators and values '''
    raise NotImplementedError('Cannot convert this {}'.format(type(value)))


@convert_value.register(list)
def _(value):
    return convert_value(value[0])


@convert_value.register(bytes)
def _(value):
    return convert_value(value.decode('utf-8'))


@convert_value.register(ObjectId)
def _(value):
    return value


@convert_value.register(str)
def _(value):
    reserved = {
        '': None,
        'null': None,
        'none': None,
        'true': True,
        'false': False
    }
    if value in reserved:
        return reserved[value]
    # check if value is of type ObjectId
    if ObjectId.is_valid(value):
        return ObjectId(value)
    # check if value is numeric and return a filter which checks both strings and integers
    if value.isnumeric():
        value = {'$in': [int(value), value]}
    # return as string
    return value
