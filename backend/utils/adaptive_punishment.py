import time
from backend.utils.ban_user import ban_user
from backend.utils.timeout_user import timeout_user
from config import OFFENSES_FILE
import json
import os
from backend.utils.user_tracker import get_offenses, update_offense

def load_offenses():
    if not os.path.exists(OFFENSES_FILE):
        return {}
    with open(OFFENSES_FILE, "r") as f:
        return json.load(f)


def adaptive_punishment(irc, channel, username, toxicity_labels):
    offense_data = get_offenses(username)
    offense_count = offense_data["count"]

    print(f"[Punishment] {username} offense count: {offense_count + 1}")
    
    # Apply punishment based on offense count *before* incrementing
    if offense_count == 0:
        timeout_user(irc, channel, username, 30, "Toxicity detected - 1st offense")
    elif offense_count == 1:
        timeout_user(irc, channel, username, 300, "Toxicity detected - 2nd offense")
    elif offense_count == 2:
        timeout_user(irc, channel, username, 900, "Toxicity detected - 3rd offense")
    else:
        ban_user(irc, channel, username, "Repeated toxic behavior")

    # Then update offense history
    update_offense(username)
