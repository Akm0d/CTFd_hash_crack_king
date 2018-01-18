from CTFd.plugins.keys import get_key_class
from CTFd.plugins import challenges, register_plugin_assets_directory
from flask import session
from CTFd.models import db, Challenges, WrongKeys, Keys, Awards, Solves, Files, Tags
from CTFd import utils
from passlib.handlers.md5_crypt import md5_crypt
from six import unichr

import logging
import random
import string

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

WORDS = ["TODO", "GET", "From", "Word", "lists"]


def generate_hash(difficulty: int, count: int):
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
    logger.debug("Hash: {}".format(pass_hash))
    logger.debug("Pass: {}".format(password))
    return pass_hash, password


class HashCrack(challenges.BaseChallenge):
    """hash-crack-king generates a new hash and flag every time it is solved"""
    id = "hash_crack_king"
    name = "hash_crack_king"

    hold = 0
    cycles = 1

    templates = {  # Handlebars templates used for each aspect of challenge editing & viewing
        'create': '/plugins/CTFd-hash_crack_king/assets/hashcrackking-challenge-create.njk',
        'update': '/plugins/CTFd-hash_crack_king/assets/hashcrackking-challenge-update.njk',
        'modal': '/plugins/CTFd-hash_crack_king/assets/hashcrackking-challenge-modal.njk',
    }
    scripts = {  # Scripts that are loaded when a template is loaded
        'create': '/plugins/CTFd-hash_crack_king/assets/hashcrackking-challenge-create.js',
        'update': '/plugins/CTFd-hash_crack_king/assets/hashcrackking-challenge-update.js',
        'modal': '/plugins/CTFd-hash_crack_king/assets/hashcrackking-challenge-modal.js',
    }

    @staticmethod
    def create(request):
        """
        This method is used to process the challenge creation request.

        :param request:
        :return:
        """
        # Create challenge
        chal = HashCrackKingChallenge(
            name=request.form['name'],
            description=request.form['description'],
            value=request.form['value'],
            category=request.form['category'],
            type=request.form['chaltype']
        )

        # self.cycles = int(request.form.get('cycles', 1)) if request.form.get('cycles', 1) else 1
        # self.hold = int(request.form.get('cycles', 0)) if request.form.get('hold', 0) else 0
        if 'hidden' in request.form:
            chal.hidden = True
        else:
            chal.hidden = False

        db.session.add(chal)
        db.session.commit()

        files = request.files.getlist('files[]')
        for f in files:
            # TODO Add these files to the word_lists
            # utils.upload_file(file=f, chalid=chal.id)
            pass

    @staticmethod
    def update(challenge, request):
        """
        This method is used to update the information associated with a challenge. This should be kept strictly to the
        Challenges table and any child tables.

        :param challenge:
        :param request:
        :return:
        """
        challenge.name = request.form['name']
        challenge.description = request.form['description']
        challenge.value = int(request.form.get('value', 0)) if request.form.get('value', 0) else 0
        # self.cycles = int(request.form.get('cycles', 1)) if request.form.get('cycles', 1) else 1
        # self.hold = int(request.form.get('cycles', 0)) if request.form.get('hold', 0) else 0
        challenge.category = request.form['category']
        challenge.hidden = 'hidden' in request.form
        db.session.commit()
        db.session.close()

    @staticmethod
    def read(challenge):
        """
        This method is in used to access the data of a challenge in a format processable by the front end.

        :param challenge:
        :return: Challenge object, data dictionary to be returned to the user
        """
        challenge = HashCrackKingChallenge.query.filter_by(id=challenge.id).first()
        data = {
            'id': challenge.id,
            'name': challenge.name,
            'value': challenge.value,
            'description': challenge.description.replace('[HASH]', "[TODO The actual hash]"),
            'category': challenge.category,
            'hidden': challenge.hidden,
            'max_attempts': challenge.max_attempts,
            'type': challenge.type,
            'type_data': {
                'id': HashCrack.id,
                'name': HashCrack.name,
                'templates': HashCrack.templates,
                'scripts': HashCrack.scripts,
            }
        }
        return challenge, data

    @staticmethod
    def delete(challenge):
        """
        This method is used to delete the resources used by a challenge.

        :param challenge:
        :return:
        """
        # Needs to remove awards data as well
        WrongKeys.query.filter_by(chalid=challenge.id).delete()
        Solves.query.filter_by(chalid=challenge.id).delete()
        Keys.query.filter_by(chal=challenge.id).delete()
        files = Files.query.filter_by(chal=challenge.id).all()
        for f in files:
            utils.delete_file(f.id)
        Files.query.filter_by(chal=challenge.id).delete()
        Tags.query.filter_by(chal=challenge.id).delete()
        Challenges.query.filter_by(id=challenge.id).delete()
        db.session.commit()

    @staticmethod
    def attempt(chal, request):
        """
        This method is used to check whether a given input is right or wrong. It does not make any changes and should
        return a boolean for correctness and a string to be shown to the user. It is also in charge of parsing the
        user's input from the request itself.

        :param chal: The Challenge object from the database
        :param request: The request the user submitted
        :return: (boolean, string)
        """
        provided_key = request.form['key'].strip()
        chal_keys = Keys.query.filter_by(chal=chal.id).all()
        for chal_key in chal_keys:
            if get_key_class(chal_key.type).compare(chal_key.flag, provided_key):
                if chal_key.type == "correct":
                    solves = Awards.query.filter_by(teamid=session['id'], name=chal.id,
                                                    description=request.form['key'].strip()).first()
                    try:
                        flag_value = solves.description
                    except AttributeError:
                        flag_value = ""
                    # Challenge not solved yet
                    if provided_key != flag_value or not solves:
                        solve = Awards(teamid=session['id'], name=chal.id, value=chal.value)
                        solve.description = provided_key
                        db.session.add(solve)
                        db.session.commit()
                        db.session.close()
                    return True, 'Correct'
                    # TODO Add description function call to the end of "Correct" in return
                elif chal_key.type == "wrong":
                    solves = Awards.query.filter_by(teamid=session['id'], name=chal.id,
                                                    description=request.form['key'].strip()).first()
                    try:
                        flag_value = solves.description
                    except AttributeError:
                        flag_value = ""
                    # Challenge not solved yet
                    if provided_key != flag_value or not solves:
                        wrong_value = 0
                        wrong_value -= chal.value
                        wrong = WrongKeys(teamid=session['id'], chalid=chal.id, ip=utils.get_ip(request),
                                          flag=provided_key)
                        solve = Awards(teamid=session['id'], name=chal.id, value=wrong_value)
                        solve.description = provided_key
                        db.session.add(wrong)
                        db.session.add(solve)
                        db.session.commit()
                        db.session.close()
                    return False, 'Error'
                    # TODO Add description function call to the end of "Error" in return
        return False, 'Incorrect'

    @staticmethod
    def solve(team, chal, request):
        """This method is not used"""

    @staticmethod
    def fail(team, chal, request):
        """This method is not used"""


class HashCrackKingChallenge(Challenges):
    __mapper_args__ = {'polymorphic_identity': 'hash_crack_king'}
    id = db.Column(None, db.ForeignKey('challenges.id'), primary_key=True)
    initial = db.Column(db.Integer)

    def __init__(self, name, description, value, category, type='hash_crack_king'):
        self.name = name
        self.description = description
        self.value = value
        self.initial = value
        self.category = category
        self.type = type


def load(app):
    """load overrides for hash_crack_king plugin to work properly"""
    app.db.create_all()
    register_plugin_assets_directory(app, base_path='/plugins/CTFd-hash_crack_king/assets/')
    challenges.CHALLENGE_CLASSES["hash_crack_king"] = HashCrack
