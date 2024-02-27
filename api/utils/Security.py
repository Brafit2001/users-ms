import datetime
import traceback
from functools import wraps
from http import HTTPStatus

import jwt
import pytz
from decouple import config
from flask import request, jsonify

from api.utils.Logger import Logger


class Security:

    secret = config('SECRET_KEY')
    tz = pytz.timezone("Europe/Madrid")
    expiration_time = 10

    @classmethod
    def authenticate(cls, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not cls.verify_token(request.headers):
                response = jsonify({'error': 'Invalid token'})
                return response, HTTPStatus.UNAUTHORIZED

            return f(*args, **kwargs)

        return decorated_function

    @classmethod
    def generate_token(cls, authenticated_user):
        try:
            payload = {
                'iat': datetime.datetime.now(tz=cls.tz),
                'exp': datetime.datetime.now(tz=cls.tz) + datetime.timedelta(minutes=cls.expiration_time),
                'username': authenticated_user.username,
                'roles': []
            }
            return jwt.encode(payload, cls.secret, algorithm="HS256")
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())

    @classmethod
    def verify_token(cls, headers):
        try:
            if 'Authorization' in headers.keys():
                authorization = headers['Authorization']
                encoded_token = authorization.split(" ")[1]
                if (len(encoded_token) > 0) and (encoded_token.count('.') == 2):

                    try:
                        payload = jwt.decode(encoded_token, cls.secret, algorithms=["HS256"])
                        # TODO (Comprobar los roles)
                        '''
                        roles = list(payload['roles'])

                        if 'Administrator' in roles:
                            return True
                        return False
                        '''
                        # TODO (Retornar errores en caso del fallo del token)
                        return True
                    except (jwt.ExpiredSignatureError, jwt.InvalidSignatureError):
                        return False

            return False
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())

    @classmethod
    def check_role_permissions(cls):
        # TODO ()
        pass
