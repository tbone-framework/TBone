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

    def __init__(self, data={}, **kwargs):
        self._data = self._convert(data)

    def __repr__(self):
        return '<%s instance>' % self.__class__.__name__

    def to_data(self):
        data = {}
        for field_name, field in self._fields.items():
            if field_name in self._data:
                data[field_name] = field.to_data(self._data[field_name])
            elif field._export_if_none is True:
                data[field_name] = None
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
        converted_data = {}
        for name, field in self._fields.items():
            if name in data:  # data contains the field's name as key
                converted_data[name] = field.to_python(data[name])
            else:  # data does not contain the field's name
                d = field.default
                if d is not None:
                    converted_data[name] = field.to_python(d)
                else:
                    pass  # TODO: add serialized when None
        return converted_data

    @classmethod
    def _export(self, data):
        pass

