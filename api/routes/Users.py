import csv
import io
import string
import traceback
from http import HTTPStatus
import random
import imghdr

import mariadb
import requests
from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash

from api.models.PermissionModel import PermissionName, PermissionType
from api.models.UserModel import User, row_to_user
from api.services.AuthService import AuthService
from api.services.UserService import UserService
from api.utils.AppExceptions import EmptyDbException, NotFoundException, BadCsvFormatException, EmailSendException, \
    PasswordCoincidenceException
from api.utils.EmailSend import sendPasswordEmail
from api.utils.FirebaseFunctions import readFirebase, uploadFirebase, deleteFirebase
from api.utils.Logger import Logger
from api.utils.QueryParameters import QueryParameters
from api.utils.Security import Security

users = Blueprint('users_blueprint', __name__)
GROUP_HOST = "http://groups-ms:8083"

PROFILE_IMAGES = ["user1", "user2", "user3", "user4"]


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
            if user.image not in PROFILE_IMAGES:
                user.image = readFirebase("images/users/%s" % user.image)
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


@users.route('/', methods=['POST'])
@Security.authenticate
@Security.authorize(permissions_required=[(PermissionName.USERS_MANAGER, PermissionType.WRITE)])
def add_user(*args):
    try:

        username = request.json["username"]
        name = request.json["name"]
        surname = request.json["surname"]
        email = request.json["email"]
        _user = User(userId=0, username=username, password="",
                     name=name, surname=surname, email=email,
                     image=random.choice(PROFILE_IMAGES))
        _user = UserService.add_user(_user)
        if not sendPasswordEmail(_user, 'Registration Confirmation', 'studentEmail.html'):
            UserService.delete_user(_user.id)
            raise EmailSendException("Email could not be send")
        response = jsonify({'message': 'User created successfully', 'success': True})
        return response, HTTPStatus.OK
    except EmailSendException as ex:
        response = jsonify({'message': ex.message, 'success': False})
        return response, ex.error_code
    except KeyError:
        response = jsonify({'message': 'Bad body format', 'success': False})
        return response, HTTPStatus.BAD_REQUEST
    except mariadb.IntegrityError as ex:
        print(ex)
        response = jsonify({'message': 'Username is already taken', 'success': False})
        return response, HTTPStatus.BAD_REQUEST
    except Exception as ex:
        Logger.add_to_log("error", str(ex))
        Logger.add_to_log("error", traceback.format_exc())
        response = jsonify({'message': str(ex), 'success': False})
        return response, HTTPStatus.INTERNAL_SERVER_ERROR


@users.route('/<user_id>', methods=['GET'])
@Security.authenticate
@Security.authorize(permissions_required=[(PermissionName.USERS_MANAGER, PermissionType.READ)])
def get_user_by_id(*args, **kwargs):
    try:
        user_id = int(kwargs["user_id"])
        user = UserService.get_user_by_id(user_id)
        # Nos conectamos a nuestra File Storage y buscamos el archivo
        if user.image not in PROFILE_IMAGES:
            user.image = readFirebase("images/users/%s" % user.image)
        response = jsonify({'success': True, 'data': user.to_json()})
        return response, HTTPStatus.OK
    except NotFoundException as ex:
        response = jsonify({'message': ex.message, 'success': False})
        return response, ex.error_code
    except ValueError as ex:
        Logger.add_to_log("error", str(ex))
        return jsonify({'message': "User id must be an integer", 'success': False})
    except Exception as ex:
        Logger.add_to_log("error", str(ex))
        Logger.add_to_log("error", traceback.format_exc())
        response = jsonify({'message': str(ex), 'success': False})
        return response, HTTPStatus.INTERNAL_SERVER_ERROR


