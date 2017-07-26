#!/usr/bin/env python
# encoding: utf-8

from collections import OrderedDict
from .fields import BaseField


class ModelMeta(type):
    '''Metaclass for Model'''
    def __new__(mcs, name, bases, attrs):
        fields = OrderedDict()

        for key, value in attrs.items():
            if isinstance(value, BaseField):
                fields[key] = value

        attrs['_fields'] = fields
        cls = super(ModelMeta, mcs).__new__(mcs, name, bases, attrs)
        for name, field in fields.items():
            field.add_to_class(cls, name)
        return cls


class Model(object, metaclass=ModelMeta):

    def __init__(self, data=None, **kwargs):
        self._data = self._convert(data)

    def __repr__(self):
        return '<%s instance>' % self.__class__.__name__

    def to_data(self):
        data = {}
        for field_name, field in self._fields.items():
            if field_name in self._data:
                data[field_name] = field.to_data(self._data[field_name])
        return data

    def to_python(self):
        return self._convert(self._data)

    def _convert(self, data):
        converted_data = {}
        for name, field in self._fields.items():
            
            converted_data[name] = field.to_python(data[name])
        return converted_data

    @classmethod
    def _export(self, data):
        pass

