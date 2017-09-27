#!/usr/bin/env python
# encoding: utf-8


class NoAuthentication(object):
    '''
    Base class for all authentication methods.
    Used as the default for all resouces.
    This is a no-op authenttication class which always returns ``True``
    '''
    async def is_authenticated(self, request):
        '''
        This method is executed by the ``Resource`` class before executing the request.
        If the result of this method is ``False`` the request will not be executed and the response will be 401 un authorized.
        The basic implementation is no-op and always returns ``True``
        '''
        return True


class ReadOnlyAuthentication(NoAuthentication):
    async def is_authenticated(self, request):
        if request.method.upper() == 'GET':
            return True
        return False


