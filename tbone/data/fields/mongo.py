#!/usr/bin/env python
# encoding: utf-8

from bson.objectid import ObjectId
from bson.dbref import DBRef
from tbone.data.fields import BaseField, CompositeField
from tbone.db.models import MongoCollectionMixin
from tbone.data import ModelMeta


class ObjectIdField(BaseField):
    '''
    A field wrapper around MongoDB ObjectIds
    '''
    _data_type = str
    _python_type = ObjectId
    ERRORS = {
        'convert': "Could not cast value as ObjectId",
    }

    def _import(self, value):
        if value is None:
            return None
        return self._python_type(value)


class RefDict(dict):
    __slots__ = ['ref', 'id']

    def __init__(self, data=None):
        for key in RefDict.__slots__:
            self[key] = ''
        if isinstance(data, dict):
            self.update(data)


class DBRefField(CompositeField):
    '''
    A field wrapper around MongoDB reference fields
    '''
    _data_type = RefDict
    _python_type = DBRef
    ERRORS = {
        'missing_id': 'Referenced model does not have the _id attribute',
        'invalid_id': 'Referenced model has an empty or invalid _id'
    }

    def __init__(self, model_class, **kwargs):
        super(DBRefField, self).__init__(**kwargs)
        if isinstance(model_class, (ModelMeta, MongoCollectionMixin)):
            self.model_class = model_class
        else:
            raise TypeError("DBRefField: Expected a model of the type '{}'.".format(model_class.__name__))

    def _import(self, value):
        if value is None:
            return None
        if isinstance(value, self.model_class):
            if not hasattr(value, '_id'):
                raise ValueError(self._errors['missing_id'])
            if value._id is None or value._id.is_valid(str(value._id)) is False:
                raise ValueError(self._errors['invalid_id'])

            return self._python_type(self.model_class.get_collection_name(), value._id)
        elif isinstance(value, self._python_type):
            return value
        elif isinstance(value, dict):
            return self._python_type(value['ref'], ObjectId(value['id']))

        raise ValueError(self._errors['to_python'])

    def _export(self, value):
        if value is None:
            return None
        if isinstance(value, self.model_class):
            if not hasattr(value, '_id'):
                raise ValueError(self._errors['missing_id'])
            if value._id is None or value._id.is_valid(str(value._id)) is False:
                raise ValueError(self._errors['invalid_id'])

            return self._data_type({
                'ref': value.get_collection_name(),
                'id': value._id
            })
        elif isinstance(value, self._python_type):
            return self._data_type({
                'ref': value.collection,
                'id': str(value.id)
            })
        raise ValueError(self._errors['to_data'])

