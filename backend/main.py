from flask import Flask, session, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv
from database import Database

load_dotenv()

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=["http://localhost:3000"])
app.secret_key = os.environ.get("FLASK_SECRET_KEY")

db = Database()


@app.route("/authenticate", methods=["POST", "GET"])
def authenticate():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username == "test_user" and password == "test_pass":
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
