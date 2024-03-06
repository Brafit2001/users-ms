import traceback
from http import HTTPStatus

from flask import Blueprint, jsonify, request

from api.models.InstagramModel import Instagram
from api.services.InstagramService import InstagramService
from api.utils.Logger import Logger
from api.utils.Security import Security

instagram = Blueprint('instagram_blueprint', __name__)


@instagram.route('/auth', methods=['POST'])
@Security.authenticate
def login(payload):
    try:
        clipclassUser = payload['userId']
        instaUser = request.json["username"]
        password = request.json["password"]
        _instaUser = Instagram(clipclassUser=clipclassUser, instagramUser=instaUser, password=password)
        insta_user = InstagramService.login(_instaUser)
        response = jsonify({'data': insta_user.to_json(), 'success': True})
        return response, HTTPStatus.OK
    except KeyError:
        response = jsonify({'message': 'Bad body format', 'success': False})
        return response, HTTPStatus.BAD_REQUEST
    except Exception as ex:
        Logger.add_to_log("error", str(ex))
        Logger.add_to_log("error", traceback.format_exc())
        response = jsonify({'message': str(ex), 'success': False})
        return response, HTTPStatus.INTERNAL_SERVER_ERROR


@instagram.route('/logout', methods=['GET'])
@Security.authenticate
def logout(payload):
    try:
        clipclassUser = payload['userId']

        _instaUser = Instagram(clipclassUser=clipclassUser, instagramUser=None)
        InstagramService.logout(_instaUser)
        response = jsonify({'message': 'User logout successfully', 'success': True})
        return response, HTTPStatus.OK
    except KeyError:
        response = jsonify({'message': 'Bad body format', 'success': False})
        return response, HTTPStatus.BAD_REQUEST
    except Exception as ex:
        Logger.add_to_log("error", str(ex))
        Logger.add_to_log("error", traceback.format_exc())
        response = jsonify({'message': str(ex), 'success': False})
        return response, HTTPStatus.INTERNAL_SERVER_ERROR
