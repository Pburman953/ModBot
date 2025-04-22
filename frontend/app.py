import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask, jsonify, render_template, request, redirect, url_for
from backend.utils.user_tracker import get_all_offenses
from backend.utils.adaptive_punishment2 import load_whitelist, save_whitelist
from backend.utils.settings import load_settings, save_settings


import time

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/flagged')
def flagged():
    # Load flagged message data
    flagged_data = get_all_offenses()

    # Convert UNIX timestamps to readable format
    for user, data in flagged_data.items():
        ts = data.get("last_offense", 0)
        data["last_offense_readable"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts))

    # Pass the flagged data to the template
    return render_template("flagged.html", flagged_messages=flagged_data)

@app.route('/get_flagged_data', methods=["GET"])
def get_flagged_data():
    # Load flagged message data
    flagged_data = get_all_offenses()

    # Convert UNIX timestamps to readable format
    for user, data in flagged_data.items():
        ts = data.get("last_offense", 0)
        data["last_offense_readable"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts))

    # Return flagged data as JSON for AJAX
    return jsonify(flagged_data)



@app.route('/whitelist', methods=["GET", "POST"])
def whitelist():
    whitelist = load_whitelist()

    if request.method == "POST":
        action = request.form.get("action")

        if action == "add":
            username = request.form.get("username", "").strip().lower()
            if username and username not in whitelist:
                whitelist.add(username)
                save_whitelist(whitelist)
                print(f"[ModBot] Added '{username}' to whitelist")

        elif action == "remove":
            username = request.form.get("username_to_remove", "").strip().lower()
            if username in whitelist:
                whitelist.remove(username)
                save_whitelist(whitelist)
                print(f"[ModBot] Removed '{username}' from whitelist")

        return redirect(url_for('whitelist'))

    return render_template("whitelist.html", whitelist=sorted(whitelist))



@app.route('/settings', methods=["GET", "POST"])
def settings():
    settings_data = load_settings()

    if request.method == "POST":
        action = request.form.get("action")

        # Safe parsing of threshold
        try:
            threshold = float(request.form.get("threshold", settings_data.get("toxicity_threshold", 0.5)))
            settings_data["toxicity_threshold"] = threshold
        except ValueError:
            pass  # fallback if somehow invalid input gets through

        if action == "add":
            new_word = request.form.get("blacklisted_word", "").strip().lower()
            if new_word and new_word not in settings_data["blacklisted_words"]:
                settings_data["blacklisted_words"].append(new_word)

        elif action == "remove":
            word_to_remove = request.form.get("word_to_remove", "").strip().lower()
            if word_to_remove in settings_data["blacklisted_words"]:
                settings_data["blacklisted_words"].remove(word_to_remove)

        # Save changes and refresh page
        save_settings(settings_data)
        return redirect(url_for('settings'))

    return render_template(
        "settings.html", 
        toxicity_threshold=settings_data.get("toxicity_threshold", 0.5),
        blacklisted_words=settings_data.get("blacklisted_words", [])
    )






if __name__ == '__main__':
    app.run(debug=True)
