import bcrypt
from database import DatabaseManager
import pandas as pd
from equipment import Equipment
from uuid import uuid4


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
    df = pd.read_excel("/Users/Bradan/Downloads/Copy of MAFES Test Data.xlsx")
    df.drop(
        [
            "Serial",
            "Use",
            "User",
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
    print(df.head())
    for i, tup in enumerate(df.iterrows()):
        _, row = tup
        if i == 0:
            continue
        row = list(row)
        print(i, ":", row)
        name = (
            ", ".join([str(row[5]), str(row[2]), str(row[3]), str(row[4])])
            + f" ({row[1]})"
        )
        name = name.replace("nan, ", "")
        print("name", name)
        equip = Equipment(uuid=str(uuid4()), name=name, _class=row[1], year=row[4])
        db.add_equipment(
            equipment=equip,
        )
