#!/usr/bin/env python
# encoding: utf-8


from random import randint
from tbone.resources.mongo import MongoResource
from tbone.resources.authentication import NoAuthentication
from tbone.resources.routers import Route
from models import *

try:
    import sanic
    from tbone.resources.sanic import SanicResource as WeblibResource
except ImportError:
    import aiohttp
    from tbone.resources.aiohttp import AioHttpResource as WeblibResource



class UserAuthentication(NoAuthentication):
    async def is_authenticated(self, request):
        if 'user' in request:
            return True
        if 'Authorization' in request.headers:
            username = request.headers['Authorization']
            user = await User.find_one(request.app.db, {'username': username})
            if user:
                request['user'] = user
                return True
        return False


class UserResource(WeblibResource, MongoResource):
    class Meta:
        object_class = User

    async def create(self, **kwargs):
        if 'avatar' not in self.data:
            self.data['avatar'] = 'https://randomuser.me/api/portraits/lego/{}.jpg'.format(randint(0, 8))
        return await super(UserResource, self).create(**kwargs)


class EntryResource(WeblibResource, MongoResource):
    class Meta:
        object_class = Entry
        authentication = UserAuthentication()
        sort = [('_id', -1)]  # revert order by creation, we want to display by order of entry decending
        hypermedia = False

    async def create(self, **kwargs):
        ''' Override the create method to add the user's id to the request data '''
        return await super(EntryResource, self).create(user=self.request['user'])


class RoomResource(WeblibResource, MongoResource):
    class Meta:
        object_class = Room
        authentication = UserAuthentication()

    async def create(self, **kwargs):
        self.data['owner'] = self.request.user
        return await super(RoomResource, self).create(**kwargs)


    @classmethod
    def nested_routes(cls, base_url):
        return [
            Route(
                path=base_url + '%s/entry/' % (cls.route_param('pk')),
                handler=cls.dispatch_entries_list,
                methods=cls.route_methods(),
                name='dispatch_entries_list')
        ]

    @classmethod
    async def dispatch_entries_list(cls, request, **kwargs):
        dispatch = EntryResource.as_list()
        room_id = request.match_info.get('pk')
        return await dispatch(request, room=room_id)


    @classmethod
    def connect_signal_receivers(cls):
        ''' Override the base call call to include additional nested resources '''
        super(RoomResource, cls).connect_signal_receivers()
        EntryResource.connect_signal_receivers()



