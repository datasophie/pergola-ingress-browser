"""Setup at app startup"""
import os
from flask import Flask
from kubernetes import config

config.load_config()

app = Flask(__name__)

# To prevent from using a blueprint, we use a cyclic import
# This also means that we need to place this import here
# pylint: disable=cyclic-import, wrong-import-position
from app import routes
