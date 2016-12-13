#!/usr/bin/env python
# encoding: utf-8


# HTTP Status Codes
OK = 200
CREATED = 201
ACCEPTED = 202
NO_CONTENT = 204

BAD_REQUEST = 400
UNAUTHORIZED = 401
NOT_FOUND = 404
METHOD_NOT_ALLOWED = 405

APPLICATION_ERROR = 500
METHOD_NOT_IMPLEMENTED = 501


class HttpError(Exception):
    status = APPLICATION_ERROR
    msg = "Application Error"

    def __init__(self, msg=None):
        if not msg:
            msg = self.__class__.msg
        super(HttpError, self).__init__(msg)


class BadRequest(HttpError):
    status = BAD_REQUEST
    msg = "Bad request"


class Unauthorized(HttpError):
    status = UNAUTHORIZED
    msg = "Unauthorized"


class NotFound(HttpError):
    status = NOT_FOUND
    msg = "Resource not found"


class MethodNotAllowed(HttpError):
    status = METHOD_NOT_ALLOWED
    msg = "The specified HTTP method is not allowed"


class MethodNotImplemented(HttpError):
    status = METHOD_NOT_IMPLEMENTED
    msg = "The specified HTTP method is not implemented"
