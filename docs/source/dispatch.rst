.. _dispatch:

============
Dispatch
============


The dispatch sub-mobule consists of all the classes used for managing internal and external events.


Signals
=================

Signals are a classes which help implement a publish/subscribe, or producer/consumer relationship between components in the application. The signals mechanism is very similar to the same concept existing in frameworks such as Django. However, signals in TBone are implemented to be non-blocking. Because of that, signals not only help to build code with the `separation of concerns <https://en.wikipedia.org/wiki/Separation_of_concerns>`_ principle, but also allow application internal events to execute outside the scope of the request/response cycle, a pattern often implemented with background tasks.

Declaring 
------------

signals are declared like so::

    from tbone.dispatch import Signal

    post_init = Signal() 

Any module within the app can import this ``Signal`` object and can register as a receiver or use it to send events to other receiver methods

.. note::
    The ``MongoCollectionMixin`` uses the ``post_save`` and ``post_delete`` events to signal that a documentent as been inserted, updated or deleted from the database. Components using ``MongoCollectionMixin`` based models, such as the ``MongoResource`` can consume such events to implement further functionality

Signals can be triggered with parameters such as ``sender`` and ``instance`` and any other parameter that is required to pass to the receiving method. Since signals are only handled within the same process, it is safe to pass Python objects. 


Sending Signals 
----------------

Sending a signal is done like so::

    import asyncio
    from my_signals import post_init  # a module containing the declaration of the signal

    ...

    asyncio.ensure_future(post_init.send(sender=App))

By using the ``ensure_future`` method of ``asyncio`` the ``send`` method is injected into the event loop without awaiting on it. If the call to ``send`` was part of a request/response cycle, the execution of the receiver methods will most likely happen after the response is returned to the client. 
Using ``ensure_future`` is not a requirement. Signals can be executed synchronously. The usage entirely depends on the developers' intentions. 

Receiving Signals
-------------------

Receiving, or consuming signals requires implementing a method and then registering this method as the signal receiver function using the ``Signal.connect()``


.. automethod:: tbone.dispatch.signals.Signal.connect




Calling the ``connect`` method is done like so::

    from my_signals import post_init 

    def on_init(sender, **kwargs):
        ... do something

    post_init.connect(on_init)



Channels
==========

Channels are another form of implementing a publish/subscribe relationship between software components, but is intended for external communication. The most common use of channels in TBone is for server-to-client communication via websockets. Channels provide the neccesary abstraction between code in the app and open websockets. Tbone provides the flexibility of creating multiple channels directing messages on the same websocket, for publishing different elements of the application.

Channels can store message data in any medium, depending on the implementation. 
TBone includes two implementations out of the box:

    1. ``MemoryChannel`` : Uses an ``asyncio.Queue`` for managing message data. Useful *only* when deploying a single instance of the backend
    2. ``MongoChannel`` : Uses a ``MongoDB`` capped collection and a tailable cursor to wait for new messages. This technique can be very useful for backends consisting of multiple instances. It is also quite useful for TBone-based apps which use ``MongoDB`` as the data store, since no additional component is required. However, for large volumes the performance cannot match that of a RAM-based database such as ``memcached`` or ``Redis`` 

Custom-backend channels can be implemented by subclassing the ``Channel`` class.


Unlike signals, a single channel respond to multiple types of events. The ``subscribe`` method is used to register to channel events.

.. automethod:: tbone.dispatch.channels.Channel.subscribe


Sending events to channel subscribers is done with the ``publish`` method:

.. automethod:: tbone.dispatch.channels.Channel.publish


TBone uses the channels mechanism inside ``Resource`` based classes to implement full-duplex RESTful APIs. Therefore, resources can accept HTTP requests, but also send REST-like events.
The ``MongoResource`` class uses a channel to publish resource events such as ``created`` or ``updated`` to implement a REST-like feedback on resource events. The scenario works like so:

1. A client send an http POST request to the resource, creating a new data object 
2. The same resource class publishes an event to the channel that a new object was created, providing the serialized form of the object
3. The ``Channel`` object iterates through all subscribers (clients registered with a websocket connection) and sends the REST-like event to the registered clients

The following diagram illustrates this:


.. image:: /images/channel1.png
    :align: center


Channels are created as singletons based on the channel's name. This means that every channel given a name will have only a single instance running within the process. This is useful since channels can be created anywhere within the app components. By doing so, channels do not have to be injected into components.


.. note::
    Channels are not restricted to usage by ``Resource`` objects. Any component can invoke a channel and send events.


Websockets
-------------

Creating a ``Channel`` and publishing events is not enough in order to send data to clients using websockets. Channels do not create the actual application endpoint which clients use to connect to the websocket interface. This has to be implemented by the developer, depending on the Webserver being used.

A minimal ``Sanic`` based example may look like this::

    from tbone.dispatch.carriers.sanic_websocket import SanicWebSocketCarrier

    async def resource_event_websocket(request, ws):
        # Create the channel - using the Mongo implementation
        request.app.pubsub = MongoChannel(name='pubsub', db=request.app.db)
        # Subscribe to the 'resource_create' event, passing the websocket instance, wrapped in a Carrier subclass.
        request.app.pubsub.subscribe('resource_create', SanicWebSocketCarrier(ws))
        while True:
            await ws.recv()
        request.app.pubsub.unsubscribe('resource_create', SanicWebSocketCarrier(ws))


A minimal ``AioHttp`` based example may look like this::

    from tbone.dispatch.carriers.aiohttp_websocket import AioHttpWebSocketCarrier

    async def websocket_handler(request):

        ws = web.WebSocketResponse()
        await ws.prepare(request)

        # Create the channel - using the Mongo implementation
        request.app.pubsub = MongoChannel(name='pubsub', db=request.app.db)
        # Subscribe to the 'resource_create' event, passing the websocket instance, wrapped in a Carrier subclass.
        request.app.pubsub.subscribe('resource_create', AioHttpWebSocketCarrier(ws))

        async for msg in ws:
            ...

        return ws


Carriers
-----------

Carriers are used by channels to abstract the mechanism in which events are sent through. Because TBone is webserver agnostic, supporting ``AioHttp`` websockets and ``Sanic`` websockets requires an abstraction layer over the websocket object itself. 
Furthermore, developers can subclass the ``Carrier`` class to implement additional mechanisms such as `SockJS <http://sockjs.org/>`_



