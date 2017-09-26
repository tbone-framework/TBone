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
        '''
        Publish an event to the channel, to be sent to all subscribers
        
        :param key:
            The name of the event
        :param data:
            The data to be passed with the event. The data must be such that it can be encoded to JSON
        '''
        raise NotImplementedError

    def subscribe(self, event, subscriber):
        '''
        Subscribe to channel events.

        :param event:
            The name of the event to subscribe to. String based

        :param subscriber:
            A ``Carrier`` type object which delivers the message to its target
        '''
        self._subscribers[event].append(subscriber)

    def unsubscribe(self, event, subscriber):
        if subscriber in self._subscribers[event]:
            self._subscribers[event].remove(subscriber)

    def kickoff(self):
        '''
        Initiates the channel and start listening to events.
        This method should be called at the startup sequence of the app, or as soon as events should be listened to.
        Pushes ``consume_events`` into the event loop.
        '''
        ensure_future(self.consume_events())

    async def consume_events(self):
        raise NotImplementedError

