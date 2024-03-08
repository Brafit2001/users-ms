import traceback
from http import HTTPStatus

import mariadb
from flask import Blueprint, jsonify, request

from api.models.PermissionModel import PermissionName, PermissionType
from api.models.RoleModel import Role
from api.services.RoleService import RoleService
from api.utils.AppExceptions import EmptyDbException, NotFoundException
from api.utils.Logger import Logger
from api.utils.Security import Security

roles = Blueprint('roles_blueprint', __name__)


# EJEMPLO SWAGGER
# @swag_from("users.yml", methods=['GET'])

# @Security.authenticate
# @Security.authorize(permissions_required=[(PermissionName.VERIFY, PermissionType.READ)])

@roles.route('/', methods=['GET'])
@Security.authenticate
@Security.authorize(permissions_required=[(PermissionName.ROLES_MANAGER, PermissionType.READ)])
def get_all_roles():
    try:
        roles_list = RoleService.get_all_roles()
        response_roles = []
        for role in roles_list:
            response_roles.append(role.to_json())
        response = jsonify({'success': True, 'data': response_roles})
        return response, HTTPStatus.OK
    except EmptyDbException as ex:
        response = jsonify({'success': False, 'message': ex.message})
        return response, ex.error_code
    except Exception as ex:
        Logger.add_to_log("error", str(ex))
        Logger.add_to_log("error", traceback.format_exc())
        response = jsonify({'message': str(ex), 'success': False})
        return response, HTTPStatus.INTERNAL_SERVER_ERROR


@roles.route('/<role_id>', methods=['GET'])
@Security.authenticate
@Security.authorize(permissions_required=[(PermissionName.ROLES_MANAGER, PermissionType.READ)])
def get_role_by_id(role_id: int):
    try:
        role_id = int(role_id)
        role = RoleService.get_role_by_id(role_id)
        return role.to_json(), HTTPStatus.OK

    except NotFoundException as ex:
        response = jsonify({'message': ex.message, 'success': False})
        return response, ex.error_code
    except ValueError:
        return jsonify({'message': "Role id must be an integer", 'success': False})
    except Exception as ex:
        Logger.add_to_log("error", str(ex))
        Logger.add_to_log("error", traceback.format_exc())
        response = jsonify({'message': str(ex), 'success': False})
        return response, HTTPStatus.INTERNAL_SERVER_ERROR


@roles.route('/', methods=['POST'])
@Security.authenticate
@Security.authorize(permissions_required=[(PermissionName.ROLES_MANAGER, PermissionType.WRITE)])
def add_role():
    try:
        _role = Role(idRole=0, name=request.json["name"])
        RoleService.add_role(_role)
        response = jsonify({'message': 'Role created successfully', 'success': True})
        return response, HTTPStatus.OK
    except KeyError:
        response = jsonify({'message': 'Bad body format', 'success': False})
        return response, HTTPStatus.BAD_REQUEST
    except mariadb.IntegrityError:
        response = jsonify({'message': 'Role already exists', 'success': False})
        return response, HTTPStatus.BAD_REQUEST
    except Exception as ex:
        Logger.add_to_log("error", str(ex))
        Logger.add_to_log("error", traceback.format_exc())
        response = jsonify({'message': str(ex), 'success': False})
        return response, HTTPStatus.INTERNAL_SERVER_ERROR


@roles.route('/<role_id>', methods=['DELETE'])
@Security.authenticate
@Security.authorize(permissions_required=[(PermissionName.ROLES_MANAGER, PermissionType.WRITE)])
def delete_role(role_id: int):
    try:
        role_deleted = RoleService.delete_role(role_id)
        response = jsonify({'message': f'Role with name <{role_deleted.name}> deleted successfully', 'success': True})
        return response, HTTPStatus.OK
    except NotFoundException as ex:
        response = jsonify({'success': False, 'message': ex.message})
        return response, ex.error_code
    except Exception as ex:
        Logger.add_to_log("error", str(ex))
        Logger.add_to_log("error", traceback.format_exc())
        response = jsonify({'message': str(ex), 'success': False})
        return response, HTTPStatus.INTERNAL_SERVER_ERROR


@roles.route('/<role_id>', methods=['PUT'])
@Security.authenticate
@Security.authorize(permissions_required=[(PermissionName.ROLES_MANAGER, PermissionType.WRITE)])
def edit_role(role_id):
    try:
        _role = Role(idRole=role_id, name=request.json["name"])
        RoleService.update_role(_role)
        response = jsonify({'message': f'Role with id <{role_id}> updated successfully', 'success': True})
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


@roles.route('/assign-user-to-role', methods=['POST'])
@Security.authenticate
@Security.authorize(permissions_required=[(PermissionName.ROLES_MANAGER, PermissionType.WRITE)])
def assign_role():
    try:
        user_id = request.json["user"]
        role_id = request.json["role"]
        RoleService.assign_role(user_id, role_id)
        response = jsonify({'message': 'Role successfully assigned to user', 'success': True})
        return response, HTTPStatus.OK
    except KeyError:
        response = jsonify({'message': 'Bad body format', 'success': False})
        return response, HTTPStatus.BAD_REQUEST
    except mariadb.IntegrityError:
        response = jsonify({'message': 'The User has already the role', 'success': False})
        return response, HTTPStatus.BAD_REQUEST
    except Exception as ex:
        Logger.add_to_log("error", str(ex))
        Logger.add_to_log("error", traceback.format_exc())
        response = jsonify({'message': str(ex), 'success': False})
        return response, HTTPStatus.INTERNAL_SERVER_ERROR

