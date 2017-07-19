#!/usr/bin/env python3
import random
import re
import os

RIDDLE_FILE = "/usr/share/games/fortunes/riddles"
if os.name == 'nt':
    RIDDLE_FILE = 'C:\\Users\\Tyler Johnson\\AppData\\Roaming\\Microsoft\\Spelling\\en-US\\default.dic'
RIDDLES = "".join(open(RIDDLE_FILE).read().split())
INSULTS = open('static/insults.txt', 'r').read().split('\n')

debug = False

cows = [
    "apt", "beavis.zen", "bong", "bud-frogs", "bunny", "calvin", "cheese", "cock", "cower", "daemon", "default",
    "dragon", "dragon-and-cow", "duck", "elephant", "elephant-in-snake", "eyes", "flaming-sheep",
    "ghostbusters", "gnu", "hellokitty", "kiss", "kitty", "koala", "kosh", "luke-koala", "mech-and-cow",
    "meow", "milk", "moofasa", "moose", "pony", "pony-smaller", "ren", "sheep", "skeleton", "snowman",
    "stegosaurus", "stimpy", "suse", "three-eyes", "turkey", "turtle", "tux", "unipony",
    "unipony-smaller", "vader", "vader-koala", "www"
]


def cowsay(text, options):
    if os.name == 'nt': return text
    text = text.replace("\\", "")
    text = text.replace('"', '\\"')
    command = "echo \"" + text + "\" |cowsay " + options + " -n"
    text = os.popen(command).read()
    return text


def fortune():
    if os.name == 'nt':
        return "Q:Why?\nA:Because I can"
    else:
        return os.popen("fortune").read()


def check_user_agent(given, expected, hint):
    # Make sure they tweaked their user agent
    if not expected.upper() in given.upper():
        text = cowsay(hint, "-d")
        return text
    else:
        return "pass"


def no_cookie_response(hint):
    return cowsay(hint, "")


def check_cooke_value(cookie_data, expected):
    cookie = str(cookie_data)
    if expected.upper() in cookie.upper():
        return "pass"
    else:
        return cowsay("There aren't any " + expected.lower() + " in this cookie", "")


def check_answer(riddler, question, answer):
    answer = "".join(answer.split())
    # Make sure they respond with a valid cow
    riddler = riddler.replace('/', '')
    riddler = riddler.replace('=', '')
    riddler = "".join(riddler.split())
    question = question.replace('/', '')
    question = question.replace('=', '')
    question = "".join(question.split())
    if not riddler in cows:
        text = cowsay("That's not who asked you the question.\nTry again\"", "-e \"vv\"")
        return text
    else:
        # It's correct if fortune can find their answers
        submission = "Q:" + question + "A:" + answer + "%"
        if debug: print("cow_fortune:check_answer: " + submission)
        if submission in RIDDLES:
            # It's incorrect if they were too broad
            text = cowsay("flag{THere_!s_Nx_coW_leVEL}\"", "-f " + riddler)
            return text

        text = cowsay(random.choice(INSULTS), "-f " + riddler)
        return text


def get_fortune():
    my_fortune = fortune()
    # Check for a riddle in the fortune
    match = re.search("Q:\s*(.+)\n+A:(.+)", my_fortune)
    match2 = re.search("Q:\s*(.+)\n+A:(.+)\n+Q:(.+)\n+A:(.+)", my_fortune)
    if match and not match2:
        if debug: print("it's a riddle!")
        cow = random.choice(cows)
        # text = "Solve " + cow + "'s riddle for the flag.\n\n"
        question = match.group(1)
        text = cowsay(question, "-f " + cow)
        question = question.replace('/', '')
        question = question.replace('=', '')
        question = "".join(question.split())
        if debug: print("Question: " + question)

        # The answer to the riddle, for testing
        if debug: print("Answer: " + match.group(2))
        return text, cow, "riddle", question
    while "Q:" in my_fortune:
        my_fortune = fortune()
    cow = random.choice(cows)
    text = cowsay(my_fortune, "-f " + cow)
    return text, "cow", "fortune", "None"


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', help='Enable debugging mode', action="store_true")
    args = parser.parse_args()
    debug = args.debug

    print(get_fortune())
    exit(0)
