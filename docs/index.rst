.. tbone documentation master file, created by
   sphinx-quickstart on Thu Aug 24 20:58:13 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=================================
TBone
=================================

TBone is a framework for building full-duplex, RESTFul APIs on top of a Python asynchronous web-server using asyncio.

TBone is web-server agnostic, assuming it is built on with asyncio.
This means that it can work with either Sanic or Aiohttp and can be extended for other web-servers as well.

Overview
------------

TBone is comprised of 3 major components:

1. Data management
2. Persistency 
3. API Resources

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   tbone/getting_started



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
