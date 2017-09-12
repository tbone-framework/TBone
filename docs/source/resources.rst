.. _resources:

============
Resources
============


Resources are at the heart of the TBone framework. They provide the foundation for the application's communication with its consumers and facilitate its API. Resources are designed to implement a RESTful abstraction layer over HTTP and Websockets protocols and assist in the creation of your application's design and infrastructure.


Overview
-----------

Resources are class-based. A single resource class implements all the methods required to communicate with your API over HTTP or Websocket, using HTTP-like verbs such as ``GET`` and ``POST``. In addition it implements resource events which translate to application events sent over websockets to the consumer. 

A ``Resource`` subclass must implement all the methods it expects to respond to.
The following table lists the HTTP verbs and their respective member methods:



+-------------+-------------------------------------------+
| HTTP Verb   | ``Resource`` subclass method to implement | 
+=============+===========================================+
| GET         | ``list()``                                |
+-------------+-------------------------------------------+
| GET  <pk>   | ``detail()``                              |
+-------------+-------------------------------------------+
| POST        | ``create()``                              |
+-------------+-------------------------------------------+
| POST  <pk>  | ``create_detail()``                       |
+-------------+-------------------------------------------+
| PUT         | ``update_list()``                         |
+-------------+-------------------------------------------+
| PUT <pk>    | ``update()``                              |
+-------------+-------------------------------------------+
| PATCH       | ``modify_list()``                         |
+-------------+-------------------------------------------+
| PATCH <pk>  | ``modify()``                              |
+-------------+-------------------------------------------+
| DELETE      | ``delete_list()``                         |
+-------------+-------------------------------------------+
| DELETE <pk> | ``delete()``                              |
+-------------+-------------------------------------------+


Sanic and AioHttp
-------------------

TBone includes two mixin classes to adapt your resources to the underlying web-server of your application. 
Those are ``SanicResource`` and ``AioHttpResource`` .
Every resource class in your application must include one of those mixin classes, respective to your application's HTTP and Websockets infrastructure. These mixin classes implement the specifics pertaining to their respective libraries and leave the developer with the work on implementing the application's domain functionality. 


If your application is based on ``Sanic`` your resources will be defined like so::

    class MyResource(SanicResource, Resource):
        ...

If your application is based on ``AioHttp`` your resources will be defined like so::

    class MyResource(AioHttpResource, Resource):
        ...

.. note::
    Adapting a resource class is done with mixins rather than with single inheritance. The reason is so developers can bind the correct resource adapter to a ``Resource`` derived class or classes that are derived from other base resources such as ``MongoResource`` .
    It obviously makes no sense to have resources mixed with both ``SanicResource`` and ``AioHttpResource`` in the same project.



Resource Options
------------------

Every resource has a ``ResourceOptions`` class associated with it, that provides the default options related to the resource.
Such options can be overriden using the ``Meta`` class within the resource class itself, like so::

    from tbone.resources import Resource

    class MyResource(Resource):
        class Meta:
            allowed_detail = ['get', 'post']  # In this example, only GET and POST methods are allowed

Resource options are essential to resources who wish to override built-in functionality such as:
    
    * Serialization
    * Authentication
    * Allowed methods

For a full list of resource options see the :doc:`API Reference </ref/resources>`


Formatters
-------------

Formatters are classes which help to convert Python ``dict`` objects to text (or binary), and back, using a certain transport protocol.
In TBone terminology, formatting turns an native Python object into another representation, such as JSON or XML. Parsing is turning JSON or XML into native Python object.

Formatters are used by resource objects to convert data into a format which can be wired over the net. When using the HTTP protocol, generally APIs expose data in a text-based format. 
By default, TBone formats and parses objects to and from a JSON representation. However, developers can override this behavior by writing additional ``Formatter`` classes to suit their needs.



Authentication
---------------

TBone provides an authentication mechanism which is wired into the resource's flow. All requests made on a resource are routed through a central ``dispatch`` method. Before the request is executed an authentication mechanism is activated to determine if the request is allowed to be processed. Therefore, every resource has an ``Authentication`` object associated with it. This is done using the ``Meta`` class of the resource, like so::

    class BookResource(Resource):
        class Meta:
            authentication = Authentication()


By default, all resources are associated with a ``NoAuthentication`` class, which does not check for any authentication whatsoever. Developers need to subclass ``NoAuthentication`` to add their own authentication mechanism. Authentication classes implement a single method ``is_authenticated`` which has the request object passed. Normally, developers would use the request headers to check for authentication and return ``True`` or ``False`` based on the content of the request.




Nested Resources
------------------

Nested resources ...
 

MongoDB Resources
-------------------

The ``MongoResource`` class provides out-of-the-box CRUD functionality over your MongoDB collections with as little as three lines of code, like so::

    from tbone.resources.mongo import MongoResource

    class BookResource(AioHttpResource, MongoResource):
        class Meta:
            object_class = Book


