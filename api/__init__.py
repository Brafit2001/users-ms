from flasgger import LazyJSONEncoder
from flask import Flask

from config import SWAGGERUI_BLUEPRINT, SWAGGER_URL


# Routes


def init_app(config):
    app = Flask(__name__)
    # Configuration
    app.config.from_object(config)
    app.json_encoder = LazyJSONEncoder

    # Swagger
    # app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)

    # ----- BLUEPRINTS --------
    from api.routes import Auth, Users, Health, Roles
    app.register_blueprint(Auth.auth, url_prefix='/auth')
    app.register_blueprint(Users.users, url_prefix='/users')
    app.register_blueprint(Roles.roles, url_prefix='/roles')
    app.register_blueprint(Health.health, url_prefix='/health')
    return app
