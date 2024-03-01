import datetime
import traceback
from functools import wraps
from http import HTTPStatus

import jwt
import mariadb
import pytz
from decouple import config
from flask import request, jsonify, abort

from api.services.AuthService import AuthService
from api.utils.AppExceptions import NotAuthorized
from api.utils.Logger import Logger


class Security:
    secret = config('SECRET_KEY')
    tz = pytz.timezone("Europe/Madrid")
    expiration_time = 300

    @classmethod
    def authenticate(cls, func):
        """
        Método para autenticar al usuario. Llama a la función de validación del token

        :return
            - 'OK' : payload del token
            - 'error' : return error
        """
        @wraps(func)
        def decorated_function(*args, **kwargs):
            try:
                payload = cls.verify_token(request.headers)
                return func(payload, *args, **kwargs)
            except KeyError:
                response = jsonify({'error': 'Authorization header not found', 'success': False})
                return response, HTTPStatus.UNAUTHORIZED
            except (jwt.ExpiredSignatureError, jwt.InvalidSignatureError, jwt.exceptions.DecodeError) as ex:
                response = jsonify({'error': 'Token error - ' + str(ex), 'success': False})
                return response, HTTPStatus.UNAUTHORIZED
            except IndexError:
                response = jsonify({'error': 'Bad token format', 'success': False})
                return response, HTTPStatus.UNAUTHORIZED
            except Exception as ex:
                Logger.add_to_log("error", str(ex))
                Logger.add_to_log("error", traceback.format_exc())
                raise

        return decorated_function

    @classmethod
    def generate_token(cls, authenticated_user):
        """
        Se genera un token de autenticación con los datos del usuario.

            :param authenticated_user: Datos del usuario.
            :return:
                - 'OK':Devuelve el token generado
        """
        try:
            payload = {
                'iat': datetime.datetime.now(tz=cls.tz),
                'exp': datetime.datetime.now(tz=cls.tz) + datetime.timedelta(minutes=cls.expiration_time),
                'idUser': authenticated_user.id,
                'username': authenticated_user.username,
            }
            return jwt.encode(payload, cls.secret, algorithm="HS256")
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())
            raise

    @classmethod
    def verify_token(cls, headers):
        """
        Verifica el token de autenticación.
        :param headers: Encabezados de la petición.
        :return
            - 'OK':payload del token
        :raise: error
        """
        try:
            authorization = headers['Authorization']
            encoded_token = authorization.split(" ")[1]
            payload = jwt.decode(encoded_token, cls.secret, algorithms=["HS256"])
            return payload
        except IndexError:
            '''Bad token format'''
            raise
        except KeyError:
            '''Authorization header missing'''
            raise
        except jwt.InvalidSignatureError:
            '''Invalid signature'''
            raise
        except jwt.exceptions.DecodeError:
            '''Not enough segments'''
            raise
        except jwt.ExpiredSignatureError:
            "Token has expired"
            raise
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())
            raise

    @classmethod
    def authorize(cls, permissions_required: list):
        """
        Método para validar los permisos del usuario. Necesita que el usuario esté autenticado ya que obtiene
        el id del usuario a partir del payload obtenido en el método authenticate()

        :param permissions_required: lista de permisos requeridos
        :return
            - error: si el usuario no tiene permisos
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    payload = args[0]
                    idUser = payload['idUser']
                    permissions_list = AuthService.get_permissions(idUser)
                    for pr in permissions_required:
                        if pr not in permissions_list:
                            raise NotAuthorized('The user does not have the appropriate permissions')
                    return func(**kwargs)
                except NotAuthorized as ex:
                    response = jsonify({'success': False, 'message': ex.message})
                    return response, ex.error_code
                except mariadb.OperationalError as ex:
                    response = jsonify({'success': False, 'message': str(ex)})
                    return response, HTTPStatus.SERVICE_UNAVAILABLE
                except Exception as ex:
                    Logger.add_to_log("error", str(ex))
                    Logger.add_to_log("error", traceback.format_exc())
                    response = jsonify({'success': False, 'message': str(ex)})
                    return response, HTTPStatus.INTERNAL_SERVER_ERROR
            return wrapper

        return decorator
