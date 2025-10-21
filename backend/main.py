from flask import Flask
from pymongo import MongoClient
import os

app = Flask(__name__)
client = MongoClient(os.environ.get("DATABASE_URI"))
user_db = client["Users"]
users_col = user_db["user_collection"]

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG"), port=5000)