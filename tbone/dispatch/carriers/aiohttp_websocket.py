#!/usr/bin/env python
# encoding: utf-8


import json
import logging
from tbone.utils import ExtendedJSONEncoder
from . import Carrier

logger = logging.getLogger(__file__)


class AioHttpWebSocketCarrier(object):

    def __init__(self, websocket):
        self._socket = websocket

    async def deliver(self, data):
        try:
            self._socket.send_str(
                json.dumps(data, cls=ExtendedJSONEncoder)
            )
            return True
        except Exception as ex:
            logger.exception(ex)
        return False
