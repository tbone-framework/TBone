#!/usr/bin/env python
# encoding: utf-8

import logging
import asyncio
from datetime import timedelta
from bson.objectid import ObjectId
from pymongo.errors import *
from pymongo import ReturnDocument
from tbone.dispatch import Signal


logger = logging.getLogger(__file__)

pre_save = Signal()
post_save = Signal()


class MongoCollectionMixin(object):
    ''' Mixin for data models, provides a persistency layer over a MongoDB collection '''

    @property
    def db(self):
        return getattr(self, '_db', None)

    @property
    def pk(self):
        return getattr(self, self.primary_key)

    @classmethod
    def process_query(cls, query):
        ''' modify queries before sending to db '''
        return dict(query)

    @classmethod
    def get_collection_name(cls):
        if hasattr(cls, '_meta'):
            np = getattr(cls._meta, 'namespace', None)
            cname = getattr(cls._meta, 'name', None)
            if np:
                return '{}.{}'.format(np, cname or cls.__name__.lower())
        return cname or cls.__name__.lower()

    @staticmethod
    def connection_retries():
        '''
        returns the number of connection retries.
        Subclass to obtain this variable from the app's global settings
        '''
        return range(5)

    @classmethod
    async def check_reconnect_tries_and_wait(cls, reconnect_number, method_name):
        if reconnect_number >= options.db_connection_retries:
            return True
        else:
            timeout = options.db_reconnect_timeout
            logger.warning('ConnectionFailure #{0} in {1}.{2}. Waiting {3} seconds'.format(
                reconnect_number + 1,
                cls.__name__, method_name,
                timeout
            ))
            await asyncio.sleep(timeout)

    @classmethod
    async def count(cls, db):
        for i in cls.connection_retries():
            try:
                result = await db[cls.get_collection_name()].count()
                return result
            except ConnectionFailure as ex:
                exceed = await cls.check_reconnect_tries_and_wait(i, 'count')
                if exceed:
                    raise ex

    @classmethod
    async def find_one(cls, db, query):
        result = None
        query = cls.process_query(query)
        for i in cls.connection_retries():
            try:
                result = await db[cls.get_collection_name()].find_one(query)
                if result:
                    result = cls.create_model(result)
                return result
            except ConnectionFailure as ex:
                exceed = await cls.check_reconnect_tries_and_wait(i, 'find_one')
                if exceed:
                    raise ex

    @classmethod
    def get_cursor(cls, db, query={}, projection=None, sort=[]):
        query = cls.process_query(query)
        return db[cls.get_collection_name()].find(filter=query, projection=projection, sort=sort)

    @classmethod
    async def create_index(cls, db, indices, **kwargs):
        for i in cls.connection_retries():
            try:
                result = await db[cls.get_collection_name()].create_index(indices, **kwargs)
            except ConnectionFailure as e:
                exceed = await cls.check_reconnect_tries_and_wait(i, 'create_index')
                if exceed:
                    raise e
            else:
                return result

    @classmethod
    async def find(cls, cursor):
        result = None
        for i in cls.connection_retries():
            try:
                result = await cursor.to_list(length=None)
                for i in range(len(result)):
                    result[i] = cls.create_model(result[i])
                return result
            except ConnectionFailure as e:
                exceed = await cls.check_reconnect_tries_and_wait(i, 'find')
                if exceed:
                    raise e

    @classmethod
    async def distinct(cls, db, key):
        for i in cls.connection_retries():
            try:
                result = await db[cls.get_collection_name()].distinct(key)
                return result
            except ConnectionFailure as ex:
                exceed = await cls.check_reconnect_tries_and_wait(i, 'distinct')
                if exceed:
                    raise ex

    @classmethod
    async def delete_entries(cls, db, query):
        ''' Delete documents by given query. '''
        query = cls.process_query(query)
        for i in cls.connection_retries():
            try:
                result = await db[cls.get_collection_name()].remove(query)
                return result
            except ConnectionFailure as ex:
                exceed = await cls.check_reconnect_tries_and_wait(i, 'delete_entries')
                if exceed:
                    raise ex

    async def delete(self, db=None):
        ''' Delete current document from collection '''
        result = await self.delete_entries(db, {'_id': self.pk})
        return result

    @classmethod
    def create_model(cls, data: dict, fields=None):
        '''
        Creates model instance from data (dict).
        '''
        if fields is None:
            fields = set(cls._fields.keys())
        else:
            if not isinstance(fields, set):
                fields = set(fields)
        new_keys = set(data.keys()) - fields
        if new_keys:
            for new_key in new_keys:
                del data[new_key]
        return cls(data)

    def prepare_data(self, data=None):
        data = data or self.export_data(native=True)
        if '_id' in data and data['_id'] is None:
            del data['_id']
        return data

    async def save(self, db=None):
        '''
        If object has _id, then object will be created or fully rewritten.
        If not, object will be inserted and _id will be assigned.
        '''
        self._db = db or self._db
        data = self.prepare_data()
        # validate object
        self.validate()
        # connect to DB to save the model
        result = None
        for i in self.connection_retries():
            try:
                created = False if '_id' in data else True
                result = await self.db[self.get_collection_name()].save(data)
                self._id = result
                # emit post save
                asyncio.ensure_future(post_save.send(
                    sender=self.__class__,
                    instance=self,
                    created=created)
                )
                break
            except ConnectionFailure as ex:
                exceed = await self.check_reconnect_tries_and_wait(i, 'save')
                if exceed:
                    raise ex

    async def insert(self, db=None):
        '''
        If object has _id then a DuplicateError will be thrown.
        If not, object will be inserted and _id will be assigned.
        '''
        db = db or self.db
        data = self.prepare_data(self._data)
        for i in self.connection_retries():
            try:
                result = await db[self.get_collection_name()].insert(data)
                self._id = result
                # emit post save
                asyncio.ensure_future(post_save.send(
                    sender=self.__class__,
                    instance=self,
                    created=created)
                )
                break
            except ConnectionFailure as ex:
                exceed = await self.check_reconnect_tries_and_wait(i, 'insert')
                if exceed:
                    raise ex

    async def update(self, db=None, data=None, full=True):
        db = db or self.db
        if data:
            self.import_data(data)
            ndata = self.export_data(native=True)
            ndata = self.prepare_data(ndata)
            data = {x: ndata[x] for x in ndata if x in data or x == self.primary_key}
        else:
            data = self.export_data(native=True)

        if self.primary_key not in data or data[self.primary_key] is None:
            raise Exception('Missing object primary key')
        query = {self.primary_key: data.pop(self.primary_key, None)}
        data = {'$set': data}
        for i in self.connection_retries():
            try:
                result = await db[self.get_collection_name()].find_one_and_update(
                    filter=query,
                    update=data,
                    return_document=ReturnDocument.AFTER
                )
                if result:
                    updated_obj = self.create_model(result)
                    updated_obj._db = db
                    # emit post save
                    asyncio.ensure_future(post_save.send(
                        sender=self.__class__,
                        instance=updated_obj,
                        created=False)
                    )
                    return updated_obj

                return None
            except ConnectionFailure as ex:
                exceed = await self.check_reconnect_tries_and_wait(i, 'update')
                if exceed:
                    raise ex


async def create_collection(db, model_class):
    name = model_class.get_collection_name()
    if name:
        try:
            # create collection
            coll = await db.create_collection(name)
        except CollectionInvalid:  # collection already exists
            coll = db[name]

        # create indices
        if hasattr(model_class, 'indices'):
            for index in model_class.indices:
                try:
                    await db[name].create_index(
                        index['fields'],
                        name=index.get('name', '_'.join([x[0] for x in index['fields']])),
                        unique=index.get('unique', False),
                        sparse=index.get('sparse', False),
                        expireAfterSeconds=index.get('expireAfterSeconds', None),
                        partialFilterExpression=index.get('partialFilterExpression', None),
                        background=True
                    )
                except OperationFailure:
                    pass  # index already exists
        return coll
    return None


async def create_app_collections(db):
    ''' load all models in app and create collections in db with specified indices'''
    futures = []
    for model_class in MongoCollectionMixin.__subclasses__():
        futures.append(create_collection(db, model_class))

    await asyncio.gather(*futures)
