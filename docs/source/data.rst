.. _data:

================================================
Data Structure and Serialization
================================================

TBone provides an ODM (Object Document Mapper) for declaring, validating and serializing data structures.

.. note::
    Data structure and data persistency are decoupled in TBone.
    The ODM is implemented seperately from the persistency layer and thus allows for implementing other datastore persistency layers, in addition to the default one for ``MongoDB``

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

Each field in the model is defined by its matching type and by optional parameters which affect its validation and serialization behavior. 


.. note::
    Why is TBone not using an external Python schema and validation library such as `Marshmallow <https://github.com/marshmallow-code/marshmallow>`_ or `Schematics <https://github.com/schematics/schematics>`_ ?

    Both libraries mentioned above are excellent for performing the tasks of schema definition, data validation and serialization.
    However, both libraries were developed to be generic and do not use the asynchronous capabilities of TBone to their advantage.
    Therefore TBone implements its own data modeling capabilities which are designed to work in an asynchronous nonblocking environment.
    An example of this is explained in detail in the `Serialize Methods`_ section



Fields
~~~~~~~~~~~~~

Fields are used to describe individual variables in a model schema. There are simple fields for data primitives such as ``int`` and ``str`` and there are composite fields for describing data such as lists and dictionaries. 
Developers who have a background in ORM implementations such as the one included in Django, should be very familiar with this concept.
All fields classes derive from ``BaseField`` and implement coersion methods to and from Python natives, with respect to their designated data types.
In addition, fields provide additional attributes pertaining to the way data is validated, and the way data is serialized and deserialized. They also provide additional attributes for database mixins


Attributes
^^^^^^^^^^^

The following table lists the different attributes of fields and how they are used

+-----------------+------------------------------------------------------------------------------------+----------------+
| Attribute       | Usage                                                                              | Default        |
+=================+====================================================================================+================+
| ``required``    | Determines if the field is required when data is imported or deserialized          |  ``False``     |
+-----------------+------------------------------------------------------------------------------------+----------------+
| ``default``     | Declares a default value when none is provided. May be a callable                  |  ``None``      |
+-----------------+------------------------------------------------------------------------------------+----------------+
| ``choices``     | Set a list of choices, limiting the field's acceptable values                      |  ``None``      |
+-----------------+------------------------------------------------------------------------------------+----------------+
| ``validators``  | A list of callables to provide external validation methods. See validators         |  ``None``      |
+-----------------+------------------------------------------------------------------------------------+----------------+
| ``projection``  | Determines how the field's data is serialized. See Projection                      |  ``True``      |
+-----------------+------------------------------------------------------------------------------------+----------------+
| ``readonly``    | Determines if data can be deserialized into this field. See Deserialization        |  ``False``     |
+-----------------+------------------------------------------------------------------------------------+----------------+
| ``primary_key`` | Used by resources to determine how to construct a resource URI                     |  ``False``     |
+-----------------+------------------------------------------------------------------------------------+----------------+


There are additional attributes which pertain only to specific fields. For example, ``min`` and ``max`` can be defined for an ``IntegerField`` to determine a range of acceptable values. See the API Reference for more details.


Composite Fields
^^^^^^^^^^^^^^^^^^

Composite fields are used to declare lists and dictionaries using the ``ListField`` and ``DictField`` fields respectively. A composite field is always based on another field which acts as the base type. 
A list of integers will be defined as ``ListField(IntegerField)`` and a dictionary of strings will be defined as ``DictField(StringField)`` .

The base field which defines the composite field can also accept the standard field attributes. The composite field itself can also define attributes related to its own behavior, like so::

    class M(Model):
        counters = DictField(IntegerField(default=0))
        tags = ListField(StringField(default='Unknown'), min_size=1, max_size=10)


Nested Models
~~~~~~~~~~~~~~

Documents can contain nested objects within them. In order to declare a nested object within your model, simply define the nested object as a model class and use the ``ModelField`` to associate it with your root Model, like so::

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


Nested objects can also be as the base fields for within lists and dictionaries, like so::

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

Every ``Model`` derived class has an internal ``Meta`` class which defines its default parameters. This is a very similar approach to meta information declared in Django models.

The following table lists the model options defined within the ``Meta`` class.

