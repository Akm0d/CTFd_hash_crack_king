from CTFd import utils
from CTFd.models import db, Challenges, WrongKeys, Keys, Teams, Awards
from CTFd.plugins.challenges import get_chal_class
from CTFd.plugins.keys import get_key_class, KEY_CLASSES
from CTFd.plugins import challenges, register_plugin_assets_directory
from CTFd.plugins.keys import BaseKey

from flask import request, redirect, jsonify, url_for, session, abort
from flask_restful import Resource, Api
from passlib.handlers.md5_crypt import md5_crypt
from random import random
from six import unichr

import logging
import string

WORDS = ["TODO", "implement", "This"]


def generate_hash(difficulty, count):
    # TODO Have a settings page where these parameters can be modified by an admin
    password = ""
    # The difficulty increases by the count value
    # increase length and dictionary following with difficulty
    if difficulty < (1 + count * 0):
        password = random.choice(WORDS)
    elif difficulty < (1 + count * 1):
        password = random.choice(WORDS)
        password += str(random.randint(10000, 20000))
        password = password[:8]
    elif difficulty < (1 + count * 2):
        chars = string.digits
        password = ''.join(random.choice(chars) for _ in range(8))
    elif difficulty < (1 + count * 3):
        chars = string.ascii_uppercase
        password = ''.join(random.choice(chars) for _ in range(8))
    elif difficulty < (1 + count * 4):
        chars = string.ascii_uppercase + string.digits
        password = ''.join(random.choice(chars) for _ in range(8))
    elif difficulty < (1 + count * 5):
        chars = string.ascii_uppercase + string.digits + string.ascii_uppercase.lower()
        password = ''.join(random.choice(chars) for _ in range(8))
    elif difficulty < (1 + count * 6):
        chars = string.ascii_uppercase + string.digits + string.ascii_uppercase.lower() \
                + "`~!@#$%^&*()_+=-\|]}[{'\";:.>,</?"
        password = ''.join(random.choice(chars) for _ in range(8))
    elif difficulty < (1 + count * 7):
        chars = string.ascii_uppercase + string.digits + string.ascii_uppercase.lower() \
                + "`~!@#$%^&*()_+=-\|]}[{'\";:.>,</?"
        password = ''.join(random.choice(chars) for _ in range(10))
    elif difficulty < (1 + count * 8):
        chars = ""
        for i in range(0, 0x7F):
            chars += str(unichr(i))
        password = ''.join(random.choice(chars) for _ in range(10))
    elif difficulty < (1 + count * 9):
        chars = ""
        for i in range(0, 0x7F):
            chars += str(unichr(i))
        password = ''.join(random.choice(chars) for _ in range(10))
    else:
        chars = ""
        for i in range(0, 0x7F):
            chars += str(unichr(i))
        password = ''.join(random.choice(chars) for _ in range(16))
    # Don't allow a password longer than 8 characters
    pass_hash = md5_crypt.encrypt(password, salt="salty")
    # passwd.write(user + ':x:' + str(uid) + ':1000:Test User,,,:/home:/usr/bin/zsh\n')
    # shadow.write(user + ':' + pass_hash + ':17080:0:99999:7:::\n')
    return pass_hash, password


def load(app):
    """load overrides for multianswer plugin to work properly"""
    api = Api(app)
    register_plugin_assets_directory(app, base_path='/plugins/hash_crack_king/assets/')
