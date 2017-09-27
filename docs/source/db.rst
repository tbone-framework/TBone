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

TBone provides the ``MongoCollectionMixin`` which is a full data persistency mixin implementation over the MongoDB database, using `Motor <http://motor.readthedocs.io>`_ , the asynchronous python driver for MongoDB.


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

In the above example, explicitely defines the ``_id`` field with the special ``ObjectIdField`` designed specifically for mongoDB databases. MongoDB will automatically create the ``_id`` field for every document (unless overruled by creation arguments) Even if the ``_id`` field is not explicitely declared in the model. However, developers should add this field to the model to include it in serialization methods. 


Primary Key
~~~~~~~~~~~~

The ``primary_key`` declared in the example above is **not** used for creating a database index. Its purpose is to set this field as the primary key of the model, for usage in resources. The ``MongoResource`` class uses the field declared as ``primary_key`` to construct the resource's URI. A field that is declared as ``primary_key`` should be unique to the collection. In MongoDB the ``_id`` field always is and therefore is the default primary key. 

There are cases when a different primary key can be defined, that would serve the application's API better.
To illustrate this the ``Book`` example above can be modified slightly, like so::

    class Book(Model, MongoCollectionMixin):
        _id = ObjectIdField()
        isbn = StringField(primary_key=True)
        title = StringField(required=True)
        author = StringField()
        publication_date = DateTimeField()  # MongoDB cannot persist dates only and accepts only datetime

        class Meta:
            name = 'books'
            namespace = 'store'  # this will produce a collection named store.books in the database
            indices = [{
                'name': '_isbn',
                'fields': [('isbn', pymongo.ASCENDING)],
                'unique': True
            }]

Fields that are declared as the primary key must have an index created with a unique constraint. 
For more declaring indices see `Indices`_ below. 

The ``MongoResource`` class automatically identifies the field designated at the primary and adjust its resource URI construction accordingly. The API would then be accessed like so::

    /api/books/9788422503552/

Passing the book's `ISBN <https://en.wikipedia.org/wiki/International_Standard_Book_Number>`_ as the resource's unique identifier. 


Indices
~~~~~~~~~~

Each ``Model`` subclass can define a list of index directives which can be applied to the database's collection.
By default MongoDB creates a default index to the ``_id`` field which is assigned to every document.
MongoDB provides an extensive list of features related to document indices. To learn more about MongoDB's indices see the MongoDB documentation.

TBone provides a convinient way to declare indices in the Model's ``Meta`` class, which adhere to the MongoDB index rules.

The following shows an example::

    class Book(Model, MongoCollectionMixin):
        isbn = StringField(primary_key=True)
        title = StringField(required=True)
        author = ListField(StringField)

        class Meta:
            name = 'books'
            indices = [{
                'name': '_isbn',
                'fields': [('isbn', pymongo.ASCENDING)],
                'unique': True
            }]

This example of a ``Model`` subclass mixed with the ``MongoCollectionMixin``
The ``Meta`` class includes one index directive with the following attributes:
1. name : give the index a unique name
2. fields: a list of fields to use for creating the index
3. unique: indicate that the field's value (isbn in this case) must be unique


It is important to remember that, unlike ORMs for relational databases, TBone model indices are **not** created automatically.
There is no concept of data migration and table (or collection) creation. In fact, MongoDB automatically creates a new collection when writing a document into a non-existing collection.
Therefore, it is up to the developer to **explicitly** call TBone's model creation method for every model in the app. 
This is done with the ``create_collection`` function

.. autocofunction:: tbone.db.models.create_collection

Calling the ``create_collection`` function for every model is something that should be done only when changes are made to the model's indices or when deploying to a new system.
Therefore, a common practice would be to include an additional Python script to achieve this. Please note that ``create_collection`` is a coroutine and needs to be executed within an event loop::

    #!/usr/bin/env python
    # encoding: utf-8

    import asyncio
    from bson.json_util import loads
    from tbone.db import connect
    from tbone.db.models import create_collection
    from app import db_config
    from models import Book, Author, Publisher

    async def bootstrap_db():
        db = connect(**db_config)
        
        futures = []
        for model_class in [Book, Author, Publisher]:
            futures.append(create_collection(db, model_class))

        await asyncio.gather(*futures)

    def main():
        loop = asyncio.get_event_loop()
        loop.run_until_complete(bootstrap_db())
        loop.close()

    if __name__ == "__main__":
        main()


