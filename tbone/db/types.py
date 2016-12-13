#!/usr/bin/env python
# encoding: utf-8


from schematics.types import BaseType, StringType


class FreeFormDictType(BaseType):
    '''
    Dict type which does not enforce a structure.
    Useful for fields which hold dictionaries with different schemas between models
    '''
    pass


class URLType(StringType):
    pass
