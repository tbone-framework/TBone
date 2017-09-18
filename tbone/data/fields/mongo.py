#!/usr/bin/env python
# encoding: utf-8

import bson
from .base import BaseField


class ObjectIdField(BaseField):
    '''
    A field wrapper around MongoDB ObjectIds
    '''
    data_type = str
    python_type = bson.objectid.ObjectId
    ERRORS = {
        'convert': "Could not cast value as ObjectId",
    }

    def _import(self, value):
        if value is None:
            return None
        return self.python_type(value)

