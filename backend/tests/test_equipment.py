import pytest
from bson import ObjectId
from database import DatabaseManager

### Fixtures for the following tests

# Creates a mock database based on the real one for testing
@pytest.fixture
def db():
    db = DatabaseManager(testing=True)
    yield db
    # Clean the mock db after testing
    # New one will be made for each test
    db.equipment_db.delete_many({})
    db.users_db.delete_many({})
    db.notifications_db.delete_many({})

# Inserts sample equipment into the mock database
@pytest.fixture
def sample_equipment(db):
    equipment_data = [
        {
            "_id": ObjectId(),
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
            "_id": ObjectId(),
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
            "_id": ObjectId(),
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
            "_id": ObjectId(),
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
    db.equipment_db.insert_many(equipment_data)
    return [item["_id"] for item in equipment_data]


### UNIT TESTS ###


### Test the sidebar filters

# Ensure that the farm options are returned/loaded
def test_farms(db, sample_equipment):
    farms = {eq.farm for eq in db.get_all_equipment() if eq.farm}
    assert farms == {"Aroostook", "Highmoor", "Rogers", "Witter"}

# Ensure that the equipment classes are returned/loaded
def test_classes(db, sample_equipment):
    classes = {eq._class for eq in db.get_all_equipment() if eq._class}
    assert classes == {"Tractor", "Forklift", "Truck"}

# Ensure that the equipment makes are returned/loaded
def test_makes(db, sample_equipment):
    makes = {eq.make for eq in db.get_all_equipment() if eq.make}
    assert makes == {"John Deere", "Ford", "Yale", "Chevrolet"}

### Test marking equipment as unavailable/available

# Mark a single equipment as unavailable
def test_mark_single_unavailable(db, sample_equipment):
    equip_id = sample_equipment[0]
    count = db.bulk_update_equipment_unavailable([equip_id], True)
    assert count == 1
    assert db.get_equipment_by_id(equip_id).unavailable is True

# Mark multiple equipment as unavailable
def test_mark_multiple_unavailable(db, sample_equipment):
    equip_ids = [sample_equipment[0]]
    count = db.bulk_update_equipment_unavailable(equip_ids, True)
    assert count == 1
    for eq_id in equip_ids:
        assert db.get_equipment_by_id(eq_id).unavailable is True

# Mark an unavailable equipment as available
def test_mark_unavailable_to_available(db, sample_equipment):
    equip_id = sample_equipment[3]  # Truck 1
    count = db.bulk_update_equipment_unavailable([equip_id], False)
    assert count == 1
    assert db.get_equipment_by_id(equip_id).unavailable is False

# Ensure checked out equipment is skipped when marking items unavailable
def test_checked_out_skipped(db, sample_equipment):
    equip_id = sample_equipment[1]  # Tractor 2
    eq = db.get_equipment_by_id(equip_id)
    assert eq.checked_out or eq.damaged or eq.unavailable

# Ensure damaged equipment is skipped when marking items unavailable
def test_damaged_skipped(db, sample_equipment):
    equip_id = sample_equipment[2]  # Forklift 1
    eq = db.get_equipment_by_id(equip_id)
    assert eq.checked_out or eq.damaged or eq.unavailable

### Test getting equipment based on their IDs

# Get 1 equipment item by its ID
def test_single(db, sample_equipment):
    eq_list = db.get_equipment_by_ids([sample_equipment[0]])
    assert len(eq_list) == 1
    assert eq_list[0].id == sample_equipment[0]

# Get more than 1 equipment items by their IDs
def test_multiple(db, sample_equipment):
    eq_list = db.get_equipment_by_ids(sample_equipment[:2])
    names = [eq.name for eq in eq_list]
    assert set(names) == {"Tractor 1", "Tractor 2"}

# Get all equipment by their IDs
def test_all(db, sample_equipment):
    eq_list = db.get_equipment_by_ids(sample_equipment)
    assert len(eq_list) == 4

### Test for canceling a pending equipment request
### when that item is marked as unavailable

# Cancel pending request when the equipment becomes unavailable
def test_cancel_pending(db, sample_equipment):
    equip_id = sample_equipment[0]
    user_id = ObjectId()
    db.users_db.insert_one({
        "_id": user_id,
        "email": "test@test.com",
        "password": "test",
        "role": "p",
        "checked_out_equipment": [],
        "inbox": [],
        "position": None,
        "name": "Test User",
        "phone": "1234567890"
    })
    notif_id = ObjectId()
    db.notifications_db.insert_one({
        "_id": notif_id,
        "sender": user_id,
        "receiver": ObjectId(),
        "body": "Request to checkout",
        "date": "2026-01-26",
        "type": "r",
        "equipment_id": equip_id,
        "read": False,
        "status": "p"
    })
    count = db.cancel_pending_requests_for_equipment([equip_id])
    assert count == 1
    assert db.notifications_db.find_one({"_id": notif_id})["status"] == "r"

# Ensure that approved equipment requests aren't canceled
def test_does_not_cancel_approved(db, sample_equipment):
    equip_id = sample_equipment[0]
    user_id = ObjectId()
    db.users_db.insert_one({
        "_id": user_id,
        "email": "test@test.com",
        "password": "test",
        "role": "p",
        "checked_out_equipment": [],
        "inbox": [],
        "position": None,
        "name": "Test User",
        "phone": "1234567890"
    })
    notif_id = ObjectId()
    db.notifications_db.insert_one({
        "_id": notif_id,
        "sender": user_id,
        "receiver": ObjectId(),
        "body": "Request to checkout",
        "date": "2026-01-26",
        "type": "r",
        "equipment_id": equip_id,
        "read": False,
        "status": "a"
    })
    count = db.cancel_pending_requests_for_equipment([equip_id])
    assert count == 0
    assert db.notifications_db.find_one({"_id": notif_id})["status"] == "a"

### Test to find the equipment checked out to a specified user

# Find which user has an equipment item checked out to them
def test_find_user_checked_out(db, sample_equipment):
    equip_id = sample_equipment[1]
    user_id = ObjectId()
    db.users_db.insert_one({
        "_id": user_id,
        "email": "user@test.com",
        "password": "test",
        "role": "p",
        "checked_out_equipment": [equip_id],
        "inbox": [],
        "position": "Researcher",
        "name": "John Doe",
        "phone": "1234567890"
    })
    user = db.get_user_by_equipment(equip_id)
    assert user is not None
    assert equip_id in user.checked_out_equipment

# Ensure that available equipment aren't marked as checked out to a user
def test_no_user_for_available_equipment(db, sample_equipment):
    equip_id = sample_equipment[0]
    assert db.get_user_by_equipment(equip_id) is None


### INTEGRATION TESTS ###


# Test the flow of a user requesting & returning an equipment item 
def test_request_equipment(login_user, db):
    # Request equipment
    res = login_user.post("/request_equipment", json={
        "equip_id": "000000000000000000000000",
        "equip_name": "test_equip"
    })
    assert res.get_json()["result"]

    # Admin approves the request
    notifications = db.get_notifications_by_equipment("000000000000000000000000")
    notification_dict = notifications.to_dict(sender_name="test_sender_name")
    res = login_user.post("/admin_account_decision", json={
        "result": True,
        "notification": notification_dict
    })
    assert res.get_json()["result"]

    # Return equipment
    res = login_user.post("/return_equipment", json={
        "equipment_id": "000000000000000000000000"
    })
    assert res.get_json()["result"]