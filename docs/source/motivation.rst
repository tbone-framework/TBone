.. _motivation:

=================================
Motivation
=================================


TBone was desighed with a simple goal in mind, to make developing asyncronous web applications and web services easy, quick and painless.


Background
=================================

Developers who've gained experience working with frameworks such as Django, often find it difficult to make the switch to developing asyncronous web applications and services. This is mainly due to the initial confusion understanding concurrent programming, but also because, at the time of this writing, no clear path to quickly and easily develop RESTful APIs that can enjoy the benefits of concurent code and asynchronous web servers.


What TBone tries to solve
=================================

TBone was created to make it simple and easy to develop full-duplex RESTful APIs. This means that such APIs have bi-directional communication baked into them, so browser and mobile apps can enjoy efficient communication and a modern user experience. TBone utilizes both HTTP and Websocket protocols to expose REST-like APIs which makes it extremely simple to develop backends for a wide range of applications.

In addition, TBone provides a powerful Object Data Mapper (ODM) layer for data object validation and serialization, and a persistency layer for MongoDB.
Since the ODM layer is decoupled from the persistency layer, it is easy to extend TBone to work with other document stores.

With a REST-like Resource layer, an ODM and a MongoDB persitency layer, TBone makes it possible to develop web applications and services quickly and with a small code footprint. 


Minimum Opinions
=================================

TBone is an HTTP and Websocket agnostic framework. This means that developers can use either Sanic or Aiohttp as their http/websocket webserver based on their preferences. 
TBone does not impose an application structure or even a configuration patters. So you can easily add TBone to your existing asnyc web applications without having to work too hard to fit it in.


Antipatterns
=================================

Although TBone strives to be unopinionated as to your application architecture, there are several things which TBone assumes:

1. You are using Python 3.5 and above. At the time of this writing, Python 3.5 is considered a mainstream version of Python. In order to develop quickly and to make testing possible, we have decided not to support Python 2 or Python 3 versions prior to 3.5. This makes the code footprint smaller and easier to maintain.

2. TBone was designed to use asyncio and works with web servers which are built on top of asyncio. Although there are other asyncronous web servers (such as the wonderful Tornado) we chose to stick with asyncio only. 

