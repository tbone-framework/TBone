#!/usr/bin/env python
# encoding: utf-8


class FieldDescriptor(object):
    '''
    Descriptor for exposing fields to allow access to the underlying data
    '''
    def __init__(self, field):
        self.field = field

    def __get__(self, instance, instance_type=None):
        if instance is not None:
            return instance._data.get(self.field.name)
        return self.field

    def __set__(self, instance, value):
        instance._data[self.field.name] = value

    def __delete__(self, instance):
        del instance._data[self.name]


class FieldMeta(type):
    def __new__(mcs, name, bases, attrs):
        errors = {}
        for base in reversed(bases):
            if hasattr(base, 'ERRORS'):
                errors.update(base.ERRORS)

        if 'ERRORS' in attrs:
            errors.update(attrs['ERRORS'])
        # store commined error messages of all field class and its bases
        attrs['_errors'] = errors

        return super(FieldMeta, mcs).__new__(mcs, name, bases, attrs)


class BaseField(object, metaclass=FieldMeta):
    '''
    Base class for all model types
    '''
    data_type = None
    python_type = None

    ERRORS = {
        'required': 'This is a required field',
        'to_data': 'Cannot coerce data to primitive form',
        'to_python': 'Cannot corece data to python type'
    }

    def __init__(self, required=True, default=None, **kwargs):
        super(BaseField, self).__init__()

        self.required = required
        self._default = default
        self._bound = False         # Whether the Field is bound to a Model

    def to_data(self, value):
        ''' Export native data type to simple form for serialization'''
        try:
            value = self.data_type(value)
        except ValueError:
            raise Exception(self._errors['to_data'])
        return value

    def to_python(self, value):
        ''' Import data from primitive form to native Python types'''
        if not isinstance(value, self.python_type):
            try:
                value = self.python_type(value)
            except ValueError:
                raise Exception(self._errors['to_python'])
        return value

    def __call__(self, value):
        return self.to_python(value)

    @property
    def default(self):
        default = self._default
        if callable(default):
            default = default()
        return default

    def add_to_class(self, model_class, name):
        '''
        Hook that replaces the `Field` attribute on a class with a named
        `FieldDescriptor`. Called by the metaclass during construction of the
        `Model`.
        '''
        self.name = name
        self.model_class = model_class
        # model_class._meta.add_field(self)
        setattr(model_class, name, FieldDescriptor(self))
        self._bound = True
