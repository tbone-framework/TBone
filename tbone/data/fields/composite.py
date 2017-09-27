#!/usr/bin/env python
# encoding: utf-8

from .base import BaseField, FieldMeta
from ..models import ModelMeta


class CompositeField(BaseField):
    '''
    Base class for fields which accept another field as parameter
    '''
    def __init__(self, **kwargs):
        super(CompositeField, self).__init__(**kwargs)
        self._is_composite = True

    @property
    def is_composite(self):
        return self._is_composite


class ListField(CompositeField):
    _data_type = list
    _python_type = list

    def __init__(self, field, min_size=None, max_size=None, **kwargs):
        super(ListField, self).__init__(**kwargs)
        self.min_size = min_size
        self.max_size = max_size
        # the provided field can be a field class or field instance
        if isinstance(field, FieldMeta):  # a field type was passed
            self.field = field()
        elif isinstance(field, BaseField):  # an instance of field was passed
            self.field = field
        elif isinstance(field, ModelMeta):  # we're being nice
            raise TypeError('To define a list of models, use ListField(ModelField(...))')
        else:
            raise TypeError("'{}' is not a field or type of field".format(field.__class__.__qualname__))

    def _export(self, value):
        if value is None:
            return None
        return self._data_type(value)

    def _import(self, value):
        if value is None:
            return None
        return self._python_type(value)

    def to_data(self, value_list):
        if value_list is None:
            if self._default is not None:
                return self.default
            return None
        if not isinstance(value_list, list):
            raise ValueError('Data is not of type list')
        data = []
        for value in value_list:
            data.append(self.field.to_data(value))
        return data

    def to_python(self, value_list):
        if value_list is None:
            if self._default is not None:
                return self.default
            return None
        if not isinstance(value_list, list):
            raise ValueError('Data is not of type list')
        data = []
        for value in value_list:
            data.append(self.field.to_python(value))
        return data

class DictField(CompositeField):
    _data_type = dict
    _python_type = dict

    def __init__(self, field, **kwargs):
        super(DictField, self).__init__(**kwargs)
        # the provided field can be a field class or field instance
        if isinstance(field, FieldMeta):  # a field type was passed
            self.field = field()
        elif isinstance(field, BaseField):  # an instance of field was passed
            self.field = field
        else:
            raise TypeError("'{}' is not a field or type of field".format(field.__class__.__qualname__))

    def _export(self, value):
        if value is None:
            return None
        return self._data_type(value)

    def _import(self, value):
        if value is None:
            return None
        return self._python_type(value)

    def to_data(self, associative):
        if associative is None:
            return None
        if not isinstance(associative, dict):
            raise ValueError('Data is not of type dict')

        data = {}
        for key, value in associative.items():
            data[key] = self.field.to_data(value)

        return data

    def to_python(self, associative):
        if associative is None:
            return None
        if not isinstance(associative, dict):
            raise ValueError('Data is not of type dict')

        data = {}
        for key, value in associative.items():
            data[key] = self.field.to_python(value)

        return data


class ModelField(CompositeField):
    '''
    A field that can hold an instance of the specified model
    '''
    _data_type = dict

    def __init__(self, model_class, **kwargs):
        super(ModelField, self).__init__(**kwargs)
        if isinstance(model_class, ModelMeta):
            self.model_class = model_class
        else:
            raise TypeError("ModelField: Expected a model of the type '{}'.".format(model_class.__name__))

    def __repr__(self):
        return '<%s instance of type %s>' % (self.__class__.__qualname__, self.model_class.__name__)

    @property
    def _python_type(self):
        return self.model_class

    @property
    def fields(self):
        return self.model_class.fields

    def to_python(self, value):
        if isinstance(value, self.model_class):
            return value.export_data(native=True)
        elif isinstance(value, dict):
            m = self.model_class(value)
            return m.export_data(native=True)
        else:
            raise ValueError('Cannot convert type {} to {}'.format(type(value), self.model_class.__name__))

    def to_data(self, value):
        if isinstance(value, self.model_class):
            return value.export_data(native=False)
        elif isinstance(value, dict):
            m = self.model_class(value)
            return m.export_data(native=False)
        else:
            raise ValueError('Cannot convert type {} to {}'.format(type(value), self.model_class.__name__))


