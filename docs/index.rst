.. TBone documentation master file, created by
   sphinx-quickstart on Tue Aug 29 12:13:14 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=================================
TBone Framework
=================================

TBone is a framework for building full-duplex, RESTful APIs on top of a Python asynchronous web-server using asyncio.

TBone is web-server agnostic, provided that the web-server is built on `asyncio`.
This means that it can work with either Sanic or Aiohttp and can be extended for other asyncio-based web-servers as well.
TBone was designed to be nonblocking and every component is implemented such that it works with the ```asyncio``` event loop 

Overview
------------

TBone is comprised of 3 major components:

1. Data Structure - an ODM-like modeling mechanism for data validation and serialization
2. Data Persistency - Persistency mixin classes for document stores with a full implementation for MongoDB
3. Resources - Mechanism for creating RESTful APIs



.. include:: source/contents.rst



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
