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
    ''' Base model which adds a mongodb default _id field and an serialize method for object creation timestamp'''
    _id = ObjectIdField(primary_key=True)

    class Meta:
        concrete = False

    @serialize
    async def created(self):
        return self._id.generation_time.isoformat()


# ------  Basic  ------- #


class Person(BaseModel):
    first_name = StringField(required=True)
    last_name = StringField(required=True)

    @serialize
    async def full_name(self):  # redundant but good for testing
        return '{} {}'.format(self.first_name, self.last_name)


class Number(BaseModel):
    number = IntegerField()


# ------  Advanced  ------- #


class Review(Model):
    user = StringField(required=True)
    ratings = DictField(IntegerField)
    text = StringField()

    @serialize
    async def total_rating(self):
        return sum(self.ratings.values(), 0.0) / len(self.ratings.values())


class Book(Model, MongoCollectionMixin):
    isbn = StringField(primary_key=True)
    title = StringField(required=True)
    author = ListField(StringField)
    format = StringField(choices=['Paperback', 'Hardcover', 'Digital', 'Audiobook'], default='Paperback')
    publication_date = DateTimeField()  # MongoDB cannot persist dates only and accepts only datetime
    reviews = ListField(ModelField(Review), default=[])
    # internal attributes
    number_of_impressions = IntegerField(default=0, projection=None)
    number_of_views = IntegerField(default=0, projection=None)

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

    async def add_review(self, db, review_data):
        ''' Adds a review to the list of reviews, without fetching and updating the entire document '''
        db = db or self.db
        # create review model instance
        new_rev = Review(review_data)
        data = new_rev.export_data(native=True)
        # use model's pk as query
        query = {self.primary_key: self.pk}
        # push review
        result = await db[self.get_collection_name()].update_one(
            filter=query,
            update={'$push': {'reviews': data}},
        )
        return result

    async def inc_number_of_impressions(self, db):
        ''' Increment the number of views by 1 '''
        db = db or self.db
        # use model's pk as query
        query = {self.primary_key: self.pk}
        # push review
        result = await db[self.get_collection_name()].update_one(
            filter=query,
            update={'$inc': {'number_of_impressions': 1}},
        )
        return result

    async def inc_number_of_views(self, db):
        ''' Increment the number of views by 1 '''
        db = db or self.db
        # use model's pk as query
        query = {self.primary_key: self.pk}
        # push review
        result = await db[self.get_collection_name()].update_one(
            filter=query,
            update={'$inc': {'number_of_views': 1}},
        )
        return result


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
