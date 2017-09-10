#!/usr/bin/env python
# encoding: utf-8

import datetime
from pymongo import ASCENDING, TEXT
from tbone.data.fields import *
from tbone.data.fields.mongo import ObjectIdField
from tbone.data.models import *
from tbone.db.models import MongoCollectionMixin


class CreditCardNumberField(StringField):
    pass  # TODO: implement luhn validation


class BaseModel(Model, MongoCollectionMixin):
    ''' Base model which adds a mongodb default _id field and an export method for object creation timestamp'''
    _id = ObjectIdField(primary_key=True)

    @export
    async def created(self):
        return self._id.generation_time.isoformat()


# ------  Basic  ------- #


class Person(BaseModel):
    first_name = StringField(required=True)
    last_name = StringField(required=True)

    @export
    async def full_name(self):  # redundant but good for testing
        return '{} {}'.format(self.first_name, self.last_name)


class Number(BaseModel):
    number = IntegerField()


# ------  Advanced  ------- #


class Review(Model):
    user = StringField(required=True)
    ratings = DictField(IntegerField)
    text = StringField()

    @export
    async def total_rating(self):
        return sum(self.ratings.values(), 0.0) / len(self.ratings.values())


class Book(Model, MongoCollectionMixin):
    isbn = StringField(primary_key=True)
    title = StringField(required=True)
    author = ListField(StringField)
    format = StringField(choices=['Paperback', 'Hardcover', 'Digital', 'Audiobook'], default='Paperback')
    publication_date = DateTimeField()  # MongoDB cannot persist dates only and accepts only datetime
    reviews = ListField(ModelField(Review))
    # internal attributes
    impressions = IntegerField(default=0, projection=None)
    views = IntegerField(default=0, projection=None)

    class Meta:
        name = 'books'
        namespace = 'catalog'

    indices = [{
        'name': '_isbn',
        'fields': [('isbn', ASCENDING)],
        'unique': True
    }, {
        'name': '_fts',
        'fields': [
            ('title', TEXT),
            ('author', TEXT)
        ]
    }]


class Profile(Model):
    title = StringField()
    first_name = StringField(required=True)
    last_name = StringField(required=True)
    suffix = StringField(projection=False)
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
    street_number = IntegerField()
    zipcode = StringField()
    state = StringField()
    country = StringField(required=True)


class Account(BaseModel):
    '''
    Main model for most unit tests, provides compregensive data on accounts.
    Useful when loading accounts.json fixture
    '''
    email = EmailField(required=True)
    password = StringField(required=True, projection=None)
    joined = DateTimeField(default=datetime.datetime.utcnow(), projection=None)
    profile = ModelField(Profile, required=True)
    gender = StringField(choices=['Male', 'Female'])
    home_address = ModelField(Address)
    phone_number = StringField()
    ip_address = StringField()
    premium = BooleanField(default=False)
    children = ListField(ModelField(Child))
    credit_card = ModelField(CreditCard)
    skills = ListField(StringField)

    class Meta:
        name = 'accounts'

    indices = [
        {
            'fields': [('email', ASCENDING)],
            'unique': True
        }, {
            'fields': [('phone_number', ASCENDING)],
            'unique': True,
            'partialFilterExpression': {'phone_number': {'$ne': None}}
        }
    ]
