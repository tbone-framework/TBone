.. _db:

========================
Data Persistency
========================


Overview
------------

TBone provides data persistency in the form of mixin classes.
Mixin classes mix with your data models and extend the model's ability to perform CRUD operatons on its data into a datastore. 
A mixin class is targeted at a specific datastore and implements the underlying functionality over the datastore's API.

Like most parts of TBone, the functionality data persistency mixins should be implemented as nonblocking. Every method which calls upon the database should be implemented as a coroutine. The database driver must support nonblocking calls.
Failing to do so will limit's TBone efficiency and your app to be truly asynchorous. 


MongoDB
------------

TBone contains the ``MongoCollectionMixin`` which is a full data persistency mixin implementation over the MongoDB database, using `Motor <http://motor.readthedocs.io>`_ , the asynchronous python driver for MongoDB.


.. note::
    By default TBone does not install the Motor library and its dependency PyMongo. If you're using the ``MongoCollectionMixin`` for your data persistency you must explicitly install Motor


The ``MongoCollectionMixin`` can be added to your ``Model`` sub classes like so::

    from tbone.data.models import *
    from tbone.data.fields import *
    from tbone.data.fields.mongo import ObjectIdField
    from tbone.db.models import MongoCollectionMixin

    class Book(Model, MongoCollectionMixin):
        _id = ObjectIdField(primary_key=True)
        isbn = StringField(required=True)
        title = StringField(required=True)
        author = StringField()
        publication_date = DateTimeField()  # MongoDB cannot persist dates only and accepts only datetime

        class Meta:
            name = 'books'
            namespace = 'store'  # this will produce a collection named store.books in the database

In the above example, we explicitely defined the ``_id`` field with the special ``ObjectIdField`` designed specifically for mongoDB databases. Even if the ``_id`` field is not explicitely declared, MongoDB will create one automatically, unless another primary key was declared. See `Indices`_ below.  


Primary Key
~~~~~~~~~~~~

Each MongoDB Model must have one of its fields defined as primary


Database Operations
~~~~~~~~~~~~~~~~~~~~


Indices
~~~~~~~~~~

Each ``Model`` can define a list of index directives which can be applied to the collection on the database.
By default MongoDB creates a default index to the ``_id`` field which is assigned to every document.


Full Text Search
~~~~~~~~~~~~~~~~~


Dynamic Schema
~~~~~~~~~~~~~~~


Extending to other datastores
------------------------------------





