#!/usr/bin/env python
# encoding: utf-8

from collections import OrderedDict
from .fields import BaseField
from functools import wraps


class ModelMeta(type):
    '''Metaclass for Model'''
    @classmethod
    def __prepare__(mcl, name, bases):
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


class Model(object, metaclass=ModelMeta):

    def __init__(self, data={}, **kwargs):
        self._data = {}
        if bool(data):
            self.import_data(data)
            self.validate()


    def __repr__(self):
        return '<%s instance>' % self.__class__.__name__

    def to_data(self):
        '''
        Convert all data in model from python data types to simple form for serialization.

        '''
        data = {}
        # iterate through all fields 
        for field_name, field in self._fields.items():
            field_data = field.to_data(self._data.get(field_name))
            if field_data:
                data[field_name] = field_data
            elif field._export_if_none is True:
                data[field_name] = None

        # iterate through all exports
        for name, func in self._exports.items():
            data[name] = func(self)

        return data

    def to_python(self):
        return self._convert(self._data)

    def _validate(self, data):
        ''' Internal method to run validation with all model fields given the data provided '''
        for name, field in self._fields.items():
            field.validate(data.get(name))

    def validate(self):
        ''' calls internal validate method with model's existing data '''
        self._validate(self._data)

    def _convert(self, data):
        ''' Converts given data from primitive form to Python variables and objects '''
        converted_data = {}
        for name, field in self._fields.items():
            converted_data[name] = field.to_python(data.get(name))
        return converted_data

    def import_data(self, data):
        self._data = self._convert(data)

    @classmethod
    def _export(self, data):
        pass

