#!/usr/bin/env python
# encoding: utf-8

from .resources import Resource


class Router(object):
    ''' Creates a url list for a group of resources. Pass a url parser method or class to generate urls for the used web framework '''
    def __init__(self, name):
        self.name = name
        self._registry = {}

    def register(self, resource, endpoint):
        ''' register a resource with the router, adding it to the url table '''
        if not issubclass(resource, Resource):
            raise ValueError('Not and instance of ``Resource`` subclass')
        self._registry[endpoint] = resource

    def unregister(self, endpoint):
        if endpoint in self._registry:
            del(self._registry[endpoint])

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
            # append any nested handlers the resource may have
            # url_patterns.extend(resource_class.nested_handlers('(?P<api_name>{})/(?P<resource_name>{})'.format(self.name, endpoint)))
            # append resource as list
            url_patterns.append((
                '*',
                '/%s/%s/' % (self.name, endpoint),
                resource_class.as_list(),
                '{}_{}_list'.format(self.name, endpoint).replace('/', '_')
            ))
            # append resource as detail
            url_patterns.append((
                '*',
                '/%s/%s/{pk}/' % (self.name, endpoint),
                resource_class.as_detail(),
                '{}_{}_detail'.format(self.name, endpoint).replace('/', '_')
            ))
        return url_patterns



    # def urls(self):
    #     '''
    #     Iterate through all resources registered with this router
    #     and create a list endpoint and a detail endpoint for each one.
    #     Uses the router name as prefix and endpoint name of the resource when registered, to assemble the url pattern.
    #     Uses the constructor-passed url method or class for generating urls
    #     '''
    #     url_patterns = []
    #     for endpoint, resource_class in self._registry.items():
    #         setattr(resource_class, 'api_name', self.name)
    #         setattr(resource_class, 'resource_name', endpoint)
    #         # append any nested handlers the resource may have
    #         url_patterns.extend(resource_class.nested_handlers('(?P<api_name>{})/(?P<resource_name>{})'.format(self.name, endpoint)))
    #         # append resource as list
    #         url_patterns.append((
    #             '*',
    #             '/(?P<api_name>{})/(?P<resource_name>{})/$'.format(self.name, endpoint),
    #             resource_class.as_list(),
    #             '{}_{}_list'.format(self.name, endpoint).replace('/', '_')
    #         ))
    #         # append resource as detail
    #         url_patterns.append((
    #             '*',
    #             '/(?P<api_name>{})/(?P<resource_name>{})/(?P<pk>[\w\d_.-]+)/$'.format(self.name, endpoint),
    #             resource_class.as_detail(),
    #             '{}_{}_detail'.format(self.name, endpoint).replace('/', '_')
    #         ))
    #     return url_patterns



