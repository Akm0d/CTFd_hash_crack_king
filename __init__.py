from CTFd import utils
from CTFd.models import db, Challenges, WrongKeys, Keys, Teams, Awards
from CTFd.plugins.challenges import get_chal_class
from CTFd.plugins.keys import get_key_class, KEY_CLASSES
from CTFd.plugins import challenges, register_plugin_assets_directory
from CTFd.plugins.keys import BaseKey
from flask import request, redirect, jsonify, url_for, session, abort
from flask_restful import Resource, Api

import logging
import time


def hints_view():
    pass


def load(app):
    """load overrides for multianswer plugin to work properly"""
    api = Api(app)
    register_plugin_assets_directory(app, base_path='/plugins/restful_api/assets/')
