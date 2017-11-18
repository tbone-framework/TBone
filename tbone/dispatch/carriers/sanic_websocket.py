#!/usr/bin/env python
# encoding: utf-8


import json
import logging
from tbone.utils import ExtendedJSONEncoder
from . import Carrier

logger = logging.getLogger(__file__)


class SanicWebSocketCarrier(object):

    def __init__(self, websocket):
        self._socket = websocket

    async def deliver(self, data):
        try:
            if isinstance(data, dict):
                payload = json.dumps(data, cls=ExtendedJSONEncoder)
            elif isinstance(data, bytes):
                payload = data.decode('utf-8')
            else:
                payload = data
            await self._socket.send(payload)
            return True
        except Exception as ex:
            logger.exception(ex)
        return False
