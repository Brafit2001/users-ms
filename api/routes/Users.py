import random
import string
import traceback
from http import HTTPStatus
import mariadb
from flasgger import swag_from
from flask import Blueprint, jsonify, request

from api.models.PermissionModel import PermissionName, PermissionType
from api.models.UserModel import User
from api.services.AuthService import AuthService
from api.services.UserService import UserService
from api.utils.AppExceptions import EmptyDbException, NotFoundException
from api.utils.Logger import Logger
from api.utils.Security import Security

users = Blueprint('users_blueprint', __name__)


# EJEMPLO SWAGGER
# @swag_from("users.yml", methods=['GET'])

@users.route('/', methods=['GET'])
@Security.authenticate
@Security.authorize(permissions_required=[(PermissionName.USERS_MANAGER, PermissionType.READ)])
def get_all_users():
    try:
        users_list = UserService.get_all_users()
        response_users = []
        for user in users_list:
            response_users.append(user.to_json())
        response = jsonify({'success': True, 'data': response_users})
        return response, HTTPStatus.OK
    except mariadb.OperationalError as ex:
        response = jsonify({'success': False, 'message': str(ex)})
        return response, HTTPStatus.SERVICE_UNAVAILABLE
    except EmptyDbException as ex:
        response = jsonify({'success': False, 'message': ex.message})
        return response, ex.error_code
    except Exception as ex:
        Logger.add_to_log("error", str(ex))
        Logger.add_to_log("error", traceback.format_exc())
        response = jsonify({'message': str(ex), 'success': False})
        return response, HTTPStatus.INTERNAL_SERVER_ERROR


@users.route('/<user_id>', methods=['GET'])
@Security.authenticate
@Security.authorize(permissions_required=[(PermissionName.USERS_MANAGER, PermissionType.READ)])
def get_user_by_id(user_id: int):
    try:
        user_id = int(user_id)
        user = UserService.get_user_by_id(user_id)
        return user.to_json(), HTTPStatus.OK
    except NotFoundException as ex:
        response = jsonify({'message': ex.message, 'success': False})
        return response, ex.error_code
    except ValueError:
        return jsonify({'message': "User id must be an integer", 'success': False})
    except Exception as ex:
        Logger.add_to_log("error", str(ex))
        Logger.add_to_log("error", traceback.format_exc())
        response = jsonify({'message': str(ex), 'success': False})
        return response, HTTPStatus.INTERNAL_SERVER_ERROR


@users.route('/', methods=['POST'])
@Security.authenticate
@Security.authorize(permissions_required=[(PermissionName.USERS_MANAGER, PermissionType.WRITE)])
def add_user():
    try:

        password = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase +
                                          string.digits, k=6))
        _user = User(idUser=0, group=None, username=request.json["username"], password=password,
                     name=request.json["name"], surname=request.json["surname"], email=request.json["email"],
                     image=None)

        UserService.add_user(_user)
        response = jsonify({'message': 'User created successfully', 'success': True})
        return response, HTTPStatus.OK
    except KeyError:
        response = jsonify({'message': 'Bad body format', 'success': False})
        return response, HTTPStatus.BAD_REQUEST
    except mariadb.IntegrityError:
        response = jsonify({'message': 'Username is already taken', 'success': False})
        return response, HTTPStatus.BAD_REQUEST
    except Exception as ex:
        Logger.add_to_log("error", str(ex))
        Logger.add_to_log("error", traceback.format_exc())
        response = jsonify({'message': str(ex), 'success': False})
        return response, HTTPStatus.INTERNAL_SERVER_ERROR


@users.route('/<user_id>', methods=['DELETE'])
@Security.authenticate
@Security.authorize(permissions_required=[(PermissionName.USERS_MANAGER, PermissionType.WRITE)])
def delete_user(user_id):
    try:

        response = UserService.delete_user(user_id)
        return response, HTTPStatus.OK
    except NotFoundException as ex:
        response = jsonify({'success': False, 'message': ex.message})
        return response, ex.error_code
    except Exception as ex:
        response = jsonify({'message': str(ex), 'success': False})
        return response, HTTPStatus.INTERNAL_SERVER_ERROR


@users.route('/<user_id>', methods=['PUT'])
@Security.authenticate
@Security.authorize(permissions_required=[(PermissionName.USERS_MANAGER, PermissionType.WRITE)])
def edit_user(user_id):
    try:
        _user = User(
            idUser=user_id,
            group=None,
            username=request.json["username"],
            password=request.json["password"],
            name=request.json["name"],
            surname=request.json["surname"],
            email=request.json["email"],
            image=None
        )
        response = UserService.update_user(_user)
        return response, HTTPStatus.OK
    except NotFoundException as ex:
        response = jsonify({'success': False, 'message': ex.message})
        return response, ex.error_code
    except Exception as ex:
        Logger.add_to_log("error", str(ex))
        Logger.add_to_log("error", traceback.format_exc())
        response = jsonify({'message': str(ex), 'success': False})
        return response, HTTPStatus.INTERNAL_SERVER_ERROR


@users.route('/<user_id>/check-permissions', methods=['GET'])
@Security.authenticate
@Security.authorize(permissions_required=[(PermissionName.ROLES_MANAGER, PermissionType.READ)])
def check_user_permissions(user_id):
    try:
        permissions = AuthService.get_permissions(user_id)
        data = []
        for p in permissions:
            permission_id = p[0].value
            permission_name = p[0].name
            permission_type = p[1].name
            repeated = False
            for perm in data:
                if perm["id"] == permission_id:
                    perm["type"].append(permission_type)
                    repeated = True
            if repeated is False:
                data.append({"id": permission_id, "name": permission_name, "type": [permission_type]})
        response = jsonify({'data': data, 'success': True})
        return response, HTTPStatus.OK
    except Exception as ex:
        Logger.add_to_log("error", str(ex))
        Logger.add_to_log("error", traceback.format_exc())
        response = jsonify({'message': str(ex), 'success': False})
        return response, HTTPStatus.INTERNAL_SERVER_ERROR
