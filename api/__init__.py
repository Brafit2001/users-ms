from flask import Flask

# Routes
from .routes import Auth, Users

app = Flask(__name__)


def init_app(config):
    # Configuration
    app.config.from_object(config)

    # Blueprints
    app.register_blueprint(Auth.auth, url_prefix='/auth')
    app.register_blueprint(Users.users, url_prefix='/users')

    return app
