#!/usr/bin/env python
# encoding: utf-8

import phonenumbers
from .simple import StringField


class PhoneNumber(phonenumbers.phonenumber.PhoneNumber):
    '''
    extend phonenumbers.phonenumber.PhoneNumber with easier accessors
    '''
    FORMATS = {
        'E164': phonenumbers.PhoneNumberFormat.E164,
        'INTERNATIONAL': phonenumbers.PhoneNumberFormat.INTERNATIONAL,
        'NATIONAL': phonenumbers.PhoneNumberFormat.NATIONAL,
        'RFC3966': phonenumbers.PhoneNumberFormat.RFC3966,
    }
    default_format = 'INTERNATIONAL'
    _region = ''

    def __repr__(self):
        fmt = self.FORMATS[self.default_format]
        return '<{} {}>'.format(self.__class__.__name__, self.format_as(fmt))

    @classmethod
    def from_string(cls, phone_number, region=None):
        try:
            phone_number_obj = cls()
            phonenumbers.parse(number=phone_number, region=region,
                               keep_raw_input=True, numobj=phone_number_obj)
            return phone_number_obj
        except phonenumbers.phonenumberutil.NumberParseException:
            return None

    def is_valid(self):
        return phonenumbers.is_valid_number(self)

    @property
    def as_international(self):
        return self.format_as(phonenumbers.PhoneNumberFormat.INTERNATIONAL)

    @property
    def as_e164(self):
        return self.format_as(phonenumbers.PhoneNumberFormat.E164)

    @property
    def as_national(self):
        return self.format_as(phonenumbers.PhoneNumberFormat.NATIONAL)

    @property
    def as_rfc3966(self):
        return self.format_as(phonenumbers.PhoneNumberFormat.RFC3966)

    @property
    def digits(self):
        return self.format_as(phonenumbers.PhoneNumberFormat.E164)[1:]

    def format_as(self, format):
        return phonenumbers.format_number(self, format)

    def __len__(self):
        return len(self.__unicode__())

    def __eq__(self, other):
        '''
        Override parent equality because we store only string representation
        of phone number, so we must compare only this string representation
        '''
        if (isinstance(other, PhoneNumber) or
                isinstance(other, phonenumbers.phonenumber.PhoneNumber) or
                isinstance(other, str)):

            fmt = self.FORMATS['E164']
            if isinstance(other, str):
                # convert string to phonenumbers.phonenumber.PhoneNumber instance
                try:
                    other = phonenumbers.phonenumberutil.parse(other)
                except phonenumbers.phonenumberutil.NumberParseException:
                    # Conversion is not possible, thus not equal
                    return False
            other_string = phonenumbers.format_number(other, fmt)
            return self.format_as(fmt) == other_string
        else:
            return False


class PhoneNumberDescriptor(object):
    '''
    Descriptor for the phone number field. returns a PhoneNumber object.
    use like this:
        customer.phone_number.as_international
        customer.phone_number.as_national
        customer.phone_number.as_e164
    '''
    def __init__(self, field):
        self.field = field

    def __get__(self, instance=None, owner=None):
        if instance is None:
            raise AttributeError(
                "The '%s' attribute can only be accessed from %s instances."
                % (self.field.name, owner.__name__))
        value = instance.__dict__[self.field]
        if value is None or isinstance(value, PhoneNumber):
            return value
        return PhoneNumber.from_string(value)

    def __set__(self, instance, value):
        instance.__dict__[self.field] = value


class PhoneNumberField(StringField):
    ERRORS = {
        'invalid': "Invalid phone number",
    }

    def to_data(self, value):
        if value is None:
            return None
        if isinstance(value, PhoneNumber):
            return value.as_e164
        phone_number = PhoneNumber.from_string(value)
        if phone_number:
            return phone_number.as_e164
        raise ValueError(self._errors['invalid'])

    def add_to_class(self, cls, name):
        '''
        Overrides the base class to add a PhoheNumberDescriptor rather than the standard FieldDescriptor
        '''
        self.model_class = cls
        setattr(cls, name, PhoneNumberDescriptor(self))
        self._bound = True
