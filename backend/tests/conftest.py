import pytest
from threading import Thread
from main import create_app
from helpers import hash_password
from bson.objectid import ObjectId

### Contains Pytest Fixtures to be used for testing

# Create a test client
@pytest.fixture
def client():
    app = create_app(testing=True)
    with app.test_client() as client:
        yield client

# Run the flask server on a seperate thread
@pytest.fixture(scope="session")
def flask_server():
    app = create_app(testing=True)

    def run():
        app.run(port=5000, use_reloader=False)

    thread = Thread(target=run)
    thread.start()
    yield
    thread.join(timeout=1)

# Seeds the test DB with a user, admin, and equipment items
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
        "checked_out_equipment": [ObjectId("000000000000000000000002")],
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

    equipment = [
        {
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
            "unavailable": False,
            "description": "This is a place holder equipment",
            "damaged": False,
        },
        {
            "_id": ObjectId("000000000000000000000001"),
            "name": "Tractor 1",
            "class": "Tractor",
            "farm": "Aroostook",
            "make": "John Deere",
            "year": 2020,
            "checked_out": False,
            "damaged": False,
            "unavailable": False,
            "description": "Test tractor",
            "model": "5075E",
            "use": "Farming",
            "images": [],
            "reports": [],
        },
        {
            "_id": ObjectId("000000000000000000000002"),
            "name": "Tractor 2",
            "class": "Tractor",
            "farm": "Highmoor",
            "make": "Ford",
            "year": 2019,
            "checked_out": True,
            "damaged": False,
            "unavailable": False,
            "description": "Test tractor 2",
            "model": "8630",
            "use": "Farming",
            "images": [],
            "reports": [],
        },
        {
            "_id": ObjectId("000000000000000000000003"),
            "name": "Forklift 1",
            "class": "Forklift",
            "farm": "Rogers",
            "make": "Yale",
            "year": 2021,
            "checked_out": False,
            "damaged": True,
            "unavailable": False,
            "description": "Test forklift",
            "model": "GP050",
            "use": "Warehouse",
            "images": [],
            "reports": [],
        },
        {
            "_id": ObjectId("000000000000000000000004"),
            "name": "Truck 1",
            "class": "Truck",
            "farm": "Witter",
            "make": "Chevrolet",
            "year": 2018,
            "checked_out": False,
            "damaged": False,
            "unavailable": True,
            "description": "Test truck",
            "model": "Silverado",
            "use": "Transport",
            "images": [],
            "reports": [],
        },
    ]

    db.equipment_db.insert_many(equipment)

    return db

# Authenticates a logged in user
@pytest.fixture
def login_user(client, seed_db):
    res = client.post(
        "/authenticate", json={"email": "user@gmail.com", "password": "test_pass"}
    )
    assert res.get_json()["result"]
    return client

# Authenticates a logged in admin
@pytest.fixture
def login_admin(client, seed_db):
    res = client.post(
        "/authenticate", json={"email": "admin@gmail.com", "password": "test_pass"}
    )
    assert res.get_json()["result"]
    return client

# Clean the database after each test
@pytest.fixture(autouse=True)
def clean_db(client):
    db = client.application.db
    db.users_db.delete_many({})
    db.equipment_db.delete_many({})
    db.notifications_db.delete_many({})
