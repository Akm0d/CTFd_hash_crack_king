#!/usr/bin/env python3
import os

from passlib.hash import md5_crypt
from os.path import expanduser
import string
import random


home = expanduser("~")
# Globals
WORD_FILE = "/usr/share/dict/words"
if os.name == 'nt': WORD_FILE = home + '\\AppData\\Roaming\\Microsoft\\Spelling\\en-US\\default.dic'
WORDS = open(WORD_FILE).read().splitlines()


def generate_hash(difficulty, count):
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
    print(password)
    return pass_hash, password


if __name__ == "__main__":
    import argparse
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--count', help='Number of passwords in each difficulty level', type=int, default=5)
    parser.add_argument('--difficulty', help='The difficulty of the hash', type=int, default=0)
    parser.add_argument('-d', '--debug', help='Enable debugging mode', action="store_true")
    parser.add_argument('-v', '--verbose', help='Enable verbose mode', action="store_true")
    args = parser.parse_args()
    print(generate_hash(args.difficulty, args.count))
