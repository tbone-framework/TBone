#!/usr/bin/env python
# encoding: utf-8

import asyncio
import pytest
import json


@pytest.fixture(scope='session')
def event_loop():
    '''
    Fixture for creating a single event loop for the entire test loop
    '''
    return asyncio.new_event_loop()


@pytest.fixture(scope='function')
def json_fixture():
    '''
    Fixture for loading json fixture files
    '''
    def _method(filename):
        with open('tests/fixtures/{}'.format(filename)) as data_file:
            data = json.load(data_file)
        return data
    return _method
