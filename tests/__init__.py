#!/usr/bin/env python
# encoding: utf-8

import asyncio
import pytest


@pytest.fixture(scope='session')
def event_loop():
    '''
    Fixture for creating a single event loop for the entire test loop
    '''
    return asyncio.new_event_loop()