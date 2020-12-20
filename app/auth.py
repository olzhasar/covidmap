from flask import Response
from flask_basicauth import BasicAuth
from werkzeug.exceptions import HTTPException

auth = BasicAuth()


class AuthException(HTTPException):
    def __init__(self, message):
        super().__init__(
            message,
            response=Response(
                message, 401, {"WWW-Authenticate": 'Basic realm="Login Required"'}
            ),
        )
