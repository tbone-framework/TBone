.. _data:

================================================
Data Structure and Serialization
================================================

TBone provides an ODM (Object Document Mapper) for declaring, validating and serializing data structures.

.. note::
    Data structure and data persistency are decoupled in TBone.
    The ODM is kept seperate from the persistency layer and thus allows for implementing additional datastore persistency layers, in addition to the default one for ``MongoDB``

The ``Model`` class is used as the Base for all data models, with an optional DB mixin class for persistency.



Define a Schema
----------------

The ODM works very similarly to ``Django`` models or other ORMS and ODMs for Python. The main difference is that the classes are not bound, by default, to a datastore.
For more information on binding a model to a datastore see :doc:`Persistency <db>`


Models
~~~~~~~

Defining a model is done like so::

    from tbone.data import Model

    class Book(Model):
        title = StringField(required=True)
        publication_date = DateField()
        authors = ListField(StringField)
        number_of_pages = IntegerField()

Each field in the model is defined by its type and by optional parameters which affect its validation and serialization behavior. 


Fields
~~~~~~~~~~~~~

Fields are great


Nested Models
~~~~~~~~~~~~~~

Documents can contain nested objects within them. In order to declare a nested object within your model, simply define the nested object as a model class and use the ``ModelField`` to accosicate it with your root Model, like so::

    class Person(Model):
        first_name = StringField()
        last_name = StringField()

    class Book(Model):
        title = StringField(required=True)
        publication_date = DateField()
        author = ModelField(Person)


This data model will produce an output like this::

    {
        "title": "Mody Dick",
        "publication_date" : "1851-10-18",
        "author" : {
            "first_name" : "Herman",
            "last_name" : "Melville"
        }
    }


Nested objects can also be added to a root model within arrays, like so::

    class Book(Model):
        title = StringField(required=True)
        publication_date = DateField()
        authors = ListModel(ModelField(Person))


This data model will produce an output like this::

    {
        "title": "The Talisman",
        "publication_date" : "1984-11-08",
        "authors" : [{
            "first_name" : "Stephen",
            "last_name" : "King"
        },{
            "first_name" : "Peter",
            "last_name" : "Straub"
        }]
    }


.. note::
    If you are using a data persistency mixin such as the ``MongoCollectionMixin`` you should only add the mixin to your root model and **not** to any of your nested models. 


Model Options
~~~~~~~~~~~~~~


Validation
----------------


Serialization
----------------


De-serialization
----------------

