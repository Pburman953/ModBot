# modbot/backend/bot/user_tracker.py

import json
import os
import time
from collections import defaultdict

from backend import config

OFFENSE_RESET_HOURS = 24

# Load existing offenses if file exists
if os.path.exists(config.OFFENSES_FILE):
    with open(config.OFFENSES_FILE, "r") as f:
        user_offenses = defaultdict(
            lambda: {"count": 0, "last_offense": 0},
            json.load(f)
        )
else:
    user_offenses = defaultdict(lambda: {"count": 0, "last_offense": 0})

def save_offenses():
    with open(config.OFFENSES_FILE, "w") as f:
        json.dump(user_offenses, f, indent=4)

def get_offenses(username):
    offense = user_offenses[username]
    now = time.time()
    time_since_last = now - offense["last_offense"]

    # Auto-reset if it's been more than OFFENSE_RESET_HOURS
    if time_since_last > OFFENSE_RESET_HOURS * 36:
        user_offenses[username] = {"count": 0, "last_offense": 0}
        save_offenses()

    return user_offenses[username]

def update_offense(username, message, action):
    user_offenses[username]["count"] += 1
    user_offenses[username]["last_offense"] = time.time()
    user_offenses[username]["last_message"] = message
    user_offenses[username]["action_taken"] = action
    save_offenses()


def reset_offenses(username):
    if username in user_offenses:
        user_offenses[username] = {"count": 0, "last_offense": 0}
        save_offenses()

def get_all_offenses():
    if os.path.exists(config.OFFENSES_FILE):
        with open(config.OFFENSES_FILE, "r") as f:
            return json.load(f)
    else:
        return {}
