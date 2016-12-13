#!/usr/bin/env python
# encoding: utf-8


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
        self.receivers = []

    async def connect(self, receiver, sender):
        ''' connect a receiver to a sender for signaling '''
        assert callable(receiver)
        key = (_make_id(receiver), _make_id(sender))
        r = ref
        if hasattr(receiver, '__self__') and hasattr(receiver, '__func__'):
            r = WeakMethod

        receiver = r(receiver)

        with (await lock.acquire()):
            for receiver_key, _ in self.receivers:
                if receiver_key == key:
                    break
            else:
                self.receivers.append((key, receiver))

    async def send(self, sender, **kwargs):
        ''' send a signal from the sender to all connected receivers '''
        if not self.receivers:
            return []
        responses = []
        for receiver in self._get_receivers(sender):
            method = receiver()
            if callable(method):
                response = await method(sender=sender, **kwargs)
                responses.append((receiver, response))
        return responses

    def _get_receivers(self, sender):
        ''' filter only receiver functions which correspond to the provided sender '''
        key = _make_id(sender)
        receivers = []
        for (sender_key, receiver_key), receiver in self.receivers:
            if receiver_key == key:
                receivers.append(receiver)
        return receivers


def receiver(signal, **kwargs):
    def decorator(func):
        @wraps(func)
        def wrapper(signal, **kwargs):
            ioloop.IOLoop.instance().add_callback(callback=lambda: signal.connect(func, **kwargs))
        return wrapper
    return decorator