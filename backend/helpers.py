import bcrypt
from database import DatabaseManager
import pandas as pd
from equipment import Equipment
from bson.objectid import ObjectId
from dotenv import load_dotenv
import secrets
import hashlib
from pymongo import MongoClient
import os
from datetime import datetime, timedelta, timezone

def generate_reset_token():
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    return token, token_hash


def hash_password(password: str):
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    return hashed_password.decode("utf-8")


def check_password(origional_password: str, hashed_password: str):
    origional_password_bytes = origional_password.encode("utf-8")
    hashed_password_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(origional_password_bytes, hashed_password_bytes)


def insert_via_spreadsheet():
    db = DatabaseManager()
    df = pd.read_excel(
        "/Users/Bradan/Downloads/MAFES Equipment Inventory_2025_tcm.xlsx"
    )
    df.drop(
        [
            "Serial",
            "Unnamed: 9",
            "Unnamed: 10",
            "Unnamed: 11",
            "Unnamed: 12",
            "Unnamed: 13",
            "Unnamed: 14",
            "Unnamed: 15",
        ],
        axis=1,
        inplace=True,
    )
    df = df.fillna("None")
    for i, tup in enumerate(df.iterrows()):
        _, row = tup

        if i == 0:
            continue
        row = list(row)
        name = (
            ", ".join([str(row[5]), str(row[2]), str(row[3]), str(row[4])])
            + f" ({row[1]})"
        )
        name = name.replace("nan, ", "")
        equip = Equipment(
            uuid=ObjectId(),
            name=name,
            _class=row[1],
            year=row[4],
            farm=row[0],
            model=row[3],
            make=row[2],
            description=row[5],
            use=row[6],
            damaged=False,
        )
        db.add_equipment(
            equipment=equip,
        )


def fill_database_with_notifications():
    load_dotenv()
    _client = MongoClient(os.environ.get("DATABASE_URI"))
    db = _client["RAM_DB"]
    for i in range(3000):
        db["notifications"].insert_one({
            "_id": ObjectId(),
            "sender": ObjectId(),
            "receiver": ObjectId(),
            "body": "This is just a testing notification, if you see this please delete immediatly, This is just a testing notification, if you see this please delete immediatly, This is just a testing notification, if you see this please delete immediatly, This is just a testing notification, if you see this please delete immediatly, This is just a testing notification, if you see this please delete immediatly, This is just a testing notification, if you see this please delete immediatly, This is just a testing notification, if you see this please delete immediatly",
            "date": datetime.now(timezone.utc) - timedelta(weeks=2),
            "type": "i",
            "equipment_id": None,
            "read": True,
            "status": None
        })

fill_database_with_notifications()