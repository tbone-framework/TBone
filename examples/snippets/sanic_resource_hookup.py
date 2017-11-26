from sanic import Sanic
from tbone.resources import Resource
from tbone.resources.sanic import SanicResource


class TestResource(SanicResource, Resource):
    async def list(self, **kwargs):
        return {
            'meta': {},
            'objects': [
                {'text': 'hello world'}
            ]
        }

app = Sanic()
app.add_route(methods=['GET'], uri='/', handler=TestResource.as_list())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)