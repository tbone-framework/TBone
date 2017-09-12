# TBone


TBone makes it easy to develop full-duplex RESTful APIs on top of your `asyncio` web application or webservice.
It uses a nonblocking asynchronous web server and provides the neccesary structure to build asynchronous web apps and services.
TBone is web-server agnostic and can be added on top of your `Sanic` or `Aiohttp` app.

TBone is comprised of 4 major components:

1. Data Structure - an ODM-like modeling mechanism for schema declaration and data validation and serialization
2. Data Persistency - Persistency mixin classes for document stores with a full implementation over MongoDB
3. Resources - Mechanism for creating full-duplex RESTful APIs over `HTTP` and `Websockets`
4. Dispatch - Classes for managing internal and external events.

Combining the usage of these 4 components makes it extremely easy to build full-duplex RESTful APIs on top of your mongoDB datastore.

## Example

```python
class Book(Model, MongoCollectionMixin):
    _id = ObjecIdField(primary_key=True)
    title = StringField(required=True)
    author = StringField(required=True)
    publication_date = DateTimeField()


class BookResource(AioHttpResource, MongoResource):
    class Meta:
        object_class = Book
```

## Nonblocking 

TBone was designed to develop asynchorous web applications and web services. The entire infrastructure was built around `coroutines`.
TBone utilizes only asynchronous 3rd party components to make sure that your app is truly nonblocking. 

## Requirements

TBone uses the async/await syntax and is limited to Python version 3.5 and up.

Furthermore, TBone has very few basic requiremets. 
However, depending on its usage requires additional packages may be required.

## documentation 

[Documentation can be found here](https://tbone.readthedocs.io)



