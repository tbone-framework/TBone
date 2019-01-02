#!/usr/bin/env python
# encoding: utf-8


import logging
from enum import Enum
from functools import wraps
from tbone.dispatch.channels import Channel
from .formatters import JSONFormatter
from .authentication import NoAuthentication
from .verbs import *


logger = logging.getLogger(__file__)


class ResourceOptions(object):
    '''
    A configuration class for Resources. Provides all the defaults and
    allows overriding inside the resource's definition using the ``Meta`` class

    :param  name:
        Declare the resource's name. If ``None`` the class name will be used. Default is ``None``

    :param object_class:
        Declare the class of the underlying data object. Used in ``MongoResource`` to bind the resource class to a ``Model``

    :param query:
        Define a query which the resource will apply to all ``list`` calls. Used in ``MongoResource`` to apply a default query fiter.
        Useful for cases where the entire collection is never queried.

    :param sort:
        Define a sort directive which the resource will apply to GET requests without a unique identifier. Used in ``MongoResource`` to declare default sorting for collection.

    :param hypermedia:
        Specify if the a ``Resource`` should format data and include HATEOAS directives, specifically link to itself.
        Defaults to ``True``

    :param fts_operator:
        Define the FTS (full text search) operator used in url parameters. Used in ``MongoResource`` to perform FTS on a collection.
        Default is set to `q`.

    :param incoming_list:
        Define the methods the resource allows access to without a primary key.
        These are incoming request methods made to the resource.
        Defaults to a full access ``['get', 'post', 'put', 'patch', 'delete']``

    :param incoming_detail:
        Same as ``incoming_list`` but for requests which include a primary key

    :param outgoing_list:
        Define the resource events which will be emitted without a primary key.
        These are outgoing resource events which are emitted to subscribers.
        Defaults to these events ``['created', 'updated', 'deleted']``

    :param outgoing_detail:
        Same as ``outgoing_list`` but for resource events which include a primary key

    :param formatter:
        Provides an instance to a formatting class the resource will be using when formatting and parsing data.
        The default is ``JSONFormatter``. Developers can subclass ``Formatter`` base class and provide implementations to other formats.

    :param authentication:
        Provides and instance to the authentication class the resource will be using when authenticating requests.
        Default is ``NoAuthentication``.
        Developers must subclass the ``NoAuthentication`` class to provide their own resource authentication, based on the application's authentication choices.

    :param channel:
        Defines the Channel class which the resource will emit events into. Defaults to in-memory
    '''
    name = None
    object_class = None
    query = None
    sort = None
    hypermedia = True
    channel_class = Channel
    fts_operator = 'q'
    incoming_list = ['get', 'post', 'put', 'patch', 'delete']
    incoming_detail = ['get', 'post', 'put', 'patch', 'delete']
    outgoing_list = ['created', 'updated', 'deleted']
    outgoing_detail = ['created', 'updated', 'deleted']
    formatter = JSONFormatter()
    authentication = NoAuthentication()

    def __init__(self, meta=None):
        if meta:
            for attr in dir(meta):
                if not attr.startswith('_'):
                    setattr(self, attr, getattr(meta, attr))


class ResourceMeta(type):
    @classmethod
    def __prepare__(mcl, name, bases):
        ''' Adds the signal decorator so member methods can be decorated as signal receivers '''
        def receiver(signal):
            def _receiver(func):
                func._signal_receiver_ = signal

                @wraps(func)
                def wrapper(*args, **kwargs):
                    return func(*args, **kwargs)

                return wrapper
            return _receiver

        d = dict()
        d['receiver'] = receiver
        return d

    def __new__(mcl, name, bases, attrs):
        attrs.pop('receiver', None)
        cls = super(ResourceMeta, mcl).__new__(mcl, name, bases, attrs)

        # create default resource options
        options = ResourceOptions()
        # copy over resource options defined in base classes, if any
        for base in reversed(bases):
            if not hasattr(base, '_meta'):
                continue
            options.__dict__.update(base._meta.__dict__)

        # copy resource options defined in this resource, if any
        if hasattr(cls, 'Meta'):
            for attr in dir(cls.Meta):
                if not attr.startswith('_'):
                    setattr(options, attr, getattr(cls.Meta, attr))
        # create the combined resource options class
        cls._meta = ResourceOptions(options)
        return cls


