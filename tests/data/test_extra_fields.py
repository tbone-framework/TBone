#!/usr/bin/env python
# encoding: utf-8

from tbone.data.fields.phone_number import PhoneNumber, PhoneNumberField


def test_phone_number_field():
    VALID = '+16505434800'
    INVALID = '111111111'

    f = PhoneNumberField()
    pn = PhoneNumber.from_string(VALID)
    data = f.to_data(pn)
    assert data == VALID  # this is true because the default parsing is e164

    pn = PhoneNumber.from_string(INVALID)
    assert pn is None
