#!/usr/bin/env python
# encoding: utf-8


class NoAuthentication(object):
    def is_authenticated(self, request):
        return True


class ReadOnlyAuthentication(NoAuthentication):
    def is_authenticated(self, request):
        if request.method.upper() == 'GET':
            return True
        return False


