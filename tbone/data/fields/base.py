#!/usr/bin/env python
# encoding: utf-8

from collections import OrderedDict
from functools import wraps

__all__ = ['BaseField']


class Ternary(object):
    ''' A class for managing a ternary object with 3 possible states '''

    def __init__(self, value=None):
        if any(value is v for v in (True, False, None)):
            self.value = value
        else:
            raise ValueError('Ternary value must be True, False, or None')

    def __eq__(self, other):
        return (self.value is other.value if isinstance(other, Ternary)
                else self.value is other)

    def __ne__(self, other):
        return not self == other

    def __bool__(self):
        raise TypeError('Ternary object may not be used as a Boolean')

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return "Ternary(%s)" % self.value


class FieldDescriptor(object):
    '''
    ``FieldDescriptor`` for exposing fields to allow access to the underlying data
    '''

    def __init__(self, field):
        self.field = field

    def __get__(self, instance, instance_type=None):
        if instance is not None:
            return instance._data.get(self.field.name, None) or self.field.default
        return self.field

    def __set__(self, instance, value):
        instance._data[self.field.name] = value

    def __delete__(self, instance):
        del instance._data[self.name]


class FieldMeta(type):
    '''
    Meta class for BaseField. Accumulated error messages and validator methods
    '''
    @classmethod
    def __prepare__(mcl, name, bases):
        ''' Adds the validator decorator so member methods can be decorated as validation methods '''
        def validator(func):
            func._validation_method_ = True

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper
        d = dict()
        d['validator'] = validator
        return d

    def __new__(mcl, name, bases, attrs):
        del attrs['validator']
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

        # store validators - locate member methods which are decorated as validator functions
        for key, attr in attrs.items():
            if getattr(attr, '_validation_method_', None):
                validators[key] = attr

        attrs['_validators'] = validators

        return super(FieldMeta, mcl).__new__(mcl, name, bases, attrs)


class BaseField(object, metaclass=FieldMeta):
    '''
    Base class for all fields in TBone models. Added to subclasses of ``Model`` to define the model's schema.

    :param required:
        Invalidates the field of no data is provided.
        Default: None

    :param default:
        Provides a default value when none is provided. Can be a callable
        Default: None

    :param choices:
        Used to limit a field's choices of value.
        Requires a list of acceptable values.
        If not ``None`` validates the value against a the provided list.

    :param validators:
        An optional list of validator functions. Requires a list of calllables.
        Used for validation functions which are not implemented as internal ``Field`` methods

    :param projection:
        Determines if the field is serlized by the model using either ``to_python`` or ``to_data`` methods.
        Useful when specific control over the model behavior is required.
        Acceptable values are ``True``, ``False`` and ``None``.
        Using ``True`` implies the field will always be serialized
        Using ``False`` implies the field will be serialized only if the value is not ``None``
        Using ``None`` implies the field will never be serialized

    :param readonly:
        Determines if the field can be overriden using the ``deserialize`` method.
        Has no effect on direct data manipulation

    :param primary_key:
        Declares the field as the model's primary key. Only one field can be declared like so.
        This declaration has no impact on the datastore, and is used by the ``Resource`` class as the model's identifier.
        If the model is also mixed with a persistency class, it would make sense that the field which 
        is defined as the primary key may also be indexed as unique
    '''
    data_type = None
    python_type = None

    ERRORS = {
        'required': 'This is a required field',
        'to_data': 'Cannot coerce data to primitive form',
        'to_python': 'Cannot corece data to python type',
        'choices': 'Value must be one of [{0}] in field {1}',
    }

    def __init__(self, required=False, default=None, choices=None,
                 validators=None, projection=True, readonly=False,
                 primary_key=False, **kwargs):
        super(BaseField, self).__init__()

        self._required = required
        self._default = default
        self._choices = choices
        self._projection = Ternary(projection)
        self._readonly = readonly
        self._primary_key = primary_key
        if primary_key:
            self._required = True
        self._bound = False                         # Whether the Field is bound to a Model

        if required and default is not None:
            raise AttributeError('Required and default cannot co-exist')

        # accumulate all validators to a single list
        self.validators = [getattr(self, name) for name in self._validators]
        if isinstance(validators, list):
            for validator in validators:
                if callable(validator):
                    self.validators.append(validator)

    def _export(self, value):
        '''
        Coerce the input data to primitive form
        Override in sub classes to add specialized behavior
        '''
        if value is None:
            if self._required:
                raise ValueError(self._errors['required'])
            return None
        return self.data_type(value)

    def _import(self, value):
        '''
        Imports field data and coerce to the field's python type.
        Overrride in sub classes to add specialized behavior
        '''
        return self.python_type(value)

    def to_data(self, value):
        '''
        Coerce python data type to simple form for serialization.
        If default value was defined returns the default value if None was passed
        '''
        if value is None and self._default is not None:
            return self.default
        try:
            value = self._export(value)
        except ValueError as ex:
            raise Exception(ex, self._errors['to_data'])
        return value

    def to_python(self, value):
        '''
        Coerce data from primitive form to native Python types.
        Returns the default type (if exists)
        '''
        if value is None and self._default is not None:
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
        ``FieldDescriptor``. Called by the metaclass during construction of the
        ``Model``.
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

    @validator
    def choices(self, value):
        if self._choices:
            if value not in self._choices and value is not None:
                raise ValueError(
                    self._errors['choices'].format(
                        ', '.join([str(x) for x in self._choices]), getattr(self, 'name', None)
                    )
                )
