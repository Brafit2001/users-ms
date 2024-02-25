import traceback
from http import HTTPStatus

from flask import Blueprint, jsonify, request

from api.models.UserModel import User
from api.services.UserService import UserService
from api.utils.Logger import Logger

users = Blueprint('users_blueprint', __name__)


@users.route('/', methods=['GET'])
def get_all_users():
    try:
        users_list = UserService.get_all_users()
        if users_list is not None:
            response_users = []
            for user in users_list:
                response_users.append(user.to_json())
            return jsonify({'success': True, 'data': response_users})
        else:
            response = jsonify({'message': 'User db is empty', 'success': False})
            return response, HTTPStatus.NOT_FOUND

    except Exception as ex:
        Logger.add_to_log("error", str(ex))
        Logger.add_to_log("error", traceback.format_exc())
        return jsonify({'message': str(ex), 'success': False})


@users.route('/<user_id>', methods=['GET'])
def get_user_by_id(user_id: int):
    try:
        user_id = int(user_id)
        user = UserService.get_user_by_id(user_id)
        if user is not None:
            return user.to_json(), HTTPStatus.OK
        else:
            response = jsonify({'message': 'User not found', 'success': False})
            return response, HTTPStatus.NOT_FOUND

    except ValueError:
        return jsonify({'message': "User id must be an integer", 'success': False})
    except Exception as ex:
        Logger.add_to_log("error", str(ex))
        Logger.add_to_log("error", traceback.format_exc())
        return jsonify({'message': str(ex), 'success': False})


@users.route('/', methods=['POST'])
def add_user():
    try:
        _user = User(
            idUser=0,
            group=None,
            username=request.json["username"],
            password=request.json["password"],
            name=request.json["name"],
            surname=request.json["surname"],
            email=request.json["email"],
            image=None
        )
        response = UserService.add_user(_user)
        return response, HTTPStatus.OK
    except Exception as ex:
        Logger.add_to_log("error", str(ex))
        Logger.add_to_log("error", traceback.format_exc())
        return jsonify({'message': str(ex), 'success': False})


@users.route('/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        response = UserService.delete_user(user_id)
        return response, HTTPStatus.OK
    except Exception as ex:
        Logger.add_to_log("error", str(ex))
        Logger.add_to_log("error", traceback.format_exc())
        return jsonify({'message': str(ex), 'success': False})


@users.route('/<user_id>', methods=['PUT'])
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
    except Exception as ex:
        Logger.add_to_log("error", str(ex))
        Logger.add_to_log("error", traceback.format_exc())
        return jsonify({'message': str(ex), 'success': False})
