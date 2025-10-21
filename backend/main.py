from flask import Flask
from pymongo import MongoClient
import os

app = Flask(__name__)
client = MongoClient()
if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG"), port=5000)