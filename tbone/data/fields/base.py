#!/usr/bin/env python
# encoding: utf-8

from collections import OrderedDict


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
    def __new__(mcl, name, bases, attrs):
        errors = {}
        validators = OrderedDict()

        # accumulate errors and validators from base classes
        for base in reversed(bases):
            if hasattr(base, '_errors'):
                errors.update(base._errors)
            if hasattr(base, '_validators'):
                validators.update(base._validators)

        if 'ERRORS' in attrs:
            errors.update(attrs['ERRORS'])
        # store commined error messages of all field class and its bases
        attrs['_errors'] = errors

        # store validators
        for name, attr in attrs.items():
            if name.startswith('validate_') and callable(attr):
                validators[name] = attr

        attrs['_validators'] = validators
        return super(FieldMeta, mcl).__new__(mcl, name, bases, attrs)


class BaseField(object, metaclass=FieldMeta):
    '''
    Base class for all model types
    '''
    data_type = None
    python_type = None

    ERRORS = {
        'required': 'This is a required field',
        'to_data': 'Cannot coerce data to primitive form',
        'to_python': 'Cannot corece data to python type',
        'choices': 'Value must be one of {0}',
    }

    def __init__(self, required=False, default=None, choices=None,
                 validators=None, export_if_none=True, **kwargs):
        super(BaseField, self).__init__()

        self._required = required
        self._default = default
        self._choices = choices
        self._export_if_none = export_if_none       # Whether the field should be exported when is None
        self._bound = False                         # Whether the Field is bound to a Model

        self.validators = [getattr(self, name) for name in self._validators]
        if isinstance(validators, list):
            for validator in validators:
                if callable(validator):
                    self.validators.append(validator)

    def _export(self, value):
        if value is None:
            if self._required:
                raise ValueError(self._errors['required'])
            return None
        return self.data_type(value)

    def _import(self, value):
        return self.python_type(value)

    def to_data(self, value):
        ''' 
        Export python data type to simple form for serialization.
        If default value was defined returns the default value if None was passed
        '''
        if value is None and self._default:
            return self.default
        try:
            value = self._export(value)
        except ValueError:
            raise Exception(self._errors['to_data'])
        return value

    def to_python(self, value):
        '''
        Import data from primitive form to native Python types.
        Returns the default type (if exists)
        '''
        if value is None and self._default:
            return self.default
        if not isinstance(value, self.python_type):
            try:
                value = self._import(value)
            except ValueError:
                raise Exception(self._errors['to_python'])
        return value

    def __call__(self, value):
        return self.to_python(value)

    def __repr__(self):
        if self._bound:
            return '<%s instance in model %s>' % (self.__class__.__qualname__, self.container_model_class.__name__)
        return '<%s instance>' % self.__class__.__qualname__

    @property
    def default(self):
        default = self._default
        if callable(default):
            default = default()
        return default

    def add_to_class(self, cls, name):
        '''
        Hook that replaces the `Field` attribute on a class with a named
        `FieldDescriptor`. Called by the metaclass during construction of the
        `Model`.
        '''
        self.name = name
        self.container_model_class = cls
        setattr(cls, name, FieldDescriptor(self))
        self._bound = True

    def validate(self, value):
        '''
        Run all validate functions pertaining to this field and raise exceptions.
        '''
        for validator in self.validators:
            validator(value)

    def validate_choices(self, value):
        if self._choices:
            if value not in self._choices:
                raise ValueError(self._errors['choices'].format(str(self._choices)))
