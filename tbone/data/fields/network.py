#!/usr/bin/env python
# encoding: utf-8

import re
from .simple import StringField


class EmailField(StringField):
    # TODO: Add SMTP validation
    REGEXP = '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$'

    def __init__(self, **kwargs):
        super(EmailField, self).__init__(**kwargs)

    @validator
    def email(self, value):
        if value is None or value == '':
            return value
        match = re.match(self.REGEXP, value)
        if match is None:
            raise ValueError('Malformed email address')
        return value


class URLField(StringField):

    @validator
    def url(self, value):
        # TODO: implement this
        return value
