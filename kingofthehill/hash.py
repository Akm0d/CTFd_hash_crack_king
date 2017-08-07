from flask import Flask, render_template, send_from_directory, request, redirect

import socket
import os
import threading
import random
from pickle import dump, load
from passlib.hash import md5_crypt
from hashlib import md5
from flask import request
from flask_recaptcha import ReCaptcha
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import json


from kingofthehill.local_functions import generate_hash
from flask import current_app as app

# Scoring
new_king_points = 30
king_keep_points = 1
# Minutes between delay
score_delay = 1

# Global variables
SCORING_SERVER = socket.gethostbyname(socket.gethostname())
#SCORING_SERVER = '127.0.0.1'
#SECURE = bool(args.key) and bool(args.cert)
TEAM_NAME = "team"
TEAM_MD5 = "check"
SCORING_TEAM = None  # The team that is currently scoring point
INSULTS = os.path.join(app.root_path, app.config['INSULTS'])
INSULTS = open(INSULTS, 'r').read().split('\n')
FILE_DIRECTORY = "files"
pickle_file = "webserver.state"
scores_file = "scores.state"
SUPPORTED_ERROR_CODES = {428, 429, 400, 401, 403, 404, 405, 406, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418,
                         422, 431, 500, 501, 502, 503, 504, 505}
# Variables that are used with password_hash and password_cracking
current_difficulty = 0
count = 5
current_hash, current_pass = generate_hash.generate_hash(current_difficulty, count)
if app.debug: print('Password: "%s"\nHash: %s' % (current_pass, current_hash))
scoring_team_pass_crack = None

# ReCaptcha
RECAPTCHA_PUBLIC_KEY = app.config.get('RECAPTCHA_PUBLIC_KEY', None)
RECAPTCHA_PRIVATE_KEY = app.config.get('RECAPTCHA_PRIVATE_KEY', None)
USE_RECAPTCHA = True if (RECAPTCHA_PRIVATE_KEY is not None) and (RECAPTCHA_PUBLIC_KEY) is not None else False
RECAPTCHA_REDIRECT = '/rules'

# App variables
if USE_RECAPTCHA:
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
        if app.debug: print(self.team_id)
        # Mark as AGREED or DISAGREED once we know if they accepted terms and conditions
        self.agreed = 'NONE'
        pass

def addTeam(name):
    newTeam = Team(name)
    team_information[newTeam.team_name] = newTeam
    with open(pickle_file, 'wb') as write_state:
        # Save the fact that they agreed
        dump(team_information, write_state)
    print("Added new team: " + newTeam.team_name)


# Save certain information about teams in a pickle state so that it is preserved across script runs
team_information = dict()
try:
    with open(pickle_file, 'rb') as read_state:
        team_information = load(read_state)
except Exception:
    pass

# Save certain information about teams in a pickle state so that it is preserved across script runs
scores = dict()
print("tttttttt")
print(scores_file)
try:
    with open(scores_file, 'rb') as read_state:
        print('5555')
        scores = load(read_state)
        print("Scores: ")
        print(scores['scoring_team_pass_crack'])
        scoring_team_pass_crack = scores['scoring_team_pass_crack']

except Exception:
    pass

def update_score():
    # Update password cracking score every five minutes
    if team_information.get(scoring_team_pass_crack, None) is not None:
        #if app.debug: 
        print("Adding %s points to %s" % (str(king_keep_points), str(scoring_team_pass_crack)))
        team_information[scoring_team_pass_crack].password_crack_points += king_keep_points
        with open(pickle_file, 'wb') as write_state:
            # Save the fact that they agreed
            dump(team_information, write_state)
    threading.Timer(score_delay * 60, update_score).start()


update_score()


def page_error(error):
    message = str(error)[3:]
    return render_template('index.html', challenge_name=str(error), text=random.choice(INSULTS),
                                 title="ICTF" + message, code=666)


for code in SUPPORTED_ERROR_CODES:
    app.register_error_handler(code, page_error)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                                     'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route("/")
def index():
    return redirect("/password_cracking", code=302)


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
    print(SCORING_SERVER)
    if request.remote_addr == SCORING_SERVER:
        global scoring_team_pass_crack
        team_md5 = md5(str(scoring_team_pass_crack).encode('utf-8')).hexdigest()
        team_json = {TEAM_NAME: str(scoring_team_pass_crack), TEAM_MD5: team_md5}
        return json.dumps(team_json)
    else:
        return render_template('password_hash.html',
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
    if USE_RECAPTCHA:
        if not recaptcha.verify():
            return redirect(RECAPTCHA_REDIRECT, code=302)
    elif not app.debug:
        return redirect(RECAPTCHA_REDIRECT, code=302)

    if request.method == 'POST':
        result = request.form
        password = result.get("password")
        team_name = result.get("team_name")
        if password and team_name:
            if app.debug: print("password_cracking: Team \"%s\" guessed \"%s\"" % (team_name, password))
            # Check if the password was correct
            status = "INCORRECT!"
            if md5_crypt.verify(password, current_hash):
                status = "CORRECT!"
                # Save their team name in another file
                if team_information.get(team_name, None) is not None:
                    if scoring_team_pass_crack != team_name:
                        team_information[team_name].password_crack_points += new_king_points
                        scoring_team_pass_crack = team_name
                        scores['scoring_team_pass_crack'] = team_name
                        print(scores['scoring_team_pass_crack'])
                else:
                    addTeam(team_name)
                    if scoring_team_pass_crack != team_name:
                        team_information[team_name].password_crack_points += new_king_points
                        scoring_team_pass_crack = team_name
                        scores['scoring_team_pass_crack'] = team_name
                        print(scores['scoring_team_pass_crack'])

                with open(pickle_file, 'wb') as write_state:
                    # Save the fact that they agreed
                    dump(team_information, write_state)
                print("writing scores: " + scores['scoring_team_pass_crack'])
                with open(scores_file, 'wb') as write_state:
                    # Save the fact that they agreed
                    dump(scores, write_state)
                # Generate more difficult hash
                current_difficulty += 1
                current_hash, current_pass = generate_hash.generate_hash(current_difficulty, count)
                if app.debug: print("Password2: %s" % current_pass)
            if status == "CORRECT!":
                return render_template("index.html",
                                             challenge_name=challenge_name + ": " + str(scoring_team_pass_crack),
                                             text=status,
                                             title="ICTF:" + challenge_name)
        return render_template("index.html", challenge_name=challenge_name + ": " + str(scoring_team_pass_crack),
                                     text=random.choice(INSULTS),
                                     title="ICTF:" + challenge_name)
    elif request.method == 'GET':
        return redirect("/password_cracking", code=302)


