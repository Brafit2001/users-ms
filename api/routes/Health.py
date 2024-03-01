import traceback
from http import HTTPStatus

from flask import Blueprint, jsonify

from api.utils.Logger import Logger

health = Blueprint('health_blueprint', __name__)


@health.route('/', methods=['GET'])
def get_health():
    try:
        return 'OK'
    except Exception as ex:
        Logger.add_to_log("error", str(ex))
        Logger.add_to_log("error", traceback.format_exc())
        response = jsonify({'message': str(ex), 'success': False})
        return response, HTTPStatus.INTERNAL_SERVER_ERROR