Additional Database Operations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``MongoCollectionMixin`` mainly provides methods for performing CRUD database operations. However, the MongoDB API provides a vast number of tools and methodologies to implements all kinds of data manipulation scenarios. 
The following example demonstates such a case::

    class Review(Model):
        user = StringField(required=True)
        text = StringField(required=True)


    class Book(Model, MongoCollectionMixin):
        isbn = StringField(primary_key=True)
        title = StringField(required=True)
        author = ListField(StringField)
        publication_date = DateTimeField()  # MongoDB cannot persist dates only and accepts only datetime
        reviews = ListField(ModelField(Review), default=[])

In this example there is a ``Book`` model which contains a field that is a list of reviews. This list is essentially a list of embedded documents, defined in the ``Review`` model. This is one of the ways to implement a one-to-many relationship with a document store, such as MongoDB, by embedding all the reviews inside the book document itself. 
If this was implemented with a relational database, most likely the ``Review`` model was an independent table and each record in this table would have a foreign-key to a record in the ``Book`` table. 
Therefore, adding a new review would be a single database operation to insert a new record to the Review table. 

But in a document store, with reviews embedded into the book document, using basic CRUD database operations the following needs to be done:
1. Fetch the book document
2. Append a new review to the list of embedded review documents (allowing unrestrained access to the whole list)
3. Saving the book document back to the database

This seems to be a lot of work for a simple insertion of one review, not to mention the exposure to data that was otherwise inserted by other users. To solve this, MongoDB provides the ``$push`` operator, which enables the appending of a single embedded document into the review list. This can be done in a single database operation without having to fetch the whole document first.

In order to utilize this capability the ``Book`` Model is extended with an additional custom method for performing this operation, like so::

    class Book(Model, MongoCollectionMixin):
        isbn = StringField(primary_key=True)
        ...


        async def add_review(self, db, review_data):
            ''' Adds a review to the list of reviews, without fetching and updating the entire document '''
            db = db or self.db
            # create review model instance
            new_rev = Review(review_data)
            data = new_rev.export_data(native=True)
            # use model's pk as query
            query = {self.primary_key: self.pk}
            # push review
            result = await db[self.get_collection_name()].update_one(
                filter=query,
                update={'$push': {'reviews': data}},
            )
            return result

This model's custom-made method takes care of adding a new review to the document with a single database operation and without exposing the entire model to a full-document update.

MongoDB provides many operators that can be used to extend the basic CRUD methodology and thus improve code reliability and performance. Please consult the MongoDB documentation to learn more about operators.







Full Text Search
~~~~~~~~~~~~~~~~~

TBone provides out-of-the-box full text search capabilities over MongoDB collections, accessed through the API. Resource which subclass ``MongoResource`` already have most of the wiring to execute full text search on their data.
In order to utilize the full text search capabilities, the Model needs to include an index for FTS like so::

    class Movie(Model, MongoCollectionMixin):
        _id = ObjectIdField(primary_key=True)
        title = StringField(required=True)
        plot = StringField()
        director = StringField()
        cast = ListField(StringField)
        release_date = DateField()
        runtime = IntegerField()
        poster = URLField()
        genres = StringField()

        class Meta:
            indices = [
                {
                    'name': '_fts',
                    'fields': [
                        ('title', pymongo.TEXT),
                        ('plot', pymongo.TEXT),
                        ('cast', pymongo.TEXT),
                        ('genres', pymongo.TEXT)
                    ]
                }
            ]

    class MovieResource(SanicResource, MongoResource):
        class Meta:
            object_class = Movie

Once the FTS index is created and indexing is complete, searching the database through the api can simply be done by making an HTTP request, like so::

    /api/movies/?q="Robert De Niro"

This request will yield all the results that include this search phrase in either of the fields that were indexed for FTS.
For more on MongoDB full text search, see the MongoDB documentation

The ``q`` operand is used by default, but can be replaced. Doing so requires a change to the ``fts_operator`` in the resources's ``Meta`` class, like so::

    class MovieResource(SanicResource, MongoResource):
        class Meta:
            object_class = Movie
            fts_operator = 'search'

Then, the making the HTTP request is done like so::

        /api/movies/?search="Robert De Niro"



Extending to other datastores
------------------------------------

MongoDB is a general-purpose NoSQL document store that has been around for a while. It is widely used as an alternative to relational databases and offers a wide range of features. 
Due to various considerations, developers may choose to use a different database that is more tuned to their application requirements.
TBone provides a MongoDB persistency layer for models, but that layer can be replaced with a custom solution for another database. Not all NoSQL databases would generally merge easily with TBone's ODM. However, most NoSQL document-oriented and key-value databases should be easily integrated with the ODM paradigm.






