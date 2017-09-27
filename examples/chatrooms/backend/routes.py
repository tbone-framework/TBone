#!/usr/bin/env python
# encoding: utf-8


from tbone.resources.routers import Router
from resources import *

# create a resource router for this app
_chatrooms_router = Router(name='api/chatrooms')
_chatrooms_router.register(UserResource, 'user')
_chatrooms_router.register(RoomResource, 'room')


routes = [
]

routes += _chatrooms_router.urls()



