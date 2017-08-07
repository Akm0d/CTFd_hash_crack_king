#!/usr/bin/env python3
# coding=utf-8
import sys

sys.path.append('local_functions')
from local_functions.generate_hash import *
from local_functions.cow_fortune import *
from local_functions.message_extension import *
from passlib.hash import md5_crypt
from flask_recaptcha import ReCaptcha
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import request
from hashlib import md5
from pickle import dump, load
from re import compile
import argparse
import hashlib
import random
import flask
import json
import sched
import socket
import time
import threading
import os

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--host', help='The host name or ip address to run on', type=str, default='0.0.0.0')
parser.add_argument('--port', help='The port number the web server will use', type=int, default=5000)
parser.add_argument('--cert', help='The SSL certificate', type=str)
parser.add_argument('--key', help='The SSL private key', type=str)
parser.add_argument('-d', '--debug', help='Enable debugging mode', action="store_true")
parser.add_argument('-v', '--verbose', help='Enable verbose mode', action="store_true")
args = parser.parse_args()

# Scoring
new_king_points = 30
king_keep_points = 1
# Minutes between delay
score_delay = 5

# Global variables
SCORING_SERVER = socket.gethostbyname('ictf.openwest.org')
SECURE = bool(args.key) and bool(args.cert)
TEAM_NAME = "team"
TEAM_MD5 = "check"
SCORING_TEAM = None  # The team that is currently scoring point
INSULTS = open('static/insults.txt', 'r').read().split('\n')
FILE_DIRECTORY = "files"
pickle_file = "webserver.state"
SUPPORTED_ERROR_CODES = {428, 429, 400, 401, 403, 404, 405, 406, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418,
                         422, 431, 500, 501, 502, 503, 504, 505}
# Variables that are used with password_hash and password_cracking
current_difficulty = 0
count = 5
current_hash, current_pass = generate_hash(current_difficulty, count)
if args.debug: print("Password: %s" % current_pass)
scoring_team_pass_crack = None

# ReCaptcha
RECAPTCHA_PUBLIC_KEY = 'TODO: GET THIS FROM CONFIG'
RECAPTCHA_PRIVATE_KEY = 'TODO: GET THIS FROM CONFIG'
RECAPTCHA_REDIRECT = '/rules'

# App variables
app = flask.Flask(__name__)
recaptcha = ReCaptcha(app=app, site_key=RECAPTCHA_PUBLIC_KEY, secret_key=RECAPTCHA_PRIVATE_KEY,
                      is_enabled=True, theme='dark', type='image')
limiter = Limiter(app=app, key_func=get_remote_address, global_limits=["5/second"],
                  strategy='fixed-window-elastic-expiry')

AGREED = 'AGREED'
DISAGREED = 'DISAGRED'

# This gets incremented every time a team is created
team_index = 0


class Team:
    team_id = None
    index = None
    team_name = None
    agreed = None
    password_crack_points = 0
    regex_length = None

    def __init__(self, team_name):
        global team_index
        self.index = team_index
        team_index += 1
        self.team_name = team_name
        # Create an id for each team based on their name and it's md5sum
        m = md5()
        m.update(self.team_name.encode())
        self.team_id = str(self.team_name).replace(" ", "_").lower() + "-" + m.hexdigest()
        self.team_id = self.team_id[:36]
        if args.debug: print(self.team_id)
        # Mark as AGREED or DISAGREED once we know if they accepted terms and conditions
        self.agreed = 'NONE'
        pass

# Save certain information about teams in a pickle state so that it is preserved across script runs
team_information = dict()
try:
    with open(pickle_file, 'rb') as read_state:
        team_information = load(read_state)
except Exception:
    pass

def update_score():
    # Update password cracking score every five minutes
    if team_information.get(scoring_team_pass_crack, None) is not None:
        if args.debug: print("Adding %s points to %s" % (str(king_keep_points), str(scoring_team_pass_crack)))
        team_information[scoring_team_pass_crack].password_crack_points += king_keep_points
        with open(pickle_file, 'wb') as write_state:
            # Save the fact that they agreed
            dump(team_information, write_state)
    threading.Timer(score_delay * 60, update_score).start()


update_score()


def page_error(error):
    message = str(error)[3:]
    return flask.render_template('index.html', challenge_name=str(error), text=random.choice(INSULTS),
                                 title="ICTF" + message, code=666)


for code in SUPPORTED_ERROR_CODES:
    app.register_error_handler(code, page_error)


