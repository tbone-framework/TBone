#!/usr/bin/env python
# encoding: utf-8


import re
import logging
from urllib.parse import urlparse, parse_qsl
from collections import namedtuple
from .resources import Resource
from tbone.db.models import post_save


logger = logging.getLogger(__file__)

Route = namedtuple('Route', 'path, handler, methods, name')
Route.__doc__ = 'Wrapper object used to create routes which are added to a ``Router``'
Route.path.__doc__ = 'The URL path of the route'
Route.handler.__doc__ = 'The handler which implements the code executing for this request. Can be a function or class'
Route.methods.__doc__ = 'Declares the HTTP methods which this route accepts. The format of this depends on the webserver implementation'
Route.name.__doc__ = 'A unique name for the route'


class Request(dict):
    __slots__ = (
        'app', 'headers', 'method', 'body', 'args', 'url'
    )

    def __init__(self, app, url, method='GET', headers={}, args={}, body={}):
        self.app = app
        self.url = url
        self.method = method
        self.args = args
        self.headers = headers
        self.body = body
        self.args = args


Response = namedtuple('Response', 'headers, data, status')


class Router(object):
    '''
    Creates a url list for a group of resources.
    Handles endpoint url prefixes.
    Calls ``Resource.connect_signal_receiver`` for every ``Resource`` that is registered
    '''

    def __init__(self, name):
        self.name = name
        self._registry = {}

    def register(self, resource, endpoint):
        '''
        This methods registers a resource with the router and connects all receivers to their respective signals

        :param resource:
            The resource class to register
        :type resource:
            A subclass of ``Resource`` class
        :param endpoint:
            the name of the resource's endpoint as it appears in the URL
        :type endpoint:
            str
        '''
        if not issubclass(resource, Resource):
            raise ValueError('Not and instance of ``Resource`` subclass')
        # register resource
        self._registry[endpoint] = resource
        # connect signal receivers
        resource.connect_signal_receivers()

    def unregister(self, endpoint):
        if endpoint in self._registry:
            del(self._registry[endpoint])

    def endpoints(self):
        return list(self._registry)

    def urls(self):
        '''
        Iterate through all resources registered with this router
        and create a list endpoint and a detail endpoint for each one.
        Uses the router name as prefix and endpoint name of the resource when registered, to assemble the url pattern.
        Uses the constructor-passed url method or class for generating urls
        '''
        url_patterns = []
        for endpoint, resource_class in self._registry.items():
            setattr(resource_class, 'api_name', self.name)
            setattr(resource_class, 'resource_name', endpoint)
            # append any nested resources the resource may have
            url_patterns.extend(resource_class.nested_routes('/%s/%s/' % (self.name, endpoint)))
            # append resource as list
            url_patterns.append(Route(
                path='/%s/%s/' % (self.name, endpoint),
                handler=resource_class.as_list(),
                methods=resource_class.route_methods(),
                name='{}_{}_list'.format(self.name, endpoint).replace('/', '_')
            ))
            # append resource as detail
            url_patterns.append(Route(
                path='/%s/%s/%s/' % (self.name, endpoint, resource_class.route_param('pk')),
                handler=resource_class.as_detail(),
                methods=resource_class.route_methods(),
                name='{}_{}_detail'.format(self.name, endpoint).replace('/', '_')
            ))
        return url_patterns

    def urls_regex(self):
        '''
        Iterate through all resources registered with this router
        and create a list endpoint and a detail endpoint for each one.
        Uses the router name as prefix and endpoint name of the resource when registered, to assemble the url pattern.
        Uses the constructor-passed url method or class for generating urls
        '''
        url_patterns = []
        for endpoint, resource_class in self._registry.items():
            setattr(resource_class, 'api_name', self.name)
            setattr(resource_class, 'resource_name', endpoint)
            # append any nested handlers the resource may have
            url_patterns.extend(resource_class.nested_routes('/(?P<api_name>{})/(?P<resource_name>{})'.format(self.name, endpoint)))
            # append resource as list
            url_patterns.append(Route(
                path='/(?P<api_name>{})/(?P<resource_name>{})/$'.format(self.name, endpoint),
                handler=resource_class.as_list(),
                methods=resource_class.route_methods(),
                name='{}_{}list'.format(self.name, endpoint).replace('/', '_')
            ))
            # append resource as detail
            url_patterns.append(Route(
                path='/(?P<api_name>{})/(?P<resource_name>{})/(?P<pk>[\w\d_.-]+)/$'.format(self.name, endpoint),
                handler=resource_class.as_detail(),
                methods=resource_class.route_methods(),
                name='{}_{}_detail'.format(self.name, endpoint).replace('/', '_')
            ))
        return url_patterns

    async def dispatch(self, app, payload, wrap_response=None):
        '''
        Dispatches an incoming request and passes it to the relevant resource
        returning the response.

        :param app:
            Application handler. must be passed as part of the request

        :param payload:
            The request payload, contains all the parameters of the request

        :param response_wrapper:
            Data objects which wraps the response. Used specifically for websocket communication to identify
            the data transfer as a response to a request
        '''
        handler = None
        params = {}
        # parse request url, separating query params if any
        url = urlparse(payload['href'])
        path = url.path
        params.update(dict(parse_qsl(url.query)))
        params.update(payload.get('args', {}))
        for route in self.urls_regex():
            match = re.match(route.path, path)
            if match:
                handler = route.handler
                break
        if handler:
            request = Request(
                app=app,
                method=payload.get('method', 'GET'),
                url=path,
                args=params,
                headers=payload.get('headers', None),
                body=payload.get('body', None)
            )
            response = await handler(request, wrap_response)
            return response
        return Response(headers={}, data=None, status=404)

