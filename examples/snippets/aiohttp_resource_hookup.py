from aiohttp import web
from tbone.resources import Resource
from tbone.resources.aiohttp import AioHttpResource


class TestResource(AioHttpResource, Resource):
    async def list(self, **kwargs):
        return {
            'meta': {},
            'objects': [
                {'text': 'hello world'}
            ]
        }

app = web.Application()
app.router.add_get('/', TestResource.as_list())

if __name__ == "__main__":
    web.run_app(app, host='127.0.0.1', port=8000)