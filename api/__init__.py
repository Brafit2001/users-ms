from flasgger import LazyJSONEncoder
from flask import Flask
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials

from config import SWAGGERUI_BLUEPRINT, SWAGGER_URL


# Routes


def init_app(config):
    app = Flask(__name__)
    CORS(app)
    app.config['CORS_HEADERS'] = 'Content-Type'

    # Configuration
    app.config.from_object(config)
    app.json_encoder = LazyJSONEncoder

    cred = credentials.Certificate({
          "type": "service_account",
          "project_id": "clipclass-4942b",
          "private_key_id": "a01f8de3534e9ee82b647b31bc506a6ea38cbdb0",
          "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDG20hH4enXjZYp\nBA3yXRvwRNl2WL0bYXNjdmvnTHFVcGWzaUm11l3FHoyxd44I478xZKn5iYkU/psg\npBWzSHtymavh7zDRuWcxx6BBcyMV2oL7JvBxVn+LhfUtiQikwRXDEl61tCJkLir7\na0PevJ0X7A60lewAQGB/YlNKDUkzUN74rq1pe2hsJBfuuna06JiV5CKmgOOz2P4K\n/lk+oicPWKS8CGwLKMhYJK7R7TKC0gyyHvHMJQSryzLF/PF4skJO2a510NBeMkgg\nv9wUyblb8RIMXvlO4ZTkX4hTjsrjq6+cpOx/e7B3ACB17CJxrClaDVVlk8V04KIK\nNjv9dhAxAgMBAAECggEABT0KbbJWQs3T5LBtFQ6rtwdW/zId0THVki/nt37X4Xa8\nq7DTW0Q3GrpiS0nyizNoHvjWUgU9Ejk6O4Cbok62XBZYiYVGjGIWqfvCH7KwV35S\nQv8wCFMo3UWh+j3SCcGc9CWVTyBcY5HI7F3BKGFgdgom5imEUZzOQD8YauGxSdFy\nZCrn5IJ4CM2E9ddSG7goSpHzdOYpDSjytiJWBVjlrwyUpO6dpC2C7wZ7YAplpCJ9\n7DS07bED+C5FsoWYlJhItLGNXqDHv1PNWrVFdVRgYVEcceYyBEtUQNT4XsgAFLf7\nzpzTTKLOt2D8+ILp1rF6BY0MZWHEtQdl3KGD9iGe3QKBgQDioaEezmlGbXCNhkaX\nWyvYi2p7Ud4PGZ1XUgCjlHluiTA+WSujAXRV3A6zmuPOj2vlsxvbbF4q6CaSMQFp\nJa7MDuRYMniEq8CmGMY9xVw9LLpC1JE1y8yly65bb76sK7IhK406xi1I9ZIVZa0o\n/+iSFvnoxjpdJ5an981HuvtW4wKBgQDgoD1RAba7IYd+TSB7O32UfHKd57Rw7hOX\nb/Gs+/BOG3CIOX7LdlTPMBp0hImo+MfycV88ZxJ2MeMtrAdhRr9QJPmV3vTOQT5f\nzNLDx3SadV0k5yCql2inY2oubkaIp9LXE1jzqZ1jDPcyDSYzm8Qez0x/+9UP7yKH\nUVpl6wMU2wKBgQCYLd5KGGJ6pyxH7B1krxTfIKbMzillTFbp9qd1MFLmFXrusuPp\nXiWnLdA1bFGCN65FHKMdEUSeXSrhScTfvS0F2w4b5zAkLkx7e/FKM0d/0JP2IlSr\nogD2Z7HZtkx7wg+n1F3OVJq9/iAs/AxtloGt7326f7lbKiUw/uW6P+Vb7wKBgQCm\nmHGhiOHbvCxfkhhLDX5ACGSBlH2RXCGPqWjW4SwC4fr+LZZKlIKl/4k/baUjew/g\nUhFOHSvmGW3iS7pVfUEa0bGCZA+wgVcfeiu/JEjo3a6tVfY2T4FA1EzGDuelJsMK\n3MCWRvABrHYR2wrAMACu0RRtv3rwDG3RapbfDAQHDQKBgQC95TxXGJmJieJS0quG\nM4i8etGNSICyjUaVPfkO3DmfebOYDXNboLsC0J3CcS5dNPqvs3bkigB1vDLKDROT\npJv72rzMtpwwb5ERJSGZywerVcmWT/NLgSKkk1hKHuZ2ubcd7PL/hyFlM59WSFJp\nmKcTwvRCJ0qA9VxeTRePcAfYXA==\n-----END PRIVATE KEY-----\n",
          "client_email": "firebase-adminsdk-ugorn@clipclass-4942b.iam.gserviceaccount.com",
          "client_id": "103514239741805976827",
          "auth_uri": "https://accounts.google.com/o/oauth2/auth",
          "token_uri": "https://oauth2.googleapis.com/token",
          "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
          "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-ugorn%40clipclass-4942b.iam.gserviceaccount.com",
          "universe_domain": "googleapis.com"
        }
    )
    firebase_admin.initialize_app(cred, {'storageBucket': 'clipclass-4942b.appspot.com'})

    # Swagger
    # app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)

    # ----- BLUEPRINTS --------
    from api.routes import Auth, Users, Health, Roles, Instagram
    app.register_blueprint(Auth.auth, url_prefix='/auth')
    app.register_blueprint(Instagram.instagram, url_prefix='/instagram')
    app.register_blueprint(Users.users, url_prefix='/users')
    app.register_blueprint(Roles.roles, url_prefix='/roles')
    app.register_blueprint(Health.health, url_prefix='/health')
    return app
