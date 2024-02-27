from decouple import config
from flask_swagger_ui import get_swaggerui_blueprint

### swagger specific ###
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Seans-Python-Flask-REST-Boilerplate"
    }
)


class DevelopmentConfig:
    SECRET_KEY = config('SECRET_KEY')
    HOST = 'localhost',
    DEBUG = True


my_config = {
    'development': DevelopmentConfig
}
