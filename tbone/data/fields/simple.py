#!/usr/bin/env python
# encoding: utf-8

import datetime
import dateutil.parser
from .base import BaseField


class StringField(BaseField):
    ''' Unicode string field '''
    _data_type = str
    _python_type = str


class NumberField(BaseField):

    ERRORS = {
        'min': "Value should be greater than or equal to {0}.",
        'max': "Value should be less than or equal to {0}.",
    }

    def __init__(self, min=None, max=None, **kwargs):
        self.min = min
        self.max = max
        super(NumberField, self).__init__(**kwargs)

    @validator
    def range(self, value):
        if self.min is not None and value < self.min:
            raise ValueError(self._errors['min'].format(self.min))

        if self.max is not None and value > self.max:
            raise ValueError(self._errors['max'].format(self.max))

        return value


class IntegerField(NumberField):
    '''
    A field that validates input as an Integer
    '''
    _data_type = int
    _python_type = int


class FloatField(NumberField):
    '''
    A field that validates input as an Integer
    '''
    _data_type = float
    _python_type = float
    # TODO: add field attribute to determine the number of digits after the dot


class BooleanField(BaseField):

    '''A boolean field type. In addition to ``True`` and ``False``, coerces these
    values:
    + For ``True``: "True", "true", "1"
    + For ``False``: "False", "false", "0"

    '''
    _data_type = bool
    _python_type = bool


class DTBaseField(BaseField):
    ''' Base field for all fields related to date and time '''
    _data_type = str

    def to_data(self, value):
        if value is None:
            if self._default is not None:
                value = self.default
            return None
        return value.isoformat()

    def _import(self, value):
        if value is None:
            return None
        elif isinstance(value, self._python_type) or isinstance(value, datetime.datetime):
            return value
        elif isinstance(value, str):
            return dateutil.parser.parse(value)
        raise ValueError('{0} Unacceptable type for {1} field'.format(value.__class__.__name__, self._python_type.__name__))


class TimeField(DTBaseField):
    ''' Date field, exposes datetime.date as the python field '''
    _python_type = datetime.time

    def _import(self, value):
        if isinstance(value, self._python_type):
            return value
        dt = super(TimeField, self)._import(value)
        return None if dt is None else dt.time()


class DateField(DTBaseField):
    ''' Date field, exposes datetime.date as the python field '''
    _python_type = datetime.date

    def _import(self, value):
        if isinstance(value, self._python_type):
            return value
        dt = super(DateField, self)._import(value)
        return None if dt is None else dt.date()


class DateTimeField(DTBaseField):
    ''' Date field, exposes datetime.datetime as the python field '''
    _python_type = datetime.datetime


