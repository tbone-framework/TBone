.. _getting_started:

========================
Getting Started
========================


.. note::
    Make sure you have at least version 3.5 of Python. TBone uses the async/await syntax, so earlier versions of python will not work.

Selecting a web server
------------------------

TBone works with either `Sanic <https://github.com/channelcat/sanic>`_ or `Aiohttp <https://github.com/aio-libs/aiohttp>`_ . It can be extended to work with other nonblocking web servers.
If you're new to both libraries and want to know which to use, please consult their respective documentation to learn which is more suited for your project. Either way, this decision won't affect the you will use TBone.


Model Definition
------------------

TBone provides an ODM layer which makes it easy to define data schemas, validate and control their serialization. Unlike ORMs or other MongoDB ODMs, such as MongoEngine, The model definition is decoupled from the data persistency layer, allowing you to use the same ODM with persistency layers on different document stores.

Defining a model looks like this::

    from tbone.data.fields import *
    from tbone.data.models import *

    class Person(Model):
        first_name = StringField(required=True)
        last_name = StringField(required=True)
        age = IntegerField()



Sanic Example
--------------------



Aiohttp Example
---------------------