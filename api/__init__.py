from flask import Flask
from flasgger import Swagger, LazyString, LazyJSONEncoder


from config import SWAGGERUI_BLUEPRINT, SWAGGER_URL
# Routes
from .routes import Auth, Users

app = Flask(__name__)


def init_app(config):
    # Configuration
    app.config.from_object(config)
    app.json_encoder = LazyJSONEncoder

    # Swagger
    app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)

    # Blueprints
    app.register_blueprint(Auth.auth, url_prefix='/auth')
    app.register_blueprint(Users.users, url_prefix='/users')

    return app
