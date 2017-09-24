#!/usr/bin/env python
# encoding: utf-8

from asyncio import ensure_future
from collections import defaultdict, OrderedDict


class Channel(object):
    '''
    Abstract base class for all Channel implementations.
    Provides pure virtual methods for subclass implementations
    '''
    _name_prefix = 'tbone_channel_'
    _channels = {}

    def __new__(cls, **kwargs):
        ''' Make sure channels are singletons based on their names '''
        if 'name' not in kwargs:
            raise NameError('Channel must be instantiated with a name')

        name = kwargs['name']
        if name not in Channel._channels:
            new_channel = object.__new__(cls)
            new_channel._name = name
            new_channel.active = True
            new_channel._subscribers = defaultdict(list)  # create a dict of lists of subscribers
            Channel._channels[name] = new_channel
        return Channel._channels[name]

    def __repr__(self):  # pragma no cover
        return '<{} {}>'.format(self.__name__, self.name)

    @property
    def name(self):
        return '{}{}'.format(self._name_prefix, self._name)

    async def publish(self, key, data=None):
        raise NotImplementedError

    def subscribe(self, event, subscriber):
        self._subscribers[event].append(subscriber)

    def unsubscribe(self, event, subscriber):
        if subscriber in self._subscribers[event]:
            self._subscribers[event].remove(subscriber)

    def kickoff(self):
        ''' Initiates the channel and start listening to events '''
        ensure_future(self.consume_events())

    async def consume_events(self):
        raise NotImplementedError

