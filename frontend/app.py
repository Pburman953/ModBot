from flask import Flask, render_template, request, redirect, url_for
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend import config
from backend.utils.user_tracker import get_all_offenses, reset_offenses
from backend.utils.adaptive_punishment2 import WHITELIST, add_to_whitelist, load_whitelist

app = Flask(__name__)

@app.route("/")
def index():
    offenses = get_all_offenses()
    return render_template("index.html", offenses=offenses, whitelist=sorted(WHITELIST))

@app.route("/whitelist", methods=["POST"])
def whitelist_user():
    username = request.form["username"]
    add_to_whitelist(username)
    return redirect(url_for("index"))

@app.route("/reset/<username>")
def reset_user(username):
    reset_offenses(username)
    return redirect(url_for("index"))

if __name__ == "__main__":
    load_whitelist()
    app.run(debug=True)
