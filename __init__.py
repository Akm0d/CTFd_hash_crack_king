from CTFd.plugins import challenges, register_plugin_assets_directory
from flask import session
from CTFd.models import db, Challenges, Keys, Awards, Solves, Files, Tags, Teams
from CTFd import utils
from passlib.handlers.md5_crypt import md5_crypt
from typing import List, Tuple

import logging
import random

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# TODO Create thread pool that decreases a counter when the game isn't paussed
# TODO if the CTF is paused, then hold timers should be paused
# TODO in the challenge description, replace [KING] with the team name of the team in control of the hill

def _team_name(session_id: int):
    """Return the team name for the given team id"""
    logger.debug("Getting team name for: {}".format(session_id))
    try:
        return Teams.query.filter_by(id=session_id).first().name
    except Exception:
        return None


def generate_key(key_length: int, character_set: str, word_list: List[str] or str = None) -> str:
    # TODO Have a settings page where these parameters can be modified by an admin
    key = ""
    words = set()

    # passwd.write(user + ':x:' + str(uid) + ':1000:Test User,,,:/home:/usr/bin/zsh\n')

    # Parse the word lists
    if isinstance(word_list, str):
        word_list = [word_list]
    if not word_list:
        word_list = list()
    for f in word_list:
        # TODO parse all the challenge's files for the one matching this string
        try:
            with open(f, "r") as word_file:
                words.union(set(x for x in word_file.readline().split()))
        except Exception:
            logger.error("Unable to read file '{}'".format(f))

    # Choose a random word from the word lists
    if words:
        key = random.choice(words)[:key_length]
    # TODO have a substitution table to translate e's to 3's and such?

    # TODO translate the character set from a regex-like pattern to a set of characters

    # Add characters to the string until it is the right size
    while len(key) < key_length:
        key += random.choice(character_set)

    logger.debug("Key is: '{}'".format(key))
    return key


def get_hash(key: str, salt: str = 'salt') -> str:
    """Return a unix shadow-like password hash"""
    # shadow.write(user + ':' + pass_hash + ':17080:0:99999:7:::\n')
    return md5_crypt.encrypt(key, salt=salt)


class HashCrackKingChallenge(Challenges):
    __mapper_args__ = {'polymorphic_identity': 'hash_crack_king'}
    id = db.Column(None, db.ForeignKey('challenges.id'), primary_key=True)
    initial = db.Column(db.Integer)
    # HAsh Crack King Challnege Values
    hold = db.Column(db.Integer)
    cycles = db.Column(db.Integer)
    current_hash = db.Column(db.String(80))
    king = db.Column(db.String(80))

    def __init__(self, name, description, value, category, hold, cycles, type='hash_crack_king',
                 current_hash: str = None):
        self.name = name
        self.description = description
        self.value = value
        self.initial = value
        self.category = category
        self.type = type
        # Hash Crack King Challenge Values
        self.hold = hold
        self.cycles = cycles
        self.king = None
        self.current_hash = current_hash


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
        files = [str(x) for x in request.files.getlist('files[]')]
        for f in files:
            # TODO Add these files to the word_lists
            # utils.upload_file(file=f, chalid=chal.id)
            pass

        # TODO generate first key based on level
        key = generate_key(key_length=3, character_set="01", word_list=files)

        # Create challenge
        chal = HashCrackKingChallenge(
            name=request.form['name'],
            description=request.form['description'],
            value=request.form['value'],
            category=request.form['category'],
            type=request.form['chaltype'],
            hold=request.form['hold'],
            cycles=request.form['cycles'],
            current_hash=get_hash(key)
        )

        if 'hidden' in request.form:
            chal.hidden = True
        else:
            chal.hidden = False

        db.session.add(chal)
        db.session.commit()

    @staticmethod
    def update(challenge: HashCrackKingChallenge, request):
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
        challenge.cycles = int(request.form.get('cycles', 0)) if request.form.get('cycles', 0) else 0
        challenge.hold = int(request.form.get('hold', 0)) if request.form.get('hold', 0) else 0
        challenge.category = request.form['category']
        challenge.hidden = 'hidden' in request.form

    @staticmethod
    def read(challenge: HashCrackKingChallenge):
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
            'description': challenge.description,  # .replace('[HASH]', "[TODO The actual hash]"),
            'category': challenge.category,
            'hidden': challenge.hidden,
            'cycles': challenge.cycles,
            'hold': challenge.hold,
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
    def delete(challenge: HashCrackKingChallenge):
        """
        This method is used to delete the resources used by a challenge.

        :param challenge:
        :return:
        """
        # Needs to remove awards data as well
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
    def attempt(chal: HashCrackKingChallenge, request) -> Tuple[bool, str]:
        """
        This method is used to check whether a given input is right or wrong. It does not make any changes and should
        return a boolean for correctness and a string to be shown to the user. It is also in charge of parsing the
        user's input from the request itself.

        :param chal: The Challenge object from the database
        :param request: The request the user submitted
        :return: (boolean, string)
        """
        provided_key = request.form['key'].strip()
        # Compare our hash with the hash of their provided key
        if chal.current_hash == get_hash(provided_key):
            solves = Awards.query.filter_by(teamid=session['id'], name=chal.id,
                                            description=request.form['key'].strip()).first()
            chal.king = session['id']
            king_name = _team_name(chal.king)
            # TODO generate new hash based on difficulty levels
            chal.current_hash = get_hash(generate_key(3, "01"))

            # Challenge not solved yet, give the team first capture points
            if not solves:
                solve = Awards(teamid=session['id'], name=chal.id, value=chal.value)
                solve.description = provided_key
                db.session.add(solve)
                db.session.commit()
                db.session.close()
                logger.debug('First capture, {} points awarded.  "{}" will receive {} points every {} seconds"'.format(
                    chal.value, king_name, chal.hold, chal.cycles))
            logger.debug(
                'Another capture", {}" is now King of the hill and will receive {} points every {} seconds'.format(
                    king_name, chal.hold, chal.cycles))
            return True, 'Correct, "{}" is now king of the hill!'.format(king_name)
        return False, 'Incorrect, "{}" remains the king'.format(_team_name(chal.king))

    @staticmethod
    def solve(team, chal: HashCrackKingChallenge, request):
        """This method is not used"""

    @staticmethod
    def fail(team, chal: HashCrackKingChallenge, request):
        """This method is not used"""


def load(app):
    """load overrides for hash_crack_king plugin to work properly"""
    app.db.create_all()
    register_plugin_assets_directory(app, base_path='/plugins/CTFd-hash_crack_king/assets/')
    challenges.CHALLENGE_CLASSES["hash_crack_king"] = HashCrack
