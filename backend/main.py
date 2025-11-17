from flask import Flask, session, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv
from database import Database
from flask_session import Session
from helpers import *


load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")

CORS(app, supports_credentials=True, origins=["http://localhost:3000"])

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_COOKIE_SAMESITE"] = None


db = Database()


@app.route("/authenticate", methods=["POST", "GET"])
def authenticate():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    user_information = db.get_user_by_username(username=username)

    if check_password(
        origional_password=password, hashed_password=user_information["password"]
    ):
        session["user"] = username
        return jsonify({"message": "success"})
    else:
        return jsonify({"message": "invalid credentials"})


@app.route("/check-session", methods=["GET"])
def check_session():
    user = session.get("user")

    if user:
        return jsonify({"user": user})
    else:
        return jsonify({"user": None})


@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user", None)
    return jsonify({"message": "logged out"})


# make sure to sanitize images for <script> tags, assigning UUID will happen in the back end
if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG"), port=5000)
