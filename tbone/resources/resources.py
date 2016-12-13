#!/usr/bin/env python
# encoding: utf-8


import ast
import logging
from functools import singledispatch
from dateutil import parser
from bson.objectid import ObjectId
from aiohttp.web import Response
from tbone.db.models import post_save
from .serializers import JSONSerializer
from .authentication import NoAuthentication
from .http import *

logger = logging.getLogger(__file__)


LIMIT = 20
OFFSET = 0


class Resource(object):
    status_map = {
        'list': OK,
        'detail': OK,
        'create': CREATED,
        'update': ACCEPTED,
        'delete': NO_CONTENT,
        'update_list': ACCEPTED,
        'create_detail': CREATED,
        'delete_list': NO_CONTENT,
    }
    http_methods = {
        'list': {
            'GET': 'list',
            'POST': 'create',
            'PUT': 'update_list',
            'PATCH': 'modify_list',
            'DELETE': 'delete_list',
        },
        'detail': {
            'GET': 'detail',
            'POST': 'create_detail',
            'PUT': 'update',
            'PATCH': 'modify',
            'DELETE': 'delete',
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

    @property
    def limit(self):
        return LIMIT

    @property
    def offset(self):
        return OFFSET

    def request_method(self):
        ''' Returns the HTTP method for the current request. '''
        return self.request.method.upper()

    async def request_body(self):
        ''' Returns the body of the current request. '''
        if self.request.has_body:
            return await self.request.text()
        return {}

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
    def nested_handlers(cls, base_url):
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

        if hasattr(self.request, 'db'):
            setattr(self, 'db', self.request.db)

        try:
            if method not in self.http_methods.get(endpoint, {}):
                raise MethodNotImplemented("Unsupported method '{0}' for {1} endpoint.".format(method, endpoint))

            if self.is_method_allowed(endpoint, method) is False:
                raise MethodNotAllowed("Unsupported method '{0}' for {1} endpoint.".format(method, endpoint))

            if not self.authentication.is_authenticated(self.request):
                raise Unauthorized()

            body = await self.request_body()
            self.data = self.deserialize(method, endpoint, body)
            kwargs.update(self.request.match_info.items())
            kwargs.update(self.request.GET.items())
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
        except:
            data = {'error': str(err)}
            body = self.serializer.serialize(data)

        status = getattr(err, 'status', 500)
        return self.build_response(body, status=status)

    def build_response(self, data, status=200):
        res = Response(status=status, text=data, content_type='application/json')
        return res

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
    def list(self, *args, **kwargs):
        raise MethodNotImplemented()

    def detail(self, *args, **kwargs):
        raise MethodNotImplemented()

    def create(self, *args, **kwargs):
        raise MethodNotImplemented()

    def update(self, *args, **kwargs):
        raise MethodNotImplemented()

    def delete(self, *args, **kwargs):
        raise MethodNotImplemented()

    def update_list(self, *args, **kwargs):
        raise MethodNotImplemented()

    def create_detail(self, *args, **kwargs):
        raise MethodNotImplemented()

    def delete_list(self, *args, **kwargs):
        raise MethodNotImplemented()


class MongoResource(Resource):
    def __init__(self, *args, **kwargs):
        super(MongoResource, self).__init__(*args, **kwargs)
        self.pk = self.object_class.primary_key
        self.pk_type = self.object_class.primary_key_type
        self.view_type = kwargs.get('view_type', None)
        # post_save.connect(self.post_save, sender=self.object_class)


    async def emit(self, db, key, data):
        pubsub = Channel(db, 'pubsub')
        await pubsub.create_channel()
        pubsub.publish(key, data)

    async def post_save(self, sender, instance, created):
        ''' Receiver function for the object class's post_save signal '''
        if instance.pk is not None:
            # fetch resource (like detail)
            self.db = instance.db
            obj = await self.detail(pk=instance.pk)
            obj['resource_uri'] = '{}{}/'.format(self.get_resource_uri(), instance.pk)
            if created is True and self.view_type == 'list':
                await self.emit(instance.db, 'resource_create', obj)
            elif created is False and self.view_type == 'detail':
                await self.emit(instance.db, 'resource_update', obj)

    async def list(self, *args, **kwargs):
        limit = int(kwargs.pop('limit', [LIMIT])[0])
        # if limit == 0:
        #     limit = 1000
        offset = int(kwargs.pop('offset', OFFSET))
        filters = self.build_filters(**kwargs)
        sort = self.build_sort(**kwargs)
        cursor = self.object_class.get_cursor(db=self.db, query=filters, sort=sort)
        cursor.skip(offset)
        cursor.limit(limit)
        total_count = await cursor.count()
        object_list = await self.object_class.find(cursor)
        return {
            'meta': {
                'total_count': total_count,
                'limit': limit,
                'offset': offset
            },
            'objects': [obj.to_primitive() for obj in object_list]
        }

    async def detail(self, **kwargs):
        try:
            pk = self.pk_type(kwargs['pk'])
            obj = await self.object_class.find_one(self.db, {self.pk: pk})
            if obj:
                return obj.to_primitive()
            raise NotFound('Object matching the given identifier was not found')
        except InvalidId:
            raise NotFound('Invalid ID')

    async def create(self, **kwargs):
        try:

            obj = self.object_class(self.data)
            # TODO: what about the validate ?
            #await obj.insert(db=self.db)
            await obj.save(db=self.db)
            return obj
        except Exception as ex:
            logger.exception(ex)
            raise BadRequest(ex)

    async def update(self, **kwargs):
        try:
            return MethodNotImplemented()
        except Exception as ex:
            logger.exception(ex)
            raise BadRequest(ex)

    async def modify(self, **kwargs):
        try:
            self.data[self.pk] = self.pk_type(kwargs['pk'])
            result = await self.object_class().update(self.db, data=self.data)
            if result is None:
                raise NotFound('Object matching the given identifier was not found')
            return result.to_primitive()

        except Exception as ex:
            logger.exception(ex)
            raise BadRequest(ex)

    async def delete(self, *args, **kwargs):
        try:
            pk = self.pk_type(kwargs['pk'])
            await self.object_class.delete_entries(db=self.db, query={self.pk: pk})
        except Exception as ex:
            logger.exception(ex)
            raise BadRequest(ex)

    def serialize(self, method, endpoint, data):
        ''' We override this method to handle schematics object exporting'''
        if isinstance(data, self.object_class):
            data = data.to_primitive()
        elif isinstance(data, list):
            data = [obj.to_primitive() for obj in data]
        return super(MongoResource, self).serialize(method, endpoint, data)

    def build_filters(self, **kwargs):
        ''' Break url parameters and turn into filters '''
        filters = {}
        for param, value in kwargs.items():
            # break each url parameter to key + operator (if exists)
            pl = dict(enumerate(param.split('__')))
            key = pl[0]
            operator = pl.get(1, None)

            if key in self.object_class().keys():
                if isinstance(value, list) and operator == 'in':
                    value = [convert_value(v) for v in value]
                else:
                    value = convert_value(value)
                # assign operator, if applicable
                filters[key] = {'${}'.format(operator): value} if operator else value
            elif key == 'created':  # special case where we map `created` key to mongo's _id which also contains a creation timestamp
                dt = parser.parse(convert_value(value))
                dummy_id = ObjectId.from_datetime(dt)
                filters['_id'] = {'${}'.format(operator): dummy_id} if operator else dummy_id
        return filters

    def build_sort(self, **kwargs):
        sort = []
        order = kwargs.get('order_by', None)
        if order:
            if type(order) is list:
                order = order[0]
            order = order.decode('utf-8')
            if order[:1] == '-':
                sort.append((order[1:], -1))
            else:
                sort.append((order, 1))
        return sort

@singledispatch
def convert_value(value):
    ''' Utility functions to convert url params to mongodb filter operators and values '''
    raise NotImplementedError('Cannot convert this {}'.format(type(value)))


@convert_value.register(list)
def _(value):
    return convert_value(value[0])


@convert_value.register(bytes)
def _(value):
    return convert_value(value.decode('utf-8'))


@convert_value.register(ObjectId)
def _(value):
    return value


@convert_value.register(str)
def _(value):
    reserved = {
        '': None,
        'null': None,
        'none': None,
        'true': True,
        'false': False
    }
    if value in reserved:
        return reserved[value]
    # check if value is of type ObjectId
    if ObjectId.is_valid(value):
        return ObjectId(value)
    # if all numeric, try to convert to numeric
    try:
        v = ast.literal_eval(value)
        #### WTF REALLY??? ####
        if v<100:
            value=v
        ######################
    except:
        pass
    return value
