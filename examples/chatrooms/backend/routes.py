#!/usr/bin/env python
# encoding: utf-8


from tbone.resources.routers import Router
from resources import *

# create a resource router for this app
chatrooms_router = Router(name='api/chatrooms')
chatrooms_router.register(UserResource, 'user')
chatrooms_router.register(RoomResource, 'room')




