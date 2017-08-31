.. _installation:

=================================
Installation and Testing
=================================

Requirements
=================================

The following are requirements to use TBone:

1. TBone requires an asyncronous web server, based on `asyncio` to run on. Out of the box it supports both `Sanic` and `Aiohttp` . It is possible to extend TBone to work with other `asyncio` based web servers
2. TBone works with Python 3.5+ this is due to the use of the async/await syntax. Earlier versions of python will not work.

The easiest way to install TBone is through PyPI::

    pip install tbone


Installation with git
=================================

The project is hosted at https://github.com/475cumulus/tbone and can be installed using git: ::

    git clone https://github.com/475cumulus/tbone.git
    cd tbone
    python setup.py install



Running the tests
=================================

Optional dependencies
=================================