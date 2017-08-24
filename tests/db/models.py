#!/usr/bin/env python
# encoding: utf-8

import datetime
from tbone.data.fields import *
from tbone.data.fields.mongo import ObjectIdField
from tbone.data.models import *
from tbone.db.models import MongoCollectionMixin


class CreditCardNumberField(StringField):
    pass  # TODO: implement luhn validation


class BaseModel(Model, MongoCollectionMixin):
    ''' Base model which adds a mongofb default _id field and an export method for object creation '''
    _id = ObjectIdField()

    @export
    def created(self):
        return self._id.generation_time


# ------  Basic  ------- #


class Person(BaseModel):
    first_name = StringField(required=True)
    last_name = StringField(required=True)

    @export
    def full_name(self):  # redundant but good for testing
        return '{} {}'.format(self.first_name, self.last_name)


class Number(Model, MongoCollectionMixin):
    _id = ObjectIdField()
    number = IntegerField()


# ------  Advanced  ------- #

class Profile(Model):
    title = StringField()
    first_name = StringField(required=True)
    last_name = StringField(required=True)
    suffix = StringField(export_if_none=False)
    avatar = StringField()
    DOB = DateField()


class Child(Model):
    gender = StringField(choices=['M', 'F'])
    first_name = StringField(required=True)
    last_name = StringField(required=True)
    DOB = DateField()


class CreditCard(Model):
    number = CreditCardNumberField()
    type = StringField()


class Address(Model):
    city = StringField(required=True)
    street_name = StringField(required=True)
    street_number = IntegerField(required=True)
    zipcode = StringField()
    state = StringField()
    country = StringField(required=True)


class Account(BaseModel):
    '''
    Main model for most unit tests, provides compregensive data on accounts.
    Useful when loading accounts.json fixture
    '''
    email = EmailField(required=True)
    password = StringField(required=True)
    joined = DateTimeField(default=datetime.datetime.utcnow())
    profile = ModelField(Profile, required=True)
    gender = StringField(choices=['Male', 'Female'])
    home_address = ModelField(Address)
    phone_number = StringField()
    ip_address = StringField()
    premium = BooleanField(default=False)
    children = ListField(ModelField(Child))
    credit_card = ModelField(CreditCard)
    skills = ListField(StringField)

