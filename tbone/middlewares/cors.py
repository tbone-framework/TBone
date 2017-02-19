#!/usr/bin/env python
# encoding: utf-8

CORS_ALLOW_ORIGIN = '*'
CORS_ALLOW_METHODS = ['POST', 'GET', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']
CORS_ALLOW_HEADERS = ['content-type', 'authorization']
CORS_ALLOW_CREDENTIALS = True

async def cors(app, handler):
    async def middleware(request):
        response = await handler(request)
        response.headers['Access-Control-Allow-Origin'] = CORS_ALLOW_ORIGIN
        response.headers['Access-Control-Allow-Methods'] = ','.join(CORS_ALLOW_METHODS)
        response.headers['Access-Control-Allow-Headers'] = ','.join(CORS_ALLOW_HEADERS)
        response.headers['Access-Control-Allow-Credentials'] = 'true' if CORS_ALLOW_CREDENTIALS else 'false'
        return response
    return middleware
