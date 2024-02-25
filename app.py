import requests
import os
from flask import Flask, jsonify

from api import init_app
from config import config

configuration = config['development']
app = init_app(configuration)

if __name__ == "__main__":
    app.run(port=8080)
