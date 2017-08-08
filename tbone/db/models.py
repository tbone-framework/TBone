#!/usr/bin/env python
# encoding: utf-8

import logging
import asyncio
from datetime import timedelta
from bson.objectid import ObjectId
from pymongo.errors import ConnectionFailure
from pymongo import ReturnDocument
from tbone.dispatch import Signal


logger = logging.getLogger(__file__)

pre_save = Signal()
post_save = Signal()


class MongoDBMixin(object):
    ''' Mixin for schematics models, provides a persistency layer over a MongoDB collection '''

    primary_key = '_id'             # default field as primary key
    primary_key_type = ObjectId     # default type for primary key

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
    def get_collection(cls):
        if hasattr(cls, 'Options'):
            np = getattr(cls.Options, 'namespace', None)
            if np:
                return '{}_{}'.format(np, getattr(cls, 'COLLECTION', cls.__name__.lower()))
        return getattr(cls, 'COLLECTION', cls.__name__.lower())

    @staticmethod
    def connection_retries():
        ''' returns the number of connection retries '''
        return range(5) # options.db_connection_retries + 1)

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
                result = await db[cls.get_collection()].count()
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
                result = await db[cls.get_collection()].find_one(query)
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
        return db[cls.get_collection()].find(filter=query, projection=projection, sort=sort)

    @classmethod
    async def create_index(cls, db, indices, **kwargs):
        for i in cls.connection_retries():
            try:
                result = await db[cls.get_collection()].create_index(indices, **kwargs)
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
                fields = set(cls._fields.keys())
                for i in range(len(result)):
                    result[i] = cls.create_model(result[i], fields)
                return result
            except ConnectionFailure as e:
                exceed = await cls.check_reconnect_tries_and_wait(i, 'find')
                if exceed:
                    raise e

    @classmethod
    async def distinct(cls, db, key):
        for i in cls.connection_retries():
            try:
                result = await db[cls.get_collection()].distinct(key)
                return result
            except ConnectionFailure as ex:
                exceed = await cls.check_reconnect_tries_and_wait(i, 'count')
                if exceed:
                    raise ex

    @classmethod
    async def delete_entries(cls, db, query):
        ''' Delete documents by given query. '''
        query = cls.process_query(query)
        for i in cls.connection_retries():
            try:
                result = await db[cls.get_collection()].remove(query)
                return result
            except ConnectionFailure as ex:
                exceed = await cls.check_reconnect_tries_and_wait(i, 'remove_entries')
                if exceed:
                    raise ex

    async def delete(self, db=None):
        ''' Delete current document from collection '''
        result = await self.delete_entries(db, {'_id': self.pk})
        return result

    @classmethod
    def create_model(cls, data, fields=None):
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

    def prepare_data(self, data):
        data = data or self.to_python()
        if '_id' in data and data['_id'] is None:
            del data['_id']
        return data

    async def save(self, db=None, data=None):
        '''
        If object has _id, then object will be created or fully rewritten.
        If not, object will be inserted and _id will be assigned.
        '''
        self._db = db or self._db
        data = self.prepare_data(data)
        # validate object
        self.validate()
        # remove extra fields which do not belong to the model
        field_names = set(self._fields.keys())
        extra_keys = set(data.keys()) - field_names
        for key in extra_keys:
            data.pop(key, None)
        # connect to DB to save the model
        result = None
        for i in self.connection_retries():
            try:
                created = False if '_id' in data else True
                result = await self.db[self.get_collection()].save(data)
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

    async def insert(self, db=None, data=None):
        '''
        If object has _id then a DuplicateError will be thrown.
        If not, object will be inserted and _id will be assigned.
        '''
        db = db or self.db
        data = self.prepare_data(data)
        for i in self.connection_retries():
            try:
                result = await db[self.get_collection()].insert(data)
                if result:
                    self._id = result
                return
            except ConnectionFailure as ex:
                exceed = await self.check_reconnect_tries_and_wait(i, 'insert')
                if exceed:
                    raise ex

    async def update(self, db=None, data=None, full=True):
        db = db or self.db
        if data:
            self.import_data(data)
            ndata = self.to_python()
            ndata = self.prepare_data(ndata)
            data = {x: ndata[x] for x in ndata if x in data or x == self.primary_key}
        else:
            data = self.to_python()

        if self.primary_key not in data or data[self.primary_key] is None:
            raise Exception('Missing object id')
        query = {self.primary_key: data.pop(self.primary_key, None)}
        data = {'$set': data}
        for i in self.connection_retries():
            try:
                result = await db[self.get_collection()].find_one_and_update(
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


async def create_collections(db):
    ''' load all models in app and create collections in db with specified indices'''
    for model_class in MongoDBMixin.__subclasses__():
        name = model_class.get_collection()
        if name:
            try:
                # create collection
                await db.create_collection(name)
            except CollectionInvalid:
                raise
            # create indices
            if hasattr(model_class, 'indices'):
                for index in model_class.indices:
                    await db[name].create_index(
                        index['fields'],
                        name=index.get('name', '_'.join([x[0] for x in index['fields']])),
                        unique=index.get('unique', False),
                        sparse=index.get('sparse', False),
                        expireAfterSeconds=index.get('expireAfterSeconds', None),
                        background=True
                    )
