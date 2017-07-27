#!/usr/bin/env python
# encoding: utf-8

import datetime
import dateutil.parser
from .base import BaseField


class StringField(BaseField):
    ''' Unicode string field '''
    data_type = str
    python_type = str


class NumberField(BaseField):

    ERRORS = {
        'min': "Value should be greater than or equal to {0}.",
        'max': "Value should be less than or equal to {0}.",
    }

    def __init__(self, min=None, max=None, **kwargs):
        # self.number_class = number_class
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


class BooleanType(BaseField):

    '''A boolean field type. In addition to ``True`` and ``False``, coerces these
    values:
    + For ``True``: "True", "true", "1"
    + For ``False``: "False", "false", "0"

    '''
    data_type = bool
    python_type = bool


class DateTimeField(BaseField):
    ''' '''
    data_type = str
    python_type = datetime.datetime

    def to_data(self, value):
        return value.isoformat()

    def to_python(self, value):
        if isinstance(value, datetime.datetime):
            return value
        return dateutil.parser.parse(value)