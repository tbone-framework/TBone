#!/usr/bin/env python
# encoding: utf-8


import logging
import asyncio
from dateutil import parser
from .serializers import JSONSerializer
from .authentication import NoAuthentication
from .http import *

logger = logging.getLogger(__file__)


class Resource(object):
    status_map = {
        'list': OK,
        'detail': OK,
        'create': CREATED,
        'update': ACCEPTED,
        'delete': NO_CONTENT,
        'update_list': ACCEPTED,
        'create_detail': CREATED,
        'delete_list': NO_CONTENT
    }
    http_methods = {
        'list': {
            'GET': 'list',
            'POST': 'create',
            'PUT': 'update_list',
            'PATCH': 'modify_list',
            'DELETE': 'delete_list'
        },
        'detail': {
            'GET': 'detail',
            'POST': 'create_detail',
            'PUT': 'update',
            'PATCH': 'modify',
            'DELETE': 'delete'
        }
    }
    allowed_list = ['get', 'post', 'put', 'patch', 'delete']
    allowed_detail = ['get', 'post', 'put', 'patch', 'delete']
    serializer = JSONSerializer()
    authentication = NoAuthentication()
    excludes = []
    pk = 'id'

    def __init__(self, *args, **kwargs):
        self.init_args = args
        self.init_kwargs = kwargs
        self.request = None
        self.data = None
        self.endpoint = None
        self.status = 200

        self.allowed_list = [i.lower() for i in self.allowed_list]
        self.allowed_detail = [i.lower() for i in self.allowed_detail]


    def request_method(self):
        ''' Returns the HTTP method for the current request. '''
        return self.request.method.upper()

    def request_args(self):
        '''
        Returns the arguments passed with the request in a dictionary.
        Returns both URL resolved arguments and query string arguments.
        Implemented for specific http libraries in derived classes
        '''
        raise NotImplementedError()


    async def request_body(self):
        '''
        Returns the body of the current request.
        Implemented for specific http libraries in derived classes
        '''
        raise NotImplementedError()



    @classmethod
    def as_view(cls, view_type, *init_args, **init_kwargs):
        '''
        Used for hooking up the endpoints. Returns a wrapper function that creates
        a new instance of the resource class and calls the correct view method for it.
        '''
        def _wrapper(request, *args, **kwargs):
            ''' Make a new instance of the resource class '''
            instance = cls(*init_args, **init_kwargs)
            instance.request = request
            return instance.dispatch(view_type, *args, **kwargs)

        return _wrapper

    @classmethod
    def as_list(cls, *args, **kwargs):
        ''' returns list views '''
        return cls.as_view('list', *args, **kwargs)

    @classmethod
    def as_detail(cls, *args, **kwargs):
        ''' returns detail views '''
        return cls.as_view('detail', *args, **kwargs)

    @classmethod
    def nested_routes(cls, base_url):
        return []

    def is_method_allowed(self, endpoint, method):
        if endpoint == 'list':
            if method.lower() in self.allowed_list:
                return True
        elif endpoint == 'detail':
            if method.lower() in self.allowed_detail:
                return True
        return False

    async def dispatch(self, endpoint, *args, **kwargs):
        self.endpoint = endpoint
        method = self.request_method()

        # support preflight requests when CORS is enabled
        if method == 'OPTIONS':
            return self.build_response(None, status=NO_CONTENT)

        if hasattr(self.request.app, 'db'):
            setattr(self, 'db', self.request.app.db)

        try:
            if method not in self.http_methods.get(endpoint, {}):
                raise MethodNotImplemented("Unsupported method '{0}' for {1} endpoint.".format(method, endpoint))

            if self.is_method_allowed(endpoint, method) is False:
                raise MethodNotAllowed("Unsupported method '{0}' for {1} endpoint.".format(method, endpoint))

            if not self.authentication.is_authenticated(self.request):
                raise Unauthorized()

            body = await self.request_body()
            self.data = self.deserialize(method, endpoint, body)
            kwargs.update(self.request_args())
            view_method = getattr(self, self.http_methods[endpoint][method])
            # call request method
            data = await view_method(*args, **kwargs)
            # add request_uri
            serialized = self.serialize(method, endpoint, data)
        except Exception as ex:
            return self.dispatch_error(ex)

        status = self.status_map.get(self.http_methods[endpoint][method], OK)
        return self.build_response(serialized, status=status)

    def dispatch_error(self, err):
        # serialize error information
        try:
            data = {'error': [l for l in err.args]}
            body = self.serializer.serialize(data)
        except Exception as ex:
            data = {'error': str(err)}
            body = self.serializer.serialize(data)

        status = getattr(err, 'status', 500)
        return self.build_response(body, status=status)

    def build_response(self, data, status=200):
        '''
        Given some data, generates an HTTP response.
        If you're integrating with a new web framework, you **MUST**
        override this method within your subclass.
        :param data: The body of the response to send
        :type data: string
        :param status: (Optional) The status code to respond with. Default is
            ``200``
        :type status: integer
        :returns: A response object
        '''
        raise NotImplementedError()

    @classmethod
    def route_methods(cls):
        '''
        Returns the relevant representation of allowed HTTP methods for a given route.
        Implemented on the http library resource sub-class to match the requirements of the HTTP library
        '''
        raise NotImplementedError()

    def get_resource_uri(self):
        return '/{}/{}/'.format(getattr(self.__class__, 'api_name', None), getattr(self.__class__, 'resource_name', None))

    def deserialize(self, method, endpoint, body):
        ''' calls deserialize on list or detail '''
        if endpoint == 'list':
            return self.deserialize_list(body)

        return self.deserialize_detail(body)

    def deserialize_list(self, body):
        if body:
            return self.serializer.deserialize(body)
        return []

    def deserialize_detail(self, body):
        if body:
            return self.serializer.deserialize(body)
        return {}

    def serialize(self, method, endpoint, data):
        ''' Calls serialize on list or detail '''
        if data is None and method == 'GET':
            raise NotFound()

        if endpoint == 'list':
            if method == 'POST':
                return self.serialize_detail(data)

            return self.serialize_list(data)
        return self.serialize_detail(data)

    def serialize_list(self, data):
        if data is None:
            return ''
        # add resource uri
        for item in data['objects']:
            item['resource_uri'] = '{}{}/'.format(self.get_resource_uri(), item[self.pk])

        return self.serializer.serialize(data)

    def serialize_detail(self, data):
        if data is None:
            return ''
        data['resource_uri'] = '{}{}/'.format(self.get_resource_uri(), data[self.pk])
        return self.serializer.serialize(self.get_resource_data(data))

    def get_resource_data(self, data):
        ''' Filter object data based on fields and excludes. Currently support only excludes'''
        resource_data = {}
        for k, v in data.items():
            if k not in self.excludes:
                resource_data[k] = v
        return resource_data

    #  methods which derived classes should implement
    async def list(self, *args, **kwargs):
        raise MethodNotImplemented()

    async def detail(self, *args, **kwargs):
        raise MethodNotImplemented()

    async def create(self, *args, **kwargs):
        raise MethodNotImplemented()

    async def update(self, *args, **kwargs):
        raise MethodNotImplemented()

    async def delete(self, *args, **kwargs):
        raise MethodNotImplemented()

    async def update_list(self, *args, **kwargs):
        raise MethodNotImplemented()

    async def create_detail(self, *args, **kwargs):
        raise MethodNotImplemented()

    async def delete_list(self, *args, **kwargs):
        raise MethodNotImplemented()
