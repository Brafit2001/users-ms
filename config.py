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
    HOST = 'localhost',
    DEBUG = True


config = {
    'development': DevelopmentConfig
}
