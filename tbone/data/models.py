#!/usr/bin/env python
# encoding: utf-8

import asyncio
from copy import deepcopy
from collections import OrderedDict
from .fields import BaseField
from functools import wraps


class ModelMeta(type):
    '''Metaclass for Model'''
    @classmethod
    def __prepare__(mcl, name, bases):
        ''' Adds the export decorator so member methods can be decorated for export '''
        def export(func):
            func._export_method_ = True

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper
        d = dict()
        d['export'] = export
        return d

    def __new__(mcl, name, bases, attrs):
        del attrs['export']
        fields = OrderedDict()
        exports = OrderedDict()

        # get model fields and exports from base classes
        for base in reversed(bases):
            if hasattr(base, '_fields'):
                fields.update(deepcopy(base._fields))

            if hasattr(base, '_exports'):
                exports.update(deepcopy(base._exports))

        # collect all defined fields and export methods
        for key, value in attrs.items():
            if getattr(value, '_export_method_', None):
                exports[key] = value

            if isinstance(value, BaseField):
                fields[key] = value

        attrs['_fields'] = fields
        attrs['_exports'] = exports
        cls = super(ModelMeta, mcl).__new__(mcl, name, bases, attrs)
        for name, field in fields.items():
            field.add_to_class(cls, name)
        return cls


class ModelSerializer(object):
    ''' Mixin class for adding nonblocking serialization methods '''
    async def _execute(self, func, *args, **kwargs):
        ''' Helper method to execute methods if they're coroutines  '''
        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        return func(*args, **kwargs)

    async def to_data(self):
        '''
        Returns a serialized from of the model as a dictionary with data primitives as values.
        Includes export methods and projection rules
        '''
        return await self._serialize(native=False)

    async def to_python(self):
        '''
        Returns a serialized from of the model as a dictionary with Python variables as values.
        Includes export methods and projection rules
        '''
        return await self._serialize(native=True)

    async def _serialize(self, native=True, exports=True, projection=True):
        data = {}
        # iterate through all fields
        for field_name, field in self._fields.items():
            # serialize field data
            raw_data = self._data.get(field_name)
            if native:
                field_data = await self._execute(field.to_python, raw_data)
            else:
                field_data = await self._execute(field.to_data, raw_data)

            # add field's data to model data based on projection settings
            if field_data and field._projection != None:
                data[field_name] = field_data
            elif field_data is None and field._projection == True:
                data[field_name] = None

        # iterate through all export methods
        for name, func in self._exports.items():
            data[name] = await func(self)
        return data


class Model(ModelSerializer, metaclass=ModelMeta):
    '''
    Base class for all data models. This is the heart  of the ODM.
    Provides field declaration and export methods.

    Example:

    .. code-block:: python

        class Person(Model):
            first_name = StringField()
            last_name = StringField()

    '''

    def __init__(self, data={}, **kwargs):
        self._data = {}
        if bool(data):
            self.import_data(data)
            self.validate()

    def __repr__(self):
        return '<%s instance>' % self.__class__.__name__

    def __iter__(self):
        ''' Implements iterator on model matching only fields with data matching them '''
        return (key for key in self._fields if key in self._data)

    @classmethod
    def fields(cls):
        return list(iter(cls._fields))

    def items(self):
        return [(field, self._data[field]) for field in self]

    def __eq__(self, other):
        ''' Override equal operator to compare field values '''
        if self is other:
            return True
        if type(self) is not type(other):
            return NotImplemented

        for k in self:
            if getattr(self, k) != getattr(other, k):
                return False
        return True

    def _validate(self, data):
        ''' Internal method to run validation with all model fields given the data provided '''
        for name, field in self._fields.items():
            field.validate(data.get(name))

    def validate(self):
        ''' calls internal validate method with model's existing data '''
        self._validate(self._data)

    def _convert(self, data, native=True):
        converted_data = {}
        for name, field in self._fields.items():
            if native is True:
                converted_data[name] = field.to_python(data.get(name))
            else:
                converted_data[name] = field.to_data(data.get(name))
        return converted_data

    def import_data(self, data: dict):
        '''
        Imports data into model and converts to python form.
        Merges with existing if data is partial
        '''
        if not isinstance(data, dict):
            raise ValueError('Cannot import data not as dict')
        self._data.update(data)
        self._data = self._convert(self._data)

    def export_data(self, native):
        '''
        Export the model into a dictionary.
        This method does not include projection rules and export methods
        '''
        return self._convert(self._data, native)