+-----------------+------------------------------------------------------------------------------------+----------------+
| Option            | Usage                                                                            | Default        |
+=================+====================================================================================+================+
| ``name``          | | Name of the model.                                                             | | name of      |
|                   | | This is used in persistency mixins to set the name in the datastore            | | the model    |
+-----------------+------------------------------------------------------------------------------------+----------------+
| ``namespace``     | Declares a namespace which prepends the name of the Model                        |  ``None``      |
+-----------------+------------------------------------------------------------------------------------+----------------+
| ``creation_args`` | Used by ``MongoCollectionMixin`` for passing creation arguments                  |  ``None``      |
+-----------------+------------------------------------------------------------------------------------+----------------+
| ``indices``       | Used to declare database indices                                                 |  ``None``      |
+-----------------+------------------------------------------------------------------------------------+----------------+



Import Data
----------------

There are multiple ways to manipulate data on a ``Model``. 

The most obvious is to access it's fields directly, like so::

    >>> book = Book()
    >>> b.title = 'Crime and Punishment'

While this example is pretty straighforward, it may not be very efficient if in cases were data is already stored in a ``dict`` which needs to be imported into a ``Model``.

The ``import_data`` method takes care of that, like so::

    >>> data = {
    ...     'title': 'Crime and Punishment',
    ...     'author': ' Fyodor Dostoyevsky',
    ...     'publication_date': '1866-01-01'  # actual date varies
    ... }
    >>> 
    >>> book = Book()
    >>> book.import_data(data)

A quicker way would be to use the ``Model`` constructor, like so::

    >> book = Book(data)

Data can be imported in a ``dict`` containing Python types, or data primitives. Once data is imported into the model is coerced into Python types.


Validation
----------------


Serialization
----------------

Models are responsible not only for declaring a schema and validating the data, but also for serializing the models to useful data structures. 
Controlling the way data models are serialized is extremely useful when creating APIs.
More often than not, developers may not want a straightforward one-to-one mapping between the data attributes of a model and the API.
In some cases there may be a need to omit some data, which is meant only for internal use and not for API consumption. 
In other cases there may be additional data attributes, required as part of an API endpoint, which are a result of a calculation, aggregation, or data manipulation between 1 or more data attributes. 

The following section reviews the tools that are implemented on the ``Model`` class and how they can be used to yield the desired results.


Serialization methods
~~~~~~~~~~~~~~~~~~~~~

The ``Model`` class has two methods for data serialization, which produce similar results but are intended for different uses.

The first method is ``to_python``. This method will serialize the model's fields and export methods (to be explained shortly) based on the rules dictated by the model. The result is a ``dict`` object containing all the relevant data.

The second method is ``to_data``. This method yields very similar result as ``to_python``. It also returns  ``dict`` object containing the fields and export methods. However, the difference is in the data types. 

The first method ``to_python`` serializes data primitives using native Python types.
the second method ``to_data`` serializes data primitives to data types which are not bound to the Python language. 

Serialization methods are co-routines and can only be run in an event loop.


The following example illustrates this::

    >>> from tbone.data.models import *
    >>> from tbone.data.fields import *
    >>> class Author(Model):
    ...     name = StringField()
    ...     dob = DateField()
    ...     rating = FloatField()
    ... 
    >>> a = Author({'name': 'John Steinbeck', 'dob' : '1902-02-27', 'rating': 4.7})

Now that we have an ``Author`` instance, lets see the difference between the two serialization methods::

    >>> obj = await a.to_python()
    >>> obj
    {'name': 'John Steinbeck', 'dob': datetime.date(1902, 2, 27), 'rating': 4.7}
    >>> type(obj)
    <class 'dict'>    

    >>> obj = await a.to_data()
    >>> obj
    {'name': 'John Steinbeck', 'dob': '1902-02-27', 'rating': 4.7}
    >>> type(obj)
    <class 'dict'>

.. note::
    Plain Python shell does cannot run co-routines as it does not have a running event loop. You can either script this code wrapped as a co-routine or use a 3rd party Python shell which supports an event loop.

Looking at the example above, both methods return a ``dict`` object with the ``Author`` instance's data. 
However, ``to_python`` returned ``dob`` as a ``datetime.date`` object while ``to_data`` returned ``dob`` as a ``str`` object.

The reason for this difference lies in the purpose of both methods.
The ``to_python`` method is meant for **inbound** serialization while the ``to_data`` method is meant for **outbound** serialization.

Inbound serialization is targeted at datastores, where Python's data primitives help maintain the data types more accurately. 
Outbound serialization is targted at APIs that use language-agnostic transport protocols such as ``JSON`` where Python data primitives are not valid.


Projection
~~~~~~~~~~~

