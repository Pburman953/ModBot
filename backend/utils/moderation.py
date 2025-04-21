import requests




def check_token_permissions(access_token):
    url = "https://id.twitch.tv/oauth2/validate"
    headers = {
        "Authorization": f"Bearer {access_token}"  # Ensure this is properly formatted
    }

    response = requests.get(url, headers=headers)  # Pass the headers dictionary
    if response.status_code == 200:
        print(f"Token is valid. Scopes: {response.json()['scopes']}")
        return response.json()
    else:
        print(f"Failed to validate token: {response.json()}")
        return None

    
def get_user_id(username, access_token, client_id):
    url = f"https://api.twitch.tv/helix/users?login={username}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Client-Id": client_id
    }

    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("data"):
            user_id = data["data"][0]["id"]
            print(f"[ModBot] User ID for {username}: {user_id}")
            return user_id
        else:
            print(f"[ModBot] No user found with username {username}.")
            return None
    else:
        print(f"[ModBot] Failed to get user ID for {username}. Status: {response.status_code}, Body: {response.text}")
        return None


def timeout_user_via_api(user_id, moderator_id, broadcaster_id, duration, reason, access_token, client_id):
    url = "https://api.twitch.tv/helix/moderation/bans"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Client-Id": client_id,
        "Content-Type": "application/json"
    }
    data = {
        "data": {
            "user_id": user_id,  # Must be user_id, not name
            "duration": duration,
            "reason": reason
        }
    }
    params = {
        "broadcaster_id": broadcaster_id,
        "moderator_id": moderator_id
    }
    response = requests.post(url, headers=headers, params=params, json=data)
    print(f"[ModBot] Timeout response: {response.status_code} - {response.text}")

def ban_user_via_api(user_id, moderator_id, broadcaster_id, reason, access_token, client_id):
    url = "https://api.twitch.tv/helix/moderation/bans"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Client-Id": client_id,
        "Content-Type": "application/json"
    }

    data = {
        "data": {
            "user_id": user_id,
            "reason": reason
        }
    }

    params = {
        "broadcaster_id": broadcaster_id,
        "moderator_id": moderator_id
    }

    response = requests.post(url, headers=headers, params=params, json=data)
    print(f"[ModBot] Ban response: {response.status_code} - {response.text}")
