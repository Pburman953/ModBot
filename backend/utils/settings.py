import os
import json

SETTINGS_PATH = os.path.join("backend", "bot_settings.json")

def load_settings():
    if not os.path.exists(SETTINGS_PATH):
        return {"toxicity_threshold": 0.5, "blacklisted_words": []}
    with open(SETTINGS_PATH, "r") as f:
        return json.load(f)

def save_settings(settings):
    with open(SETTINGS_PATH, "w") as f:
        json.dump(settings, f, indent=4)
