import io
import random
import csv
import string
import traceback
from http import HTTPStatus

import mariadb
import requests
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin

from api.models.PermissionModel import PermissionName, PermissionType
from api.models.UserModel import User, row_to_user
from api.services.AuthService import AuthService
from api.services.UserService import UserService
from api.utils.AppExceptions import EmptyDbException, NotFoundException, BadCsvFormatException
from api.utils.Logger import Logger
from api.utils.QueryParameters import QueryParameters
from api.utils.Security import Security

users = Blueprint('users_blueprint', __name__)
GROUP_HOST = "http://localhost:8083"

# EJEMPLO SWAGGER
# @swag_from("users.yml", methods=['GET'])

@users.route('/', methods=['GET'])
@Security.authenticate
@Security.authorize(permissions_required=[(PermissionName.USERS_MANAGER, PermissionType.READ)])
def get_all_users(*args):
    try:
        params = QueryParameters(request)
        users_list = UserService.get_all_users(params)
        response_users = []
        for user in users_list:
            response_users.append(user.to_json())
        response = jsonify({'success': True, 'data': response_users})
        response.headers.set('Access-Control-Allow-Origin', '*')
        response.headers.set("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept")
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
        response = jsonify({'success': True, 'data': user.to_json()})
        return response, HTTPStatus.OK
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

        _user = User(userId=0, username=request.json["username"], password="",
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
        response_message = UserService.delete_user(user_id)
        response = jsonify({'message': response_message, 'success': True})
        return response, HTTPStatus.OK
    except NotFoundException as ex:
        response = jsonify({'success': False, 'message': ex.message})
        return response, ex.error_code
    except Exception as ex:
        Logger.add_to_log("error", str(ex))
        Logger.add_to_log("error", traceback.format_exc())
        response = jsonify({'message': str(ex), 'success': False})
        return response, HTTPStatus.INTERNAL_SERVER_ERROR


@users.route('/<user_id>', methods=['PUT'])
@Security.authenticate
@Security.authorize(permissions_required=[(PermissionName.USERS_MANAGER, PermissionType.WRITE)])
def edit_user(user_id):
    try:
        _user = User(
            userId=user_id,
            username=request.json["username"],
            password=request.json["password"],
            name=request.json["name"],
            surname=request.json["surname"],
            email=request.json["email"],
            image=None
        )
        response_message = UserService.update_user(_user)
        response = jsonify({'message': response_message, 'success': True})
        return response, HTTPStatus.OK
    except KeyError:
        response = jsonify({'message': 'Bad body format', 'success': False})
        return response, HTTPStatus.BAD_REQUEST
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


@users.route('/import-csv', methods=['POST'])
@Security.authenticate
@Security.authorize(permissions_required=[(PermissionName.USERS_MANAGER, PermissionType.WRITE)])
def import_users_csv(*args):
    columns = ["username", "name", "surname", "email", "group name", "class name", "subject name", "course name",
               "course year"]
    # QUITAR IMAGE (METER GROUP)
    try:
        created = []
        failed = []
        token = args[1]
        headers = {"Authorization": token, "Content-Type": "application/json"}
        csv_file = request.files['import-csv-users']
        stream = io.StringIO(csv_file.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.reader(stream)
        line_count = 0
        for row in csv_input:
            if line_count == 0:
                if row[0].split(';') != columns:
                    raise BadCsvFormatException(f"The csv Format is not correct - Header should be: "
                                                f"{columns}")
            if line_count != 0:
                # Ponemos el id a 0 (es incremental)
                row_info = [0] + row[0].split(';')
                # Dejamos la posición de la contraseña y la imagen en vacío
                row_info.insert(2, "")  # CONTRASEÑA
                row_info.insert(6, "")  # IMAGEN
                group_name = row_info[7]
                class_name = row_info[8]
                subject = row_info[9]
                course_name = row_info[10]
                course_year = row_info[11]
                _user = row_to_user(row_info)
                try:
                    # Obtenemos el id del grupo a partir de su información
                    group_id = requests.get(f'{GROUP_HOST}/groups/find-id-by-name?'
                                            f'name={group_name}&class={class_name}&subject={subject}&course={course_name}'
                                            f'&year={course_year}', headers=headers).json()["groupId"]
                    # Añadimos el usuario
                    user_id = UserService.add_user(_user)
                    # Asignamos el usuario al grupo
                    UserService.assign_group(userId=user_id, groupId=group_id)
                    created.append(_user.username)

                except KeyError:
                    response = {'user': _user.username, 'reason': 'Bad format'}
                    failed.append(response)
                except mariadb.IntegrityError:
                    response = {'user': _user.username, 'reason': 'User already exists'}
                    failed.append(response)
                except Exception as ex:
                    Logger.add_to_log("error", str(ex))
                    Logger.add_to_log("error", traceback.format_exc())
                    response = {'user': _user.username, 'reason': str(ex)}
                    failed.append(response)

            line_count += 1

        response = jsonify({'message': 'Process Completed', 'created': created, 'failed': failed, 'success': True})
        return response, HTTPStatus.OK
    except KeyError:
        response = jsonify({'message': 'Bad key file format - should be `import-csv-users`', 'success': False})
        return response, HTTPStatus.BAD_REQUEST
    except BadCsvFormatException as ex:
        response = jsonify({'message': ex.message, 'success': False})
        return response, ex.error_code
    except Exception as ex:
        Logger.add_to_log("error", str(ex))
        Logger.add_to_log("error", traceback.format_exc())
        response = jsonify({'message': str(ex), 'success': False})
        return response, HTTPStatus.INTERNAL_SERVER_ERROR
