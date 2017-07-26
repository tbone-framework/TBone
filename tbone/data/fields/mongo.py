#!/usr/bin/env python
# encoding: utf-8

import bson
from .base import BaseField


class ObjectIdField(BaseField):
    '''
    An field wrapper around MongoDB ObjectIds
    '''
    # python_type = bson.objectid.ObjectId
    ERRORS = {
        'convert': "Couldn't cast value as ObjectId",
    }

    def to_python(self, value):
        if not isinstance(value, bson.objectid.ObjectId):
            try:
                value = bson.objectid.ObjectId(str(value))
            except bson.objectid.InvalidId:
                raise Exception(self._errors['convert'])
        return value

    def to_data(self, value):
        return str(value)
