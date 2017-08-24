#!/usr/bin/env python
# encoding: utf-8

import datetime
import dateutil.parser
from .base import BaseField


class StringField(BaseField):
    ''' Unicode string field '''
    data_type = str
    python_type = str

    def _import(self, value):
        if value is None:
            return None
        return self.python_type(value)


class NumberField(BaseField):

    ERRORS = {
        'min': "Value should be greater than or equal to {0}.",
        'max': "Value should be less than or equal to {0}.",
    }

    def __init__(self, min=None, max=None, **kwargs):
        self.min = min
        self.max = max
        super(NumberField, self).__init__(**kwargs)

    def validate_range(self, value):
        if self.min is not None and value < self.min:
            raise ValueError(self._errors['min'].format(self.min))

        if self.max is not None and value > self.max:
            raise ValueError(self._errors['max'].format(self.max))

        return value


class IntegerField(NumberField):
    '''
    A field that validates input as an Integer
    '''
    data_type = int
    python_type = int


class FloatField(NumberField):
    '''
    A field that validates input as an Integer
    '''
    data_type = float
    python_type = float


class BooleanField(BaseField):

    '''A boolean field type. In addition to ``True`` and ``False``, coerces these
    values:
    + For ``True``: "True", "true", "1"
    + For ``False``: "False", "false", "0"

    '''
    data_type = bool
    python_type = bool


class DTBaseField(BaseField):
    ''' Base field for all fields related to date and time '''
    data_type = str

    def to_data(self, value):
        if value is None:
            return None
        return value.isoformat()

    def to_python(self, value):
        if isinstance(value, self.python_type):
            return value
        return dateutil.parser.parse(value)


class TimeField(DTBaseField):
    ''' Date field, exposes datetime.date as the python field '''
    python_type = datetime.time

    def to_python(self, value):
        return super(TimeField, self).to_python(value).time()

class DateField(DTBaseField):
    ''' Date field, exposes datetime.date as the python field '''
    python_type = datetime.date

    def to_python(self, value):
        if value is None:
            return None
        if isinstance(value, self.python_type):
            return value
        return super(DateField, self).to_python(value).date()


class DateTimeField(DTBaseField):
    ''' Date field, exposes datetime.datetime as the python field '''
    python_type = datetime.datetime

