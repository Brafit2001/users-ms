import traceback
from http import HTTPStatus
from flask import request, jsonify, Blueprint
from api.models.UserModel import User
from api.services.AuthService import AuthService
from api.utils.Logger import Logger
from api.utils.Security import Security

auth = Blueprint('auth_blueprint', __name__)


@auth.route('/', methods=['POST'])
def login():
    try:
        # Recoger datos
        username = request.json['username']
        password = request.json['password']

        _user = User(userId=0, username=username, password=password, name='', surname='', email='',
                     image=None)

        authenticated_user = AuthService.login_user(_user)

        if authenticated_user is not None:
            encoded_token = Security.generate_token(authenticated_user)
            return jsonify({'token': encoded_token, 'success': True})
        else:
            response = jsonify({'message': 'Incorrect username or password'})
            return response, HTTPStatus.UNAUTHORIZED
    except Exception as ex:
        Logger.add_to_log("error", str(ex))
        Logger.add_to_log("error", traceback.format_exc())
        response = jsonify({'message': str(ex), 'success': False})
        return response, HTTPStatus.INTERNAL_SERVER_ERROR


@auth.route('/permissions', methods=['GET'])
@Security.authenticate
def get_permissions(*args):
    try:
        payload = args[0]
        userId = payload['userId']
        permissions = AuthService.get_permissions(userId)
        data = []
        for permission in permissions:
            data.append((permission[0].value, permission[1].value))
        response = jsonify({'data': data, 'success': True})
        return response, HTTPStatus.OK
    except Exception as ex:
        Logger.add_to_log("error", str(ex))
        Logger.add_to_log("error", traceback.format_exc())
        response = jsonify({'message': str(ex), 'success': False})
        return response, HTTPStatus.INTERNAL_SERVER_ERROR
