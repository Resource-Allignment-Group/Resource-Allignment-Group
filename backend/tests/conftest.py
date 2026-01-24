import pytest
from threading import Thread
from main import create_app
from helpers import hash_password
from bson.objectid import ObjectId


@pytest.fixture
def client():
    app = create_app(testing=True)
    with app.test_client() as client:
        yield client


@pytest.fixture(scope="session")
def flask_server():
    app = create_app(testing=True)

    def run():
        app.run(port=5000, use_reloader=False)

    thread = Thread(target=run)
    thread.start()
    yield
    thread.join(timeout=1)


@pytest.fixture
def seed_db(client):
    db = client.application.db

    user = {
        "_id": ObjectId("112233445566778899001120"),
        "email": "user@gmail.com",
        "password": hash_password("test_pass"),
        "name": "Test User",
        "phone": "3333333333",
        "role": "u",
        "position": None,
        "checked_out_equipment": [],
        "inbox": [],
    }

    db.users_db.insert_one(user)

    admin = {
        "_id": ObjectId("112233445566778899001121"),
        "email": "admin@gmail.com",
        "password": hash_password("test_pass"),
        "name": "Test Admin",
        "phone": "1111111111",
        "position": None,
        "role": "a",
        "checked_out_equipment": [],
        "inbox": [],
    }

    db.users_db.insert_one(admin)

    equipment = {
        "_id": ObjectId("000000000000000000000000"),
        "name": "Testing Equipment",
        "class": "None",
        "year": 2000,
        "farm": "None",
        "model": "None",
        "make": "None",
        "use": "None",
        "images": [],
        "reports": [],
        "checked_out": False,
        "description": "This is a place holder equipment",
        "damaged": False,
    }

    db.equipment_db.insert_one(equipment)

    return db


@pytest.fixture
def login_user(client, seed_db):
    res = client.post(
        "/authenticate", json={"email": "user@gmail.com", "password": "test_pass"}
    )
    print(res.get_json())
    assert res.get_json()["result"]
    return client


@pytest.fixture
def login_admin(client, seed_db):
    res = client.post(
        "/authenticate", json={"email": "admin@gmail.com", "password": "test_pass"}
    )
    print(res.get_json())
    assert res.get_json()["result"]
    return client

@pytest.fixture(autouse=True)
def clean_db(client):
    db = client.application.db
    db.users_db.delete_many({})
    db.equipment_db.delete_many({})
    db.notifications_db.delete_many({})
