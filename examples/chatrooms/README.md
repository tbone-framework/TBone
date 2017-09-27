# Chatrooms Example App

This example demonstrates the full-duplex communication capabilities of TBone resources, by implementing a chatrooms app.

The design concept of this app is not optimized for large amounts of data.
It is used to demonstrate several key concepts:

1. Declare database models for users, chatrooms and entries
2. Create `MongoResource` based resources to expose users, chat rooms and entries as API endpoints
3. Demonstrate how resources can generate events, to be consumed by websocket clients
4. Demonstrate a custom Authentication class for resources (albeit pretty useless since it requires no password)
5. Using the `init_db.py` file, demonstrate how to bootstrap the application's database, create all collections and their indices


The app has entry code for `Sanic` based apps and `AioHttp` based app.

To launch the app with sanic call:

    $ python app_sanic.py

To launch the app with aiohttp call:

    $ python app_aiohttp.py


Please note that the relevant requirements must be installed, depending on which webserver you intend to use.


The `Entry` model implements a `MongoDB` capped collection to limit the amount of messages the database will store
