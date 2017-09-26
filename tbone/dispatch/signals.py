#!/usr/bin/env python
# encoding: utf-8


import asyncio
import logging
from functools import wraps
from weakref import WeakMethod, ref
from asyncio import Lock


logger = logging.getLogger(__file__)

lock = Lock()


def _make_id(target):
    if hasattr(target, '__func__'):
        return (id(target.__self__), id(target.__func__))
    return id(target)


class Signal(object):
    ''' Base class for all signals '''
    def __init__(self):
        self.receivers = {}

    def connect(self, receiver, sender):
        '''
        Connects a signal to a receiver function

        :param receiver:
            The callback function which will be connected to this signal

        :param sender:
            Specifies a particular sender to receive signals from.
            Used to limit the receiver function to signal from particular sender types
        '''
        logger.info('Signal connected: {}'.format(receiver))
        ''' connect a receiver to a sender for signaling '''
        assert callable(receiver)
        receiver_id = _make_id(receiver)
        sender_id = _make_id(sender)
        r = ref
        if hasattr(receiver, '__self__') and hasattr(receiver, '__func__'):
            r = WeakMethod

        receiver = r(receiver)

        self.receivers.setdefault((receiver_id, sender_id), receiver)

    def disconnect(self, receiver, sender):
        logger.info('Signal disconnected: {}'.format(receiver))
        receiver_id = _make_id(receiver)
        sender_id = _make_id(sender)
        del self.receivers[(receiver_id, sender_id)]

    async def send(self, sender, **kwargs):
        ''' send a signal from the sender to all connected receivers '''
        if not self.receivers:
            return []
        responses = []
        futures = []
        for receiver in self._get_receivers(sender):
            method = receiver()
            if callable(method):
                futures.append(method(sender=sender, **kwargs))
        if len(futures) > 0:
            responses = await asyncio.gather(*futures)
        return responses


    def _get_receivers(self, sender):
        ''' filter only receiver functions which correspond to the provided sender '''
        key = _make_id(sender)
        receivers = []
        for (receiver_key, sender_key), receiver in self.receivers.items():
            if sender_key == key:
                receivers.append(receiver)
        return receivers


def receiver(signal, **kwargs):
    def decorator(func):
        @wraps(func)
        def wrapper(signal, **kwargs):
            ioloop.IOLoop.instance().add_callback(callback=lambda: signal.connect(func, **kwargs))
        return wrapper
    return decorator