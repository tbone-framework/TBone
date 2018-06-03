#!/usr/bin/env python
# encoding: utf-8

import asyncio
from copy import deepcopy
from collections import OrderedDict
from .fields import BaseField
from functools import wraps


class ModelOptions(object):
    '''
    A configuration class for data Models. Provides all the defaults and
    allows overriding inside the model's definition using the ``Meta`` class
    :param name:
        The name of the data model.
        Persistency mixins use this to determine the name of the data collection in the datastore.
        Defaults to the class's name with ``None``.

    :param namespace:
        Defines a namespace for the model name. Used by persistency mixins to prepend to the collection's name

    :param exclude_fields:
        Exclude fields inherited by one of the base classes of the model.
        Useful for creating similar models with small differences in fields

    :param exclude_serialize_methods:
        Exclude serialize methods inherited by one of the base classes of the model.
        Useful for creating similar models with small differences in serialize methods

    :param concrete:
        Defines the model as concrete and not abstract. This is useful for persistency mixins to determine
        if the model should be created in the database.
    :type concrete:
        Boolean - Default is ``True``

    :param creation_args:
        Used when creating a MongoDB collection for passing creation arguments

    :param indices:
        Used for definding database indices
    '''
    name = None
    namespace = None
    concrete = True
    exclude_fields = []
    exclude_serialize = []
    creation_args = {}
    indices = []

    def __init__(self, meta=None):
        if meta:
            for attr in dir(meta):
                if not attr.startswith('_'):
                    setattr(self, attr, getattr(meta, attr))


class ModelMeta(type):
    '''Metaclass for Model'''
    @classmethod
    def __prepare__(mcl, name, bases):
        ''' Adds the ``serialize`` decorator so member methods can be decorated for serialization '''
        def serialize(func):
            func._serialize_method_ = True

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper
        d = dict()
        d['serialize'] = serialize
        return d

    def __new__(mcl, name, bases, attrs):
        del attrs['serialize']
        fields = OrderedDict()
        serialize_methods = OrderedDict()

        # get model fields and exports from base classes
        for base in reversed(bases):
            if hasattr(base, '_fields'):
                fields.update(deepcopy(base._fields))  # copy all fields
                # remove excludes
                if 'Meta' in attrs and hasattr(attrs['Meta'], 'exclude_fields'):
                    ex = attrs['Meta'].exclude_fields
                    for f in ex:
                        if f in fields:
                            del fields[f]

            if hasattr(base, '_serialize_methods'):
                serialize_methods.update(deepcopy(base._serialize_methods))
                # remove excludes
                if 'Meta' in attrs and hasattr(attrs['Meta'], 'exclude_serialize'):
                    ex = attrs['Meta'].exclude_serialize
                    for f in ex:
                        if f in serialize_methods:
                            del serialize_methods[f]

        # collect all defined fields and export methods
        for key, value in attrs.items():
            if hasattr(value, '_serialize_method_'):
                serialize_methods[key] = value

            if isinstance(value, BaseField):
                fields[key] = value

        attrs['_fields'] = fields
        attrs['_serialize_methods'] = serialize_methods

        # create class
        cls = super(ModelMeta, mcl).__new__(mcl, name, bases, attrs)
        # apply field descriptors
        for name, field in fields.items():
            field.add_to_class(cls, name)
            if field._primary_key:
                # assign primary key information
                cls.primary_key = field.name
                cls.primary_key_type = field._python_type

        # add model options
        opts = getattr(cls, 'Meta', None)
        cls._meta = ModelOptions(opts)

        return cls


class ModelSerializer(object):
    '''
    Mixin class for adding nonblocking serialization methods.
    Provides serialization methods to data primitives and to python types.
    Performs serialization taking into account projection attributes and serialize methods
    '''
    async def serialize(self, native=False):
        '''
        Returns a serialized from of the model taking into account projection rules and ``@serialize`` decorated methods.
        
        :param native:
            Deternines if data is serialized to Python native types or primitive form. Defaults to ``False``
        '''
        data = {}
        # iterate through all fields
        for field_name, field in self._fields.items():
            # serialize field data
            raw_data = self._data.get(field_name)
            # add field's data to model data based on projection settings
            if field._projection != None:  # noqa E711
                field_data = await field.serialize(raw_data, native)
                if field_data:
                    data[field_name] = field_data
                elif field._projection == True: # noqa E711
                    data[field_name] = None

        # iterate through all export methods
        for name, func in self._serialize_methods.items():
            data[name] = await func(self)
        return data

    async def deserialize(self, data: dict, silent=True):
        '''
        Deserializes a Python ``dict`` into the model by assigning values to their respective fields.
        Ignores data attributes that do not match one of the Model's fields.
        Ignores data attributes who's matching fields are declared with the ``readonly`` attribute
        Validates the data after import.
        Override in sub classes to modify or add to deserialization behavior

        :param data:
            Python dictionary with data
        :type data:
            ``dict``
        :param silent:
            Determines if an exception is thrown if illegal fields are passed. Such fields can be non existent or readonly. Default is True
        :type silent:
            ``bool``
        '''
        self.import_data(self. _deserialize(data))
        self.validate()

    def _deserialize(self, data: dict, silent=True) -> dict:
        ''' Internal deserialize method for sifting out unacceptable data for the model '''
        deserialized_data = {}
        for name, field in self._fields.items():
            if field._readonly is False and name in data:
                deserialized_data[name] = data.get(name)
        return deserialized_data


class Model(ModelSerializer, metaclass=ModelMeta):
    '''
    Base class for all data models. This is the heart of the ODM.
    Provides field declaration and export methods implementations.

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
        desc = self.description()
        if desc is None:
            return '<%s instance>' % self.__class__.__name__
        return '<%s instance: %s>' % (self.__class__.__name__, desc)

    def __iter__(self):
        ''' Implements iterator on model matching only fields with data matching them '''
        return (key for key in self._fields if key in self._data)

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

    def description(self):
        '''
        Adds an instance description to the class's ``repr``.
        Override in sub classes to provide desired functionality
        '''
        return None

    @classmethod
    def fields(cls):
        # return list(iter(cls._fields))
        return iter(cls._fields)

    def items(self):
        return [(field, self._data[field]) for field in self]

    @classmethod
    def _validate(cls, data):
        try:
            for name, field in cls._fields.items():
                field.validate(data.get(name))
        except Exception as ex:
            raise Exception('Failed to validate field "{}" model "{}"'.format(name, cls.__name__), ex)

    def validate(self):
        '''
        Performs model data validation by iterating through all model fields
        and validating the field's data according to the field's internal validation rules or
        validation methods provided during model declaration
        '''
        self._validate(self._data)

    def _convert(self, data, native):
        converted_data = {}
        for name, field in self._fields.items():
            value = data.get(name)
            if value is None and field._export_if_none is False:
                continue
            if native is True:
                conversion_func = field.to_python
            else:
                conversion_func = field.to_data
            converted_data[name] = conversion_func(value)
        return converted_data

    def import_data(self, data: dict):
        '''
        Imports data into model and converts to python form.
        Model fields and container of model fields retain their model class structure.
        Merges with existing if data is partial
        '''
        if not isinstance(data, dict):
            raise ValueError('Cannot import data not as dict')
        self._data.update(data)

        for name, field in self._fields.items():
            self._data[name] = field._import(self._data.get(name)) or field.default

    def export_data(self, native=True):
        '''
        Export the model into a dictionary.
        This method does not include projection rules and export methods
        '''
        return self._convert(self._data, native)