The previous section went over ``Model`` serialization methods. This section covers specific instructions that can be added to the ``Field`` in order to determine how it is serialized. 

Every ``Field`` in the ``Model`` has a ``projection`` attribute, which defaults to ``True``. 
The projection field is a `ternary <https://en.wikipedia.org/wiki/Three-valued_logic>`_ value which can be set to either ``True``, ``False`` or ``None`` and determines the field's serialization in the following way:
    
    1. ``True`` means that the ``Field`` will always be serialized, even if its value is ``None``
    2. ``False`` means that the ``Field`` will only be serialized if its value is **not** ``None`` and will be skipped otherwise.
    3. ``None`` means that the ``Field`` will never be serialized, regardless of its value.

When a ``Model`` serialization method is called, it iterates through all the fields and uses the ``projection`` attribute to determine if and how to serialize the specific field.

The following example illustrates this::

    >>> from tbone.data.models import *
    >>> from tbone.data.fields import *
    >>> class BlogPost(Model):
    ...     title = StringField()
    ...     body = StringField()
    ...     number_of_views = IntegerField(default=0, projection=False)
    ... 
    >>> post = BlogPost({'title': 'Trees Are Tall', 'body': 'Trees can grow to be very tall ...'})
    >>> await post.to_data()
    {'title': 'Trees Are Tall', 'body': 'Trees can grow to be very tall ...'}
    >>> post.number_of_views += 1

The above example illustrates a ``Model`` that has a field used, in this case, for analytics, and is not required to be included as part of the API


``serialize`` methods
~~~~~~~~~~~~~~~~~~~~~~~~

When designing APIs, it is sometimes required to expose data which is not directly mapped to a single field in the model's schema.
Such data can be a result on a calculation, data aggregation or even data fetched sources ourside the model.
For this purpose, the ``Model`` class can implement serialize methods.

Serialize methods are regular member methods on the model with the following attributes:

    1. Serialize methods accept no external parameters and rely only on the model's data
    2. Serialize methods always return a primitive value
    3. Serialize methods are decorated with the ``@serialize`` decorator
    4. Serialize methods are coroutines and therefore are prefixed with ``async``

The following example illustrates this::

    >>> from tbone.data.models import *
    >>> from tbone.data.fields import *
    >>> class Trainee(Model):
    ...     weight = FloatField()
    ...     height = FloatField()
    ...     @serialize
    ...     async def bmi(self): # body mass index
    ...         return (self.weight*703)/(self.height*self.height)
    ... 
    >>> t = Trainee({'weight': 81.5, 'height' : 178})
    >>> t.to_data()
    {'weight': 81.5, 'height': 178.0, 'bmi': 1.8083101881075623}

(Please do not consider the above example to be a real BMI calculator)


The example above brings the quetion of why serialize methods need to be coroutines. 
In the ``bmi`` serialize example there are no lines of code which make use of the application's event loop.
However, serialize functions may include data from external sources as well. If such an implementation would not be using a coroutine the code will be blocking.
The following example illustrates this::

    from aiohttp import client
    from tbone.data.models import Model
    from tbone.data.fields import *

    API_KEY = '<get your own for free>';
    QUERY_URL = 'http://api.openweathermap.org/data/2.5/forecast?appid={key}&q={city},{state}'

    class CityInfo(Model):
        city = StringField()
        state = StringField()

        @serialize
        async def current_weather(self):
            async with aiohttp.ClientSession() as session:
                async with session.get(QUERY_URL.format(key=API_KEY, city=self.city, state=self.state)) as resp:
                    if resp.status == 200:  # http OK
                        data = await resp.json()
                        return data['list'][0]['main']['temp']
                    return None
    .
    .
    .
    city_info = CityInfo({'city': 'San Francisco', 'state': 'CA'})
    serialized_data = await city_info.to_data()


To see a fully working example, please visit the examples page






De-serialization
----------------

De-serialization is the process of constructing a data model from raw data, usually passed into the API.
The ``Model`` class implements a ``deserialize`` method which, by default, matches the data being passed to the fields defined on the model. Variables assigned are assigned to their respective fields and the object's data is validated. 
Developers may want to customize this behavior to control how models are deserialized, from data.

readonly
~~~~~~~~~

Every model field can be assigned with the ``readonly`` attribute.
This tells the model never to accept incoming data to certain fields using the deserialization method.
The following example illustrates this::

    class User(Model):
        username = StringField(required=True)
        password = StringField(readonly=True)