.. important::
    TBone is not aware of how you manage your application's global infrastructure. Therefore Resources and Models are not aware of your database's handle. Because of that, TBone makes the assumption that your global ``app`` object is attached to every ``request`` object, which both ``Sanic`` and ``AioHttp`` do by default. it also assumes that the database handler is assigned to the global ``app`` object, which you must handle yourself, like so::

        app.db = connect(...)

    See TBone `examples <https://github.com/475Cumulus/TBone/tree/develop/examples/>`_ for more details

CRUD
~~~~~~~~~~

The ``MongoResource`` class provides out-of-the-box CRUD operations on your data models. As mentioned in the :doc:`Persistency <db>` section, models are mapped to MongoDB collections. 
This allows for HTTP verbs are to be mapped directly to a MongoDB collection's core functionality.

The following table lists the way HTTP verbs are mapped to MongoDB collections

+-------------+---------------------------+
| HTTP Verb   | MongoDB Collection method | 
+=============+===========================+
| GET         | ``find()`` ``find_one()`` |
+-------------+---------------------------+
| POST        | ``insert()``              |
+-------------+---------------------------+
| PUT         | ``save()``                |
+-------------+---------------------------+
| PATCH       | ``find_and_modify()``     |
+-------------+---------------------------+
| DELETE      | ``delete()``              |
+-------------+---------------------------+


Filtering
~~~~~~~~~~~

The ``MongoResource`` provides a mapping mechanism between url parameters and MongoDB query parameters.
Therefore, the url::

    /api/v1/movies/?genre=drama

Will be mapped to::

    coll.find(query={"genre": "drama"})

Passing additional parameters to the url will add additional parameters to the query. 

In addition, it is possible to also add the query operator to the urls parameters.
Operators are added to the url parameters using a double underscore ``__`` like so::

    /api/v1/movies/?rating__gt=4

Which will be mapped to::

    coll.find(query={{"rating": {"$gt": 4}})    

     



Sorting 
~~~~~~~~~~

Sorting works very similar to filtering, by passing url parameters which are mapped to the sort parameter like so::

    /api/v1/member/?order_by=age

Which will be mapped to::

    coll.find(sort={'age': 1})  # pymongo.ASCENDING

Placing the `-` sign befor ethe sorted field's name will sort the collection in decending order like so::

    /api/v1/member/?order_by=-age

Which will be mapped to::

    coll.find(sort={'age': -1})  # pymongo.DESCENDING



Full Text Search
~~~~~~~~~~~~~~~~~

The ``MongoResource`` class provides an easy hook between url parameters and a full-text-search query.
However, full text search is not available on a collection by default. In order to utilize MongoDB's FTS functionality the proper indices must be configured within the collection. Please consult with the `MongoDB documentation <https://docs.mongodb.com/manual/core/index-text/>`_ on using text indices as well as TBone's documentation on defining indices as part of a ``Model`` .

FTS (full text search) is provided out-of-the-box on all ``MongoResource`` classes, provided the relevant indices are in place. 
FTS can be used using query parameters like so::

    /api/books/?q=history
    
This will execute a FTS query on all fields that were indexed with the text index. FTS takes presedence over standard filters, which means that if the url parameters include both FTS and filters, FTS will be executed.

The default operator for accessing FTS is ``q``. However, this can overriden in the ``Meta`` class by overriding the option ``fts_operator`` like so::

    class BookResource(SanicResource, MongoResource):
        class Meta:
            object_class = Book
            fts_operator = 'fts'


This will result in a usage like so::

    /api/books/?fts=history


Routers
----------

Routers are *optional* components which help to bind resources to the application's url router.  Whether you're using ``Sanic`` or ``AioHttp`` every application must have its url routes defined. 

The fact that AioHttp uses a centralized system of defining routes, similar to ``Django``, while Sanic uses a de-centralized system of defining routes, in the form of decorators, bears no difference. 

Resources are registered with routers. A router may have one or more resources registered with it. An application can have one or more routers defined.

.. note::
    For small applications a single router for all your resources may be good enough. 
    Larger applications may want to use multiple routers in order to seperate the application's components, similar to the way a Django project may contain multiple apps.
    It is up to the developers to decide how many routes are needed in their projects.

A router may have an optional ``path`` variable which the router prepends to all resources.

Resources are registered with a router like so::

    class AccountResource(AioHttpResource, Resource):
        ...

    class PublicUserResource(AioHttpResource, Resource):
        ...

    router = Router(name='api/user')                    # api/user is the url prefix of all resources under this router
    router.register(AccountResource, 'account')         # the full url would be api/user/account/
    router.register(PublicUserResource, 'public_user')  # the full url would be api/user/public_user/


Once the router is created, the urls need to be added to the application's urls.

With ``AioHttp`` it looks like this::

    app = web.Application()
    .
    .
    .
    for route in router.urls():
        app.router.add_route(
            method=route.methods,
            path=route.path,
            handler=route.handler,
            name=route.name
        )

With ``Sanic`` it looks like this::

    app = Sanic()
    .
    .
    .
    for route in router.urls():
        app.add_route(
            methods=route.methods,
            uri=route.path,
            handler=route.handler
        ) 











