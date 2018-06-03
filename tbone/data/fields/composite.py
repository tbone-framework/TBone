#!/usr/bin/env python
# encoding: utf-8

import asyncio
from collections import Iterable
from .base import BaseField, FieldMeta
from ..models import ModelMeta


class CompositeField(BaseField):
    '''
    Base class for fields which accept another field as parameter
    '''

    def __init__(self, **kwargs):
        super(CompositeField, self).__init__(**kwargs)
        self._is_composite = True


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
            raise TypeError("'{}' is not a field or type of field".format(
                field.__class__.__qualname__))

    def _import(self, value_list):
        if value_list is None:
            return None
        if not isinstance(value_list, list):
            raise ValueError('Data is not of type list')
        data = []
        for value in value_list:
            data.append(self.field.to_python(value))
        return data

    def _export(self, value_list):
        if value_list is None:
            return None
        if not isinstance(value_list, list):
            raise ValueError('Data is not of type list')
        data = []
        for value in value_list:
            data.append(self.field.to_data(value))
        return data

    async def serialize(self, value_list: list, native=False) -> list:
        if value_list is None:
            return None

        if not isinstance(value_list, list):
            raise ValueError('Data is not of type list')

        futures = []
        for value in value_list:
            futures.append(self.field.serialize(value))
        return await asyncio.gather(*futures)


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
            raise TypeError("'{}' is not a field or type of field".format(
                field.__class__.__qualname__))

    def _export(self, associative):
        if associative is None:
            return None
        if not isinstance(associative, dict):
            raise ValueError('Data is not of type dict')

        data = {}
        for key, value in associative.items():
            data[key] = self.field.to_data(value)

        return data

    def _import(self, associative):
        if associative is None:
            return None
        if not isinstance(associative, dict):
            raise ValueError('Data is not of type dict')

        data = {}
        for key, value in associative.items():
            data[key] = self.field.to_python(value)

        return data

    async def serialize(self, associative: dict, native=False) -> dict:
        if associative is None:
            return None

        if not isinstance(associative, dict):
            raise ValueError('Data is not of type dict')

        tasks = {}
        for key, value in associative.items():
            tasks[key] = self.field.serialize(value)

        async def mark(key, future):
            return key, await future

        return {
            key: result
            for key, result in await asyncio.gather(
                *(mark(key, future) for key, future in tasks.items())
            )
        }

        # return await asyncio.gather(*futures)


class ModelField(CompositeField):
    '''
    A field that can hold an instance of the specified model
    '''
    _data_type = dict

    def __init__(self, model_class, **kwargs):
        super(ModelField, self).__init__(**kwargs)
        if isinstance(model_class, ModelMeta):
            self._model_class = model_class
        else:
            raise TypeError(
                "ModelField: Expected a model of the type '{}'.".format(model_class.__name__))

    def __repr__(self):
        return '<%s instance of type %s>' % (self.__class__.__qualname__, self._python_type.__name__)

    @property
    def _python_type(self):
        return self._model_class

    @property
    def fields(self):
        return self.model_class.fields

    def to_python(self, value):
        # create a model instance from data
        instance = super(ModelField, self).to_python(value)
        if instance is None:
            return None
        return instance.export_data(native=True)

    def _import(self, value):
        if isinstance(value, self._python_type):
            return value
        elif isinstance(value, dict):
            return self._python_type(value)
        elif value is None:  # no data was passed
            return None
        else:
            raise ValueError('Cannot convert type {} to {}'.format(
                type(value), self._python_type.__name__))

    def _export(self, value):
        if isinstance(value, self._python_type):
            return value.export_data(native=False)
        elif isinstance(value, dict):
            return self._python_type(value).export_data(native=False)
        elif value is None:  # no data was passed
            return None
        else:
            raise ValueError('Cannot convert type {} to {}'.format(
                type(value), self._python_type.__name__))

    async def serialize(self, value, native=False):
        # create a model instance from data
        instance = super(ModelField, self).to_python(value)
        if instance is None:
            return None
        # return the model's serialization
        dd = await instance.serialize(native)
        return dd


class PolyModelField(CompositeField):
    '''
    A field that can hold an instance of the one of the specified models
    '''
    _data_type = dict

    def __init__(self, model_classes, **kwargs):
        super(PolyModelField, self).__init__(**kwargs)
        if isinstance(model_classes, ModelMeta):
            self._model_classes = (model_classes,)
        elif isinstance(model_classes, Iterable):
            self._model_classes = {model.__name__: model for model in model_classes}
        else:
            raise TypeError("PolyModelField: Expected a model of the type '{}'.".format(
                self._model_classes.keys()))

    @property
    def _python_type(self):
        return tuple(self._model_classes.values())

    def _export(self, value):
        # TODO:   use if isinstance(value, self._python_type) to allow inheritance
        if value is None:
            return None
        elif value.__class__ in self._python_type:
            return{
                'type': type(value).__name__,
                'data': value.export_data(native=False)
            }
        else:
            raise ValueError('Cannot convert type {} to  on of the types in {}'.format(
                type(value), self._python_type))

    def _import(self, value):
        if isinstance(value, self._python_type):
            return value
        elif isinstance(value, dict):
            model_class = self._model_classes[value['type']]
            return model_class(value['data'])
        elif value is None:  # no data was passed
            return None
        else:
            raise ValueError('Cannot convert type {} to {}'.format(
                type(value), self._python_type.__name__))
