#!/usr/bin/env python
# encoding: utf-8

import json
import uuid
import decimal
import datetime


class ExtendedJSONEncoder(json.JSONEncoder):
    '''
    Extends the default JSON encoder to support additional data types:
    datetime.datetime
    datetime.date
    datetime.time
    decimal.Decimal
    uuid.UUID
    '''
    def default(self, data):
        if isinstance(data, (datetime.datetime, datetime.date, datetime.time)):
            return data.isoformat()
        elif isinstance(data, decimal.Decimal) or isinstance(data, uuid.UUID):
            return str(data)
        else:
            return super(ExtendedJSONEncoder, self).default(data)


def run_once(func):
    ''' Decorator for making sure a method can only be executed once '''
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return func(*args, **kwargs)
    wrapper.has_run = False
    return wrapper