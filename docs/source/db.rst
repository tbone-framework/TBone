.. _db:

============
Data Persistency
============


Overview
------------

TBone provides data persistency in the form of mixin classes.
Mixin classes mix with your data models and extend the model's ability to perform CRUD operatons on its data into a datastore. 
A mixin class is targeted at a specific datastore and implements the underlying functionality over the datastore's API.

Like most parts of TBone, the functionality data persistency mixins should be implemented as nonblocking. Every method which calls upon the database should be implemented as a coroutine. The database driver must support nonblocking calls.
Failing to do so will limit's TBone efficiency and your app to be truly asynchorous. 


MongoDB
------------

TBone contains a ``MongoCollectionMixin`` which is a full data persistency mixin implementation over the MongoDB database, using `Motor <http://motor.readthedocs.io>`_ , the asynchronous python driver for MongoDB.





Extending to other datastores
------------------------------------





