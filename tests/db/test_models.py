#!/usr/bin/env python
# encoding: utf-8

import pytest
from tbone.data.fields import *
from tbone.data.fields.mongo import ObjectIdField
from tbone.data.models import *
from tbone.db.models import MongoDBMixin
from . import * 

@pytest.mark.asyncio
async def test_create_model_and_save(request, database):

    class Person(Model, MongoDBMixin):
        _id = ObjectIdField()
        first_name = StringField(required=True)
        last_name = StringField(required=True)

    # save model to db
    p1 = Person({'first_name': 'Ron', 'last_name': 'Burgundy'})
    await p1.save(db=database)

    # load model from db
    p2 = await Person.find_one(db=database, query={'first_name':'Ron'})
    assert isinstance(p2, Person)
    import pdb; pdb.set_trace()