@users.route('/<user_id>/roles', methods=['GET'])
@Security.authenticate
@Security.authorize(permissions_required=[(PermissionName.USERS_MANAGER, PermissionType.READ)])
def get_user_roles(*args, **kwargs):
    try:
        user_id = int(kwargs["user_id"])
        roles_list = UserService.get_user_roles(user_id)
        response_roles = []
        for role in roles_list:
            response_roles.append(role.to_json())
        response = jsonify({'success': True, 'data': response_roles})
        return response, HTTPStatus.OK
    except EmptyDbException as ex:
        response = jsonify({'success': False, 'message': ex.message})
        return response, ex.error_code
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


@users.route('/<user_id>/groups', methods=['GET'])
@Security.authenticate
@Security.authorize(permissions_required=[(PermissionName.USERS_MANAGER, PermissionType.READ)])
def get_user_groups(*args, **kwargs):
    try:
        user_id = int(kwargs["user_id"])
        groups_list = UserService.get_user_groups(user_id)
        response_groups = []
        for group in groups_list:
            response_groups.append(group.to_json())
        response = jsonify({'success': True, 'data': response_groups})
        return response, HTTPStatus.OK
    except EmptyDbException as ex:
        response = jsonify({'success': False, 'message': ex.message})
        return response, ex.error_code
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


@users.route('/<user_id>', methods=['DELETE'])
@Security.authenticate
@Security.authorize(permissions_required=[(PermissionName.USERS_MANAGER, PermissionType.WRITE)])
def delete_user(*args, **kwargs):
    try:
        user_id = int(kwargs["user_id"])
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


@users.route('/<user_id>/roles/<role_id>', methods=['DELETE'])
@Security.authenticate
@Security.authorize(permissions_required=[(PermissionName.USERS_MANAGER, PermissionType.WRITE)])
def delete_user_role(*args, **kwargs):
    try:
        user_id = int(kwargs["user_id"])
        role_id = int(kwargs["role_id"])
        response_message = UserService.delete_user_role(userId=user_id, roleId=role_id)
        response = jsonify({'message': response_message, 'success': True})
        return response, HTTPStatus.OK
    except NotFoundException as ex:
        response = jsonify({'message': ex.message, 'success': False})
        return response, ex.error_code
    except ValueError:
        return jsonify({'message': "User and Role id must be an integer", 'success': False})
    except Exception as ex:
        Logger.add_to_log("error", str(ex))
        Logger.add_to_log("error", traceback.format_exc())
        response = jsonify({'message': str(ex), 'success': False})
        return response, HTTPStatus.INTERNAL_SERVER_ERROR


@users.route('/<user_id>/groups/<group_id>', methods=['DELETE'])
@Security.authenticate
@Security.authorize(permissions_required=[(PermissionName.USERS_MANAGER, PermissionType.WRITE)])
def delete_user_group(*args, **kwargs):
    try:
        user_id = int(kwargs["user_id"])
        group_id = int(kwargs["group_id"])
        response_message = UserService.delete_user_group(userId=user_id, groupId=group_id)
        response = jsonify({'message': response_message, 'success': True})
        return response, HTTPStatus.OK
    except NotFoundException as ex:
        response = jsonify({'message': ex.message, 'success': False})
        return response, ex.error_code
    except ValueError:
        return jsonify({'message': "User and Group id must be an integer", 'success': False})
    except Exception as ex:
        Logger.add_to_log("error", str(ex))
        Logger.add_to_log("error", traceback.format_exc())
        response = jsonify({'message': str(ex), 'success': False})
        return response, HTTPStatus.INTERNAL_SERVER_ERROR