class Resource(object, metaclass=ResourceMeta):
    '''
    Base class for all resources. 
    '''
    responses = {
        'GET': OK,
        'POST': CREATED,
        'PUT': ACCEPTED,
        'PATCH': ACCEPTED,
        'DELETE': NO_CONTENT
    }
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
    methods = {
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

    class Protocol(Enum):
        http = 10
        websocket = 20
        amqp = 30

    def __init__(self, *args, **kwargs):
        self.request = kwargs.get('request', None)
        self.endpoint = kwargs.get('endpoint', 'list')
        self.data = None

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
    def wrap_handler(cls, handler, protocol, **kwargs):
        ''' Wrap a request handler with the matching protocol handler '''
        def _wrapper(request, *args, **kwargs):
            instance = cls(request=request, **kwargs)
            if protocol == Resource.Protocol.http:
                return instance._wrap_http(handler, request=request, **kwargs)
            elif protocol == Resource.Protocol.websocket:
                return instance._wrap_ws(handler, request=request, **kwargs)
            elif protocol == Resource.Protocol.amqp:
                return instance._wrap_amqp(view_type, *args, **kwargs)
            else:
                raise Exception('Communication protocol not specified')
        return _wrapper

    @classmethod
    def as_view(cls, endpoint, protocol, *init_args, **init_kwargs):
        '''
        Used for hooking up the endpoints. Returns a wrapper function that creates
        a new instance of the resource class and calls the correct view method for it.
        '''
        def _wrapper(request, *args, **kwargs):
            ''' Make a new instance of the resource class and returns a coroutine for execution'''
            instance = cls(*init_args, endpoint=endpoint, request=request, **init_kwargs)
            if protocol == Resource.Protocol.http:
                return instance._wrap_http(cls.dispatch, endpoint=endpoint, *args, **kwargs)
            elif protocol == Resource.Protocol.websocket:
                return instance._wrap_ws(cls.dispatch, endpoint=endpoint, *args, **kwargs)
            elif protocol == Resource.Protocol.amqp:
                return instance._wrap_amqp(endpoint, *args, **kwargs)
            else:
                raise Exception('Communication protocol not specified')

        return _wrapper

    @classmethod
    def as_list(cls, protocol=Protocol.http, *args, **kwargs):
        ''' returns list views '''
        return cls.as_view('list', protocol, *args, **kwargs)

    @classmethod
    def as_detail(cls, protocol=Protocol.http, *args, **kwargs):
        ''' returns detail views '''
        return cls.as_view('detail', protocol, *args, **kwargs)

    async def _wrap_http(self, handler, *args, **kwargs):
        ''' wraps a handler with an HTTP request-response cycle'''
        try:
            method = self.request_method()
            # support preflight requests when CORS is enabled
            if method == 'OPTIONS':
                return self.build_http_response(None, status=NO_CONTENT)
            data = await handler(self, *args, **kwargs)
            # format the response object
            formatted = self.format(method, data)
            status = self.responses.get(method, OK)
            return self.build_http_response(formatted, status=status)
        except Exception as ex:
            return self.dispatch_error(ex)

    async def _wrap_ws(self, handler, *args, **kwargs):
        ''' wraps a handler by receiving a websocket request and returning a websocket response '''
        try:
            method = self.request_method()
            # call the wrapped handler
            data = await handler(self, *args, **kwargs)
            status = self.responses.get(method, OK)
            response = {
                'type': 'response',
                'key': getattr(self.request, 'key', None),
                'status': status,
                'payload': data
            }
        except Exception as ex:
            response = {
                'type': 'response',
                'key': getattr(self.request, 'key', None),
                'status': getattr(ex, 'status', 500),
                'payload': getattr(ex, 'msg', 'general error')
            }
        # return a formatted response object
        return self.format(method, response)

    async def _wrap_amqp(self, handler, *args, **kwargs):
        return NotImplemented()

    @classmethod
    def nested_routes(cls, base_url, formatter: callable = None) -> list:
        '''
        Returns an array of ``Route`` objects which define additional routes on the resource.
        Implement in derived resources to add additional routes to the resource

        :param base_url:
            The URL prefix which will be prepended to all nested routes

        :param formatter:
            The format method to be used when parsing url variables.
            By default the resource's  ``route_param`` method is used, which formats the url based on which HTTP libary is used.

        '''
        return []

    def is_method_allowed(self, endpoint, method) -> bool:
        if endpoint == 'list':
            if method.lower() in self._meta.incoming_list:
                return True
        elif endpoint == 'detail':
            if method.lower() in self._meta.incoming_detail:
                return True
        return False

    async def dispatch(self, *args, **kwargs):
        '''
        This method handles the actual request to the resource.
        It performs all the neccesary checks and then executes the relevant member method which is mapped to the method name.
        Handles authentication and de-serialization before calling the required method.
        Handles the serialization of the response
        '''
        method = self.request_method()

        # get the db object associated with the app and assign to resource
        if hasattr(self.request.app, 'db'):
            setattr(self, 'db', self.request.app.db)

        # check if method is allowed
        if method not in self.methods.get(self.endpoint, {}):
            raise MethodNotImplemented("Unsupported method '{0}' for {1} endpoint.".format(method, self.endpoint))

        if self.is_method_allowed(self.endpoint, method) is False:
            raise MethodNotAllowed("Unsupported method '{0}' for {1} endpoint.".format(method, self.endpoint))

        # check user authentication
        if not await self._meta.authentication.is_authenticated(self.request):
            raise Unauthorized()

        # deserialize request data
        body = await self.request_body()
        self.data = self.parse(method, self.endpoint, body)
        # if method != 'GET':
            # self.data.update(kwargs)
        kwargs.update(self.request_args())
        view_method = getattr(self, self.methods[self.endpoint][method])
        # call request method
        data = await view_method(*args, **kwargs)
        # add hypermedia to the response, if response is not empty
        if data and self._meta.hypermedia is True:
            if self.endpoint == 'list' and method == 'GET':
                for item in data['objects']:
                    self.add_hypermedia(item)
            else:
                self.add_hypermedia(data)

        return data

    def dispatch_error(self, err):
        '''
        Handles the dispatch of errors
        '''
        try:
            data = {'error': [l for l in err.args]}
            body = self._meta.formatter.format(data)
        except Exception as ex:
            data = {'error': str(err)}
            body = self._meta.formatter.format(data)

        status = getattr(err, 'status', 500)
        return self.build_http_response(body, status=status)

    @classmethod
    def build_http_response(cls, data, status=200):
        '''
        Given some data, generates an HTTP response.
        If you're integrating with a new web framework, other than sanic or aiohttp, you **MUST**
        override this method within your subclass.

        :param data:
             The body of the response to send
        :type data:
            string
        :param status:
            (Optional) The status code to respond with. Default is ``200``
        :type status:
            integer
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

    @classmethod
    def route_param(cls, param, type=str):
        '''
        Returns the route representation of a url param, pertaining to the web library used.
        Implemented on the http library resource sub-class to match the requirements of the HTTP library
        '''
        raise NotImplementedError()

    def get_resource_uri(self):
        return '/{}/{}/'.format(getattr(self.__class__, 'api_name', None), getattr(self.__class__, 'resource_name', None))

    def parse(self, method, endpoint, body):
        ''' calls parse on list or detail '''
        if isinstance(body, dict):  # request body was already parsed
            return body
        if endpoint == 'list':
            return self.parse_list(body)

        return self.parse_detail(body)

    def parse_list(self, body):
        if body:
            return self._meta.formatter.parse(body)
        return []

    def parse_detail(self, body):
        if body:
            return self._meta.formatter.parse(body)
        return {}

    def add_hypermedia(self, obj):
        '''
        Adds HATEOAS links to the resource. Adds href link to self.
        Override in subclasses to include additional functionality
        '''
        if hasattr(self, 'pk'):
            obj['_links'] = {
                'self': {
                    'href': '{}{}/'.format(self.get_resource_uri(), obj[self.pk])
                }
            }

    def format(self, method, data):
        ''' Calls format on list or detail '''
        if data is None:
            if method == 'GET':
                raise NotFound()
            return ''

        return self._meta.formatter.format(data)

    def format_list(self, data):
        if data is None:
            return ''
        return self._meta.formatter.format(data)

    def format_detail(self, data):
        if data is None:
            return ''
        return self._meta.formatter.format(data)

    @classmethod
    def connect_signal_receivers(cls):
        # connect signal receivers
        for item in dir(cls):
            attr = getattr(cls, item)
            if hasattr(attr, '_signal_receiver_'):
                logger.debug('signal receiver subscription', attr)
                attr._signal_receiver_.connect(attr, sender=cls._meta.object_class)

    #  methods which derived classes should implement
    async def list(self, **kwargs):
        raise MethodNotImplemented()

    async def detail(self, **kwargs):
        raise MethodNotImplemented()

    async def create(self, **kwargs):
        raise MethodNotImplemented()

    async def update(self, **kwargs):
        raise MethodNotImplemented()

    async def modify(self, **kwargs):
        raise MethodNotImplemented()

    async def delete(self, **kwargs):
        raise MethodNotImplemented()

    async def update_list(self, **kwargs):
        raise MethodNotImplemented()

    async def modify_list(self, **kwargs):
        raise MethodNotImplemented()

    async def create_detail(self, **kwargs):
        raise MethodNotImplemented()

    async def delete_list(self, **kwargs):
        raise MethodNotImplemented()


class ModelResource(Resource):
    '''
    A specialized resource class for using data models. Requires further implementation for data persistency
    '''

    def __init__(self, *args, **kwargs):
        super(ModelResource, self).__init__(*args, **kwargs)
        # verify object class has a declared primary key
        if not hasattr(self._meta.object_class, 'primary_key') or not hasattr(self._meta.object_class, 'primary_key_type'):
            raise Exception('Cannot create a ModelResource to model {} without a primary key'.format(self._meta.object_class.__name__))
        self.pk = self._meta.object_class.primary_key
        self.pk_type = self._meta.object_class.primary_key_type
