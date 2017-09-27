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

TBone has a suite of tests implemented on top of ``pytest``
Before running the tests additional requirements need to be installed, including ``pytest`` and ``pytest-asyncio``.
The file ``test.txt`` in the requirements directory lists all requirements needed for testing. 

To run all the tests execute the command in the root directory of the project::

    pytest

For coverage results run the following commands::

    coverage run --source tbone -m py.test
    coverage report  







Optional dependencies
=================================

TBone includes very few Python library dependencies. However, depending on the usage developers may need to manually install additional libraries:

Install ``sanic`` when using TBone with a sanic webserver::
    
    pip install sanic

Install ``aiohttp`` when using TBone with a aiohttp webserver::
    
    pip install aiohttp

To use the ``MongoDB`` persisrency layer and resources install ``Motor`` the asynchronous Python driver for MongoDB::
    
    pip install motor