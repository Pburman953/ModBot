import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask, jsonify, render_template, request, redirect, url_for
from backend.utils.user_tracker import get_all_offenses
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
    if request.method == "POST":
        # Add username to whitelist logic
        pass
    return render_template("whitelist.html", whitelist=[])

@app.route('/settings', methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        # Save settings logic here
        pass
    return render_template("settings.html", threshold=0.5, blacklist=[])

if __name__ == '__main__':
    app.run(debug=True)
