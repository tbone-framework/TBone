#!/usr/bin/env python
# encoding: utf-8


from tbone.resources.routers import Router
from resources import *

# create a resource router for this app
_blog_router = Router(name='api/blog')
_blog_router.register(EntryResource, 'entry')

routes = []

routes += _blog_router.urls()



