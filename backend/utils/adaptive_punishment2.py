import os
import json
from backend.utils.user_tracker import get_offenses, update_offense
from backend.utils.moderation import check_token_permissions, get_user_id, timeout_user_via_api, ban_user_via_api
from backend import config

def load_offenses():
    if not os.path.exists(config.OFFENSES_FILE):
        return {}
    with open(config.OFFENSES_FILE, "r") as f:
        return json.load(f)


def adaptive_punishment(username, toxicity_labels, access_token, client_id, moderator_id, broadcaster_id):
    offense_data = get_offenses(username)
    offense_count = offense_data["count"]

    print(f"[Punishment] {username} offense count: {offense_count + 1}")

    user_id = get_user_id(username, access_token, client_id)
    if not user_id:
        print(f"[ModBot] Failed to retrieve user_id for {username}")
        return

    # Punishment logic
    if offense_count == 0:
        timeout_user_via_api(user_id, moderator_id, broadcaster_id, 30, "Toxicity detected - 1st offense", access_token, client_id)
    elif offense_count == 1:
        timeout_user_via_api(user_id, moderator_id, broadcaster_id, 300, "Toxicity detected - 2nd offense", access_token, client_id)
    elif offense_count == 2:
        timeout_user_via_api(user_id, moderator_id, broadcaster_id, 900, "Toxicity detected - 3rd offense", access_token, client_id)
    else:
        ban_user_via_api(user_id, moderator_id, broadcaster_id, "Repeated toxic behavior", access_token, client_id)

    # Update offense tracker
    update_offense(username)
