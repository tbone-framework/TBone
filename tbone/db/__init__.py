#!/usr/bin/env python
# encoding: utf-8

import os
import time
import logging
from pymongo.errors import ConnectionFailure
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__file__)


def connect(**kwargs):
    db = None
    for i in range(kwargs['connection_retries'] + 1):
        try:
            url = os.environ.get('DATABASE_URL', None)
            if url is None:
                url = 'mongodb://{cred}{host}:{port}{extra}'.format(
                    cred='{}:{}@'.format(kwargs['username'], kwargs['password']) if len(kwargs['username']) > 0 else '',
                    host=kwargs['host'],
                    port=kwargs['port'],
                    extra=kwargs['extra']
                )
            db = AsyncIOMotorClient(url)[kwargs['name']]
            break
        except ConnectionFailure:
            if i >= kwargs['connection_retries']:
                raise
            else:
                timeout = kwargs['reconnect_timeout']
                logger.warning("ConnectionFailure #{0} during server initialization, waiting {1} seconds".format(i + 1, timeout))
                time.sleep(timeout)
    return db
