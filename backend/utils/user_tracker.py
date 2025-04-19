# modbot/backend/bot/user_tracker.py

import json
import os
import time
from collections import defaultdict

from config import OFFENSES_FILE


# Load existing offenses if file exists
if os.path.exists(OFFENSES_FILE):
    with open(OFFENSES_FILE, "r") as f:
        user_offenses = defaultdict(
            lambda: {"count": 0, "last_offense": 0},
            json.load(f)
        )
else:
    user_offenses = defaultdict(lambda: {"count": 0, "last_offense": 0})

def save_offenses():
    with open(OFFENSES_FILE, "w") as f:
        json.dump(user_offenses, f, indent=4)

def get_offenses(username):
    return user_offenses[username]

def update_offense(username):
    user_offenses[username]["count"] += 1
    user_offenses[username]["last_offense"] = time.time()
    save_offenses()

def reset_offenses(username):
    if username in user_offenses:
        user_offenses[username] = {"count": 0, "last_offense": 0}
        save_offenses()

def get_all_offenses():
    return dict(user_offenses)
