#!/usr/bin/env python
# encoding: utf-8

from .base import BaseField, FieldMeta


class CompositeField(BaseField):
    def _init_field(self, field_class, options):
        '''
        Instantiate the inner field that represents each element within this composite type.
        In case the inner field is itself a composite type, its inner field can be provided
        as the ``nested_field`` keyword argument.
        '''
        if not isinstance(field_class, BaseField):
            nested_field = options.pop('nested_field', None)
            if nested_field:
                field = field_class(field_class=nested_field, **options)
            else:
                field = field_class(**options)
        return field


class ListField(CompositeField):
    data_type = list
    python_type = list
    
    def __init__(self, field_class, min_size=None, max_size=None, **kwargs):
        if isinstance(field_class, FieldMeta):
            self.field_class = field_class
        else:
            raise TypeError("'{}' is not of type BaseField".format(field_class.__class__.__name__))

        self.field = self._init_field(field_class, kwargs)
        self.min_size = min_size
        self.max_size = max_size
        super(ListField, self).__init__(**kwargs)


# class ModelField(CompositeField):
#     """A field that can hold an instance of the specified model."""

#     data_type = dict

#     def __init__(self, model_class, **kwargs):
#         if isinstance(model_class, ModelMeta):
#             self.model_class = model_class
#             self.model_name = self.model_class.__name__
#         else:
#             raise TypeError("ModelField: Expected a model of the type '{}'.".format(model_class.__class__.__name__))

#     @property
#     def python_type(self):
#         return self.model_class

#     @property
#     def fields(self):
#         return self.model_class.fields

#     def to_python(self, value):
#         pass

#     def to_data(self, value):
#         return self.model_class