@users.route('/<user_id>', methods=['PUT'])
@Security.authenticate
@Security.authorize(permissions_required=[(PermissionName.USERS_MANAGER, PermissionType.WRITE)])
def edit_user(*args, **kwargs):
    try:
        Logger.add_to_log("info", request.form)
        user_id = int(kwargs["user_id"])
        image = ""
        if len(request.files) > 0:
            image = request.files['image']
            image_name = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase +
                                                string.digits, k=64))
            file_type = image.filename.split('.')[-1]
            image_name += '.' + file_type
        else:
            image_name = request.form['image']

        _user = User(
            userId=user_id,
            username=request.form["username"],
            password="",
            name=request.form["name"],
            surname=request.form["surname"],
            email=request.form["email"],
            image=image_name
        )

        oldUser = UserService.get_user_by_id(user_id)
        response_message = UserService.update_user(_user)

        # Si la imagen ha cambiado la eliminamos y añadimos la nueva a Firebase
        # (en caso de que no sean las imagenes por defecto).
        if oldUser.image != _user.image:
            deleteFirebase("images/users/%s" % oldUser.image)
            if _user.image not in PROFILE_IMAGES:
                uploadFirebase(image=image, path="images/users/%s" % image_name)

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
def check_user_permissions(*args, **kwargs):
    try:
        user_id = int(kwargs["user_id"])
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


@users.route('/<user_id>/change-password', methods=['PUT'])
@Security.authenticate
@Security.authorize(permissions_required=[(PermissionName.USERS_MANAGER, PermissionType.WRITE)])
def change_password(*args, **kwargs):
    try:
        user_id = int(kwargs["user_id"])
        password = request.json["password"]

        user = UserService.get_user_by_id(user_id)
        if check_password_hash(user.password, password):
            raise PasswordCoincidenceException('Password cannot be the same as the old one')
        user.password = password
        UserService.update_password(password, user_id)
        if not sendPasswordEmail(user, 'Password Changed', 'passwordUpdateEmail.html'):
            raise EmailSendException('Something went wrong sending the email')
        response = jsonify({'message': 'Password updated successfully', 'success': True})
        return response, HTTPStatus.OK
    except EmailSendException as ex:
        response = jsonify({'message': ex.message, 'success': False})
        return response, ex.error_code
    except PasswordCoincidenceException as ex:
        response = jsonify({'message': ex.message, 'success': False})
        return response, ex.error_code
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


@users.route('/<user_id>/reset-password', methods=['PUT'])
@Security.authenticate
@Security.authorize(permissions_required=[(PermissionName.USERS_MANAGER, PermissionType.WRITE)])
def reset_password(*args, **kwargs):
    try:
        user_id = int(kwargs["user_id"])
        password = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase +
                                          string.digits, k=6))

        user = UserService.get_user_by_id(user_id)
        user.password = password
        UserService.update_password(password, user_id)
        if not sendPasswordEmail(user, 'Password Changed', 'passwordUpdateEmail.html'):
            raise EmailSendException('Something went wrong sending the email')
        response = jsonify({'message': 'Password updated successfully', 'success': True})
        return response, HTTPStatus.OK
    except EmailSendException as ex:
        response = jsonify({'message': ex.message, 'success': False})
        return response, ex.error_code
    except PasswordCoincidenceException as ex:
        response = jsonify({'message': ex.message, 'success': False})
        return response, ex.error_code
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


@users.route('/import-csv', methods=['POST'])
@Security.authenticate
@Security.authorize(permissions_required=[(PermissionName.USERS_MANAGER, PermissionType.WRITE)])
def import_users_csv(*args):
    columns = ["username", "name", "surname", "email", "group name", "class name", "subject name", "course name",
               "course year"]
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
                row_info = row[0].split(';')

                # Dejamos la posición de la contraseña y la imagen en vacío
                row_info.insert(0, "")
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
                    user_id = UserService.add_user(_user).id
                    # Enviamos el correo
                    if not sendPasswordEmail(_user, 'Registration Confirmation', 'studentEmail.html'):
                        UserService.delete_user(_user.id)
                        raise EmailSendException("Email could not be send")
                    # Asignamos el usuario al grupo
                    UserService.assign_group(userId=user_id, groupId=group_id)
                    created.append(_user.username)

                except EmailSendException as ex:
                    response = jsonify({'message': ex.message, 'success': False})
                    return response, ex.error_code
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