@app.route('/favicon.ico')
def favicon():
    return flask.send_from_directory(os.path.join(app.root_path, 'static'),
                                     'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route("/")
def index():
    return flask.redirect("/password_cracking", code=302)


def get_password_crack_scoreboard():
    builder = ""
    for team in sorted(team_information.keys()):
        builder += team + ": %s\n" % str(team_information[team].password_crack_points)
    return builder


# TODO use pickle to store the state of the password cracking challenge
# If FBCTF doesn't get this working, then keep a tally on your own and add it after the competition is over
@app.route("/password_cracking")
@limiter.limit("1/second")
def password_hash_hash():
    challenge_name = "King of the Hill"
    # Do this when they make the scoring server explicitly requests json
    # if request.headers['Content-Type'] == 'application/json':
    if request.remote_addr == SCORING_SERVER:
        global scoring_team_pass_crack
        team_md5 = hashlib.md5(str(scoring_team_pass_crack).encode('utf-8')).hexdigest()
        team_json = {TEAM_NAME: str(scoring_team_pass_crack), TEAM_MD5: team_md5}
        return json.dumps(team_json)
    else:
        return flask.render_template('password_hash.html',
                                     challenge_name=challenge_name + ": " + str(scoring_team_pass_crack),
                                     password_hash=current_hash,
                                     title="ICTF:" + challenge_name, text=get_password_crack_scoreboard())


@app.route("/password_cracking/guess", methods=['POST', 'GET'])
@limiter.limit("1/second")
def password_cracking_guess():
    challenge_name = "King of the Hill"
    global current_hash
    global current_difficulty
    global scoring_team_pass_crack

    # If they didn't come in with a valid recaptcha, then redirect
    if not recaptcha.verify() and not args.debug:
        return flask.redirect(RECAPTCHA_REDIRECT, code=302)

    if flask.request.method == 'POST':
        result = flask.request.form
        password = result.get("password")
        team_name = result.get("team_name")
        if password and team_name:
            if args.debug: print("password_cracking: Team \"%s\" guessed \"%s\"" % (team_name, password))
            # Check if the password was correct
            status = "INCORRECT!"
            if md5_crypt.verify(password, current_hash):
                status = "CORRECT!"
                # Save their team name in another file
                if team_information.get(team_name, None) is not None:
                    if scoring_team_pass_crack != team_name:
                        team_information[team_name].password_crack_points += new_king_points
                        scoring_team_pass_crack = team_name
                else:
                    return flask.render_template("index.html",
                                                 challenge_name=challenge_name + ": " + str(scoring_team_pass_crack),
                                                 text="No such team: '%s'" % team_name,
                                                 title="ICTF:" + challenge_name)

                with open(pickle_file, 'wb') as write_state:
                    # Save the fact that they agreed
                    dump(team_information, write_state)
                # Generate more difficult hash
                current_difficulty += 1
                current_hash, current_pass = generate_hash(current_difficulty, count)
                if args.debug: print("Password: %s" % current_pass)
            if status == "CORRECT!":
                return flask.render_template("index.html",
                                             challenge_name=challenge_name + ": " + str(scoring_team_pass_crack),
                                             text=status,
                                             title="ICTF:" + challenge_name)
        return flask.render_template("index.html", challenge_name=challenge_name + ": " + str(scoring_team_pass_crack),
                                     text=random.choice(INSULTS),
                                     title="ICTF:" + challenge_name)
    elif flask.request.method == 'GET':
        return flask.redirect("/password_cracking", code=302)


@app.route("/cow_secrets")
def cow_fortune():
    challenge_name = "Cow Secrets"
    hint = "Your browser is not supported.\nTry upgrading from EPOC 5"
    response = check_user_agent(str(flask.request.user_agent), "Symbian", hint)
    if not "pass" in response:
        return flask.render_template("index.html", text=response, challenge_name=challenge_name,
                                     title="ICTF:" + challenge_name)
    if not flask.request.cookies.get("oatmeal",None):
        return flask.render_template("index.html", text=no_cookie_response("oatmeal cookie Please!"),
                                     challenge_name=challenge_name, title="ICTF:" + challenge_name)
    response = check_cooke_value(flask.request.cookies, "Raisins")
    if not "pass" in response:
        return flask.render_template("index.html", text=response, challenge_name=challenge_name,
                                     title="ICTF:" + challenge_name)
    text, cow, riddle, question = get_fortune()
    cow = cow.replace('/', '')
    if args.debug: print("Type: " + cow_type)
    if riddle == "riddle":
        return flask.render_template("cow_riddle.html", challenge_name=challenge_name, text=text, riddler=cow,
                                     question=question)
    else:
        return flask.render_template("index.html", text=text, challenge_name=challenge_name,
                                     title="ICTF:" + challenge_name)


@app.route("/cow_secrets/guess", methods=['POST', 'GET'])
def cow_fortune_guess():
    challenge_name = "Cow Secrets"
    # If they didn't come in with a valid recaptcha, then redirect
    if not recaptcha.verify() and not args.debug:
        return flask.redirect(RECAPTCHA_REDIRECT, code=302)
    if flask.request.method == 'POST':
        result = flask.request.form
        riddler = result.get("riddler")
        question = result.get("question")
        answer = result.get("answer")
        if riddler and question and answer:
            if args.debug: print("cow_fortune: riddler=%s,question=%s,answer=%s" % (riddler, question, answer))
        return flask.render_template("index.html", text=check_answer(riddler, question, answer),
                                     challenge_name=challenge_name, title="ICTF:" + challenge_name)
    if flask.request.method == 'GET':
        return flask.redirect("/cow_secrets", code=302)


@app.route("/message_extension")
def message_extension():
    challenge_name = "Message Extension"
    text = "This challenge has not yet been implemented"
    return flask.render_template('mac.html', challenge_name=challenge_name, title="ICTF:" + challenge_name)


original_message = "Every team fails this challenge"
original_digest = '0ef645a89daaea2fc39cba15ab1d7ce1edaeb12a'
flag = "flag{Merkle_Damigard-Con4truct1oN5}"
key_length = 128 / 8
answer = mac(message=original_message, mac=original_digest, key_length=key_length)
answer_message, answer_digest = answer.mac_attack("Thing")


# Give them the hint that the full extended message must be decoded using cp437
@app.route("/message_extension/guess", methods=['POST', 'GET'])
def message_extension_guess():
    challenge_name = "Message Extension"
    # If they didn't come in with a valid recaptcha, then redirect
    if not recaptcha.verify() and not args.debug:
        return flask.redirect(RECAPTCHA_REDIRECT, code=302)
    if flask.request.method == 'POST':
        result = flask.request.form
        extension = result.get("extension")
        message = result.get("message")
        digest = result.get("digest")
        # Don't let them do an empty submission
        if extension and message and digest:
            if answer.check_extension(extension, message, digest):
                return flask.render_template("index.html", text=flag, challenge_name=challenge_name,
                                             title="ICTF:" + challenge_name)
        return flask.render_template("index.html", challenge_name=challenge_name, text=random.choice(INSULTS),
                                     title="ICTF:" + challenge_name)
    elif flask.request.method == 'GET':
        return flask.redirect("/message_extension", code=302)


def get_regex_scoreboard():
    builder = "Shortest solution for each team"
    builder += "\n" + "-" * 80 + "\n"
    for team in sorted(team_information.keys()):
        builder += team + ": %s\n" % str(len(team_information[team].regex_length)if team_information[team].regex_length else None)
    builder += "-" * 80
    return builder


positive_list = [
    "end the party. And go on",
    "lots of music. What can",
    "when will it? why is there",
    "sold the item.\" After it did",
    "the burrito!'  She screamed",
    "thought so.) Then"
]
negative_list = [
    "in the U.S.A., we always",
    "Sally?\", they inquired, but",
    "but 9.8 meters/second was",
    "well ... if they could then",
    "A.I. has changed so",
    "like that\", he thought",
    "but G.I. Roku burrito"
]


@app.route("/regular_expressions")
def regular_expressions():
    challenge_name = "Regular Expressions"
    # https://callumacrae.github.io/regex-tuesday/challenge1.html
    # https://regex.sketchengine.co.uk
    text = get_regex_scoreboard()
    text += "\nWrite a regular expression that matches every line in 'positive', but none of the lines in the 'negative'"
    return flask.render_template('regex.html', challenge_name=challenge_name, text=text, title="ICTF:" + challenge_name,
                                 positive="\n".join(positive_list), negative="\n".join(negative_list))


@app.route("/regular_expressions/submit", methods=['POST'])
def regular_expressions_submit():
    # If they didn't come in with a valid recaptcha, then redirect
    if not recaptcha.verify() and not args.debug:
        return flask.redirect(RECAPTCHA_REDIRECT, code=302)

    challenge_name = "Regular Expressions"

    result = flask.request.form
    regex_text = result.get('regex')
    regex = compile(regex_text)
    team = result.get("team_name")
    text = ""

    for item in positive_list:
        if not regex.match(item):
            text += "Failed to match '%s'\n" % item

    for item in negative_list:
        if regex.match(item):
            text += "Shouldn't have matched '%s'\n" % item

    if not text:
        if team not in team_information.keys():
            text += "Team '%s' not recognised"
        else:
            if team_information[team].regex_length is None or len(regex_text) < team_information[team].regex_length:
                team_information[team].regex_length = regex_text
                with open(pickle_file, 'wb') as write_state:
                    # Save the fact that they agreed
                    dump(team_information, write_state)
        text += "\nflag{xKcD::/208/}\n"

    return flask.render_template('index.html', challenge_name=challenge_name, text=text, title="ICTF:" + challenge_name)


if __name__ == "__main__":
    # Display basic info based on command line arguments
    if args.verbose: print("Verbose mode activated")
    if args.debug: print("Debug mode activated")
    if bool(args.cert) != bool(args.key):
        print("ERROR! --cert and --key must be used together")
        exit(1)
    if args.verbose or args.debug:
        if SECURE:
            print("Using HTTPS on port %d" % args.port)
        else:
            print("Using HTTP on port %d" % args.port)
    if SECURE:
        try:
            context = (args.cert, args.key)
            if args.debug:
                app.run(port=args.port, debug=True, ssl_context=context, host=args.host)
            else:
                app.run(port=args.port, debug=False, ssl_context=context, host=args.host)
        except Exception as e:
            if args.debug:
                print(e)
                exit(2)
            else:
                print("ERROR! Invalid certificate ,key, or host")
                print("Use --debug for more info")
                exit(2)
    else:
        app.run(port=args.port, debug=args.debug, host=args.host)
