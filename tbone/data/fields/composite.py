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
        self.is_composite = True

class ListField(CompositeField):
    data_type = list
    python_type = list
    
    def __init__(self, field, min_size=None, max_size=None, **kwargs):
        super(ListField, self).__init__(**kwargs)
        self.min_size = min_size
        self.max_size = max_size
        # the provided field can be a field class or field instance
        if isinstance(field, FieldMeta):  # a field type was passed
            self.field = field()
        elif isinstance(field, BaseField):  # an instance of field was passed
            self.field = field
        else:
            raise TypeError("'{}' is not a field or type of field".format(field.__class__.__name__))

    def _export(self, value):
        if value is None:
            return None
        return self.data_type(value)

    def _import(self, value):
        if value is None:
            return None
        return self.python_type(value)

    def to_data(self, value_list):
        if value_list is None:
            return None
        if not isinstance(value_list, list):
            raise ValueError('Data is not of type list')

        data = []
        for value in value_list:
            data.append(self.field.to_data(value))

        return data


class ModelField(CompositeField):
    '''
    A field that can hold an instance of the specified model
    '''

    data_type = dict

    def __init__(self, model_class, **kwargs):
        if isinstance(model_class, ModelMeta):
            self.model_class = model_class
            self.model_name = self.model_class.__name__
        else:
            raise TypeError("ModelField: Expected a model of the type '{}'.".format(model_class.__class__.__name__))

        super(ModelField, self).__init__(**kwargs)

    @property
    def python_type(self):
        return self.model_class

    @property
    def fields(self):
        return self.model_class.fields

    def to_python(self, value):
        if isinstance(value, self.model_class):
            return value.to_python()
        elif isinstance(value, dict):
            m = self.model_class(value)
            return m.to_python()
        else:
            raise ValueError('Cannot convert type {} to {}'.format(type(value), self.model_class.__name__))

    def to_data(self, value):
        if isinstance(value, self.model_class):
            return value.to_data()
        elif isinstance(value, dict):
            m = self.model_class(value)
            return m.to_data()
        else:
            raise ValueError('Cannot convert type {} to {}'.format(type(value), self.model_class.__name__))



        m = self.model_class(value)
        return m.to_data()





