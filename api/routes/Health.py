from flask import Blueprint

health = Blueprint('health_blueprint', __name__)


@health.route('/', methods=['GET'])
def get_health():
    return 'OK'


