from http import HTTPStatus
from flask import request, jsonify, Blueprint
from api.models.UserModel import User
from api.services.AuthService import AuthService

auth = Blueprint('auth_blueprint', __name__)


@auth.route('/', methods=['POST'])
def login():
    try:
        # Recoger datos
        username = request.json['username']
        password = request.json['password']

        _user = User(
            idUser=0,
            group=None,
            username=username,
            password=password,
            name='',
            surname='',
            email='',
            image=None
        )

        authenticated_user = AuthService.login_user(_user)
        print(authenticated_user)
        if authenticated_user is not None:
            return jsonify({'success': True, 'data': {'user': authenticated_user.username}})
        else:
            response = jsonify({'message': 'Incorrect username or password'})
            return response, HTTPStatus.UNAUTHORIZED

    except Exception as ex:
        return jsonify({'message': str(ex), 'success': False})
