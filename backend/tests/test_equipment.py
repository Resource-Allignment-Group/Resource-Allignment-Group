import pytest
from bson import ObjectId
from database import DatabaseManager

### Test the sidebar filters -----------------------------------------


# Ensure that the farm options are returned/loaded
def test_farms(login_user):
    db = login_user.application.db
    farms = {eq.farm for eq in db.get_all_equipment() if eq.farm and eq.farm != "None"}
    assert farms == {"Aroostook", "Highmoor", "Rogers", "Witter"}


# Ensure that the equipment classes are returned/loaded
def test_classes(login_user):
    db = login_user.application.db
    classes = {
        eq._class for eq in db.get_all_equipment() if eq._class and eq._class != "None"
    }
    assert classes == {"Tractor", "Forklift", "Truck"}


# Ensure that the equipment makes are returned/loaded
def test_makes(login_user):
    db = login_user.application.db
    makes = {eq.make for eq in db.get_all_equipment() if eq.make and eq.make != "None"}
    assert makes == {"John Deere", "Ford", "Yale", "Chevrolet"}


### Test marking equipment as unavailable/available -----------------------------------------


# Mark a single equipment as unavailable
def test_mark_single_unavailable(login_user):
    db = login_user.application.db
    all_equip = db.get_all_equipment()
    # Get an item from the mock db
    equip_id = all_equip[1].id
    count = db.bulk_update_equipment_unavailable([equip_id], True)
    assert count == 1
    assert db.get_equipment_by_id(equip_id).unavailable is True


# Mark multiple equipment as unavailable
def test_mark_multiple_unavailable(login_user):
    db = login_user.application.db
    all_equip = db.get_all_equipment()
    # Only pick equipment that is initially available
    equip_ids = [
        eq.id
        for eq in all_equip
        if not eq.unavailable and not eq.checked_out and not eq.damaged
    ]
    count = db.bulk_update_equipment_unavailable(equip_ids, True)
    assert count == len(equip_ids)
    # Ensure they were flagged correctly
    for eq_id in equip_ids:
        assert db.get_equipment_by_id(eq_id).unavailable is True


# Mark an unavailable equipment as available
def test_mark_unavailable_to_available(login_user):
    db = login_user.application.db
    all_equip = db.get_all_equipment()
    equip_id = all_equip[4].id  # Truck 1
    count = db.bulk_update_equipment_unavailable([equip_id], False)
    assert count == 1
    assert db.get_equipment_by_id(equip_id).unavailable is False


# Ensure checked out equipment is skipped when marking items unavailable
def test_checked_out_skipped(login_user):
    db = login_user.application.db
    all_equip = db.get_all_equipment()
    equip_id = all_equip[2].id  # Tractor 2
    count = db.bulk_update_equipment_unavailable([equip_id], True)
    assert count == 0
    assert db.get_equipment_by_id(equip_id).unavailable is False


# Ensure damaged equipment is skipped when marking items unavailable
def test_damaged_skipped(login_user):
    db = login_user.application.db
    all_equip = db.get_all_equipment()
    equip_id = all_equip[3].id  # Forklift 1
    count = db.bulk_update_equipment_unavailable([equip_id], True)
    assert count == 0
    assert db.get_equipment_by_id(equip_id).unavailable is False


### Test the sidebar search input with various search queries -----------------------------------------


# If the search bar is empty, return all equipment as usual
def test_search_no_query_returns_all(login_user):
    res = login_user.post("/search_equipment", json={"query": ""})
    data = res.get_json()
    assert data["result"] is True
    # All 5 sample equipment should be returned
    assert len(data["equip_list"]) == 5


# If they search param is an exact match, that item should be returned
def test_search_exact_name_match(login_user):
    res = login_user.post("/search_equipment", json={"query": "Tractor 1"})
    data = res.get_json()
    names = [e["name"] for e in data["equip_list"]]
    # Ensure we get the expected result
    assert "Tractor 1" in names
    # Ensure it is at the top
    assert data["equip_list"][0]["name"] == "Tractor 1"


# Partial inputs (like 'tract' for tractor) should be accepted
def test_search_partial_name(login_user):
    res = login_user.post("/search_equipment", json={"query": "tract"})
    data = res.get_json()
    names = [e["name"] for e in data["equip_list"]]
    # Both tractors should be returned
    assert "Tractor 1" in names
    assert "Tractor 2" in names
    # Should not include Forklift or Truck
    assert "Forklift 1" not in names
    assert "Truck 1" not in names
    assert "Testing Equipment" not in names


# Accept typos and/or missed characters in the search params
def test_search_fuzzy_typo(login_user):
    res = login_user.post("/search_equipment", json={"query": "tractr"})
    data = res.get_json()
    names = [e["name"] for e in data["equip_list"]]
    # Typos should still return similar results
    assert "Tractor 1" in names
    assert "Tractor 2" in names


# Allow multiple words to be searched at a time (search diff equipment fields)
def test_search_multi_word_across_fields(login_user):
    res = login_user.post("/search_equipment", json={"query": "Ford Tractor"})
    data = res.get_json()
    names = [e["name"] for e in data["equip_list"]]
    # "Ford Truck" should match Tractor 2
    assert "Tractor 2" in names
    # Tractor 2 should rank first
    assert data["equip_list"][0]["name"] == "Tractor 2"


# Should be able to search equipment by status lines
def test_search_by_status_checked_out(login_user):
    res = login_user.post("/search_equipment", json={"query": "checked out"})
    data = res.get_json()
    names = [e["name"] for e in data["equip_list"]]
    # Only Tractor 2 is checked out
    assert "Tractor 2" in names
    # No other items should be returned
    assert "Tractor 1" not in names
    assert "Forklift 1" not in names
    assert "Truck 1" not in names
    assert "Testing Equipment" not in names


def test_search_by_status_unavailable(login_user):
    res = login_user.post("/search_equipment", json={"query": "unavailable"})
    data = res.get_json()
    assert data["equip_list"][0]["name"] == "Truck 1"


def test_search_by_status_damaged(login_user):
    res = login_user.post("/search_equipment", json={"query": "damaged"})
    data = res.get_json()
    assert data["equip_list"][0]["name"] == "Forklift 1"


def test_search_by_status_available(login_user):
    res = login_user.post("/search_equipment", json={"query": "available"})
    data = res.get_json()
    names = [e["name"] for e in data["equip_list"]]
    # Only Tractor 1  and Testing Equipment is available
    assert "Tractor 1" in names
    assert "Testing Equipment" in names


# Ensure the search params parse multiple equipment fields (make, desc., etc)
def test_search_combined_fields(login_user):
    # A search with multiple words to map to Tractor 1
    res = login_user.post(
        "/search_equipment", json={"query": "5075E John Deere Test Aroostook"}
    )
    data = res.get_json()
    names = [e["name"] for e in data["equip_list"]]
    # These params should return Tractor 1
    assert "Tractor 1" in names
    # Rank Tractor 1 as first since it will be strongest match
    assert data["equip_list"][0]["name"] == "Tractor 1"


# Allow capitalization and lowercase in searches
def test_search_case_insensitive(login_user):
    res = login_user.post("/search_equipment", json={"query": "trAcToR"})
    data = res.get_json()
    names = [e["name"] for e in data["equip_list"]]
    # Should still return both tractors
    assert "Tractor 1" in names
    assert "Tractor 2" in names


# Ensure search results that are weak don't appear
def test_search_score_threshold(login_user):
    # Random string that doesn't match anything
    res = login_user.post(
        "/search_equipment", json={"query": "zzzzxyzzzzzxyxyxyzyzyyxy"}
    )
    data = res.get_json()
    assert len(data["equip_list"]) == 0


### Test getting equipment based on their IDs -----------------------------------------


# Get 1 equipment item by its ID
def test_single(login_user):
    db = login_user.application.db
    all_equip = db.get_all_equipment()
    equip_id = all_equip[1].id  # Tractor 1
    eq_list = db.get_equipment_by_ids([equip_id])
    assert len(eq_list) == 1
    assert eq_list[0].id == equip_id


# Get more than 1 equipment items by their IDs
def test_multiple(login_user):
    db = login_user.application.db
    all_equip = db.get_all_equipment()
    equip_ids = [all_equip[1].id, all_equip[2].id]  # Tractor 1, Tractor 2
    eq_list = db.get_equipment_by_ids(equip_ids)
    names = [eq.name for eq in eq_list]
    assert set(names) == {"Tractor 1", "Tractor 2"}


# Get all equipment by their IDs
def test_all(login_user):
    db = login_user.application.db
    all_equip = db.get_all_equipment()
    equip_ids = [eq.id for eq in all_equip]
    eq_list = db.get_equipment_by_ids(equip_ids)
    assert len(eq_list) == 5


### Test for canceling a pending equipment request -----------------------------------------
### when that item is marked as unavailable


# Cancel pending request when the equipment becomes unavailable
def test_cancel_pending(login_user):
    db = login_user.application.db
    all_equip = db.get_all_equipment()
    equip_id = all_equip[1].id # Tractor 1
    user_id = ObjectId()
    db.users_db.insert_one({
        "_id": user_id,
        "email": "test@test.com",
        "password": "test_Pass2",
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
def test_does_not_cancel_approved(login_user):
    db = login_user.application.db
    all_equip = db.get_all_equipment()
    equip_id = all_equip[1].id # Tractor 1
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


### Test to find the equipment checked out to a specified user -----------------------------------------


# Find which user has an equipment item checked out to them
def test_find_user_checked_out(login_user):
    db = login_user.application.db
    all_equip = db.get_all_equipment()
    equip_id = all_equip[2].id  # Tractor 2
    user_id = ObjectId()
    db.users_db.insert_one(
        {
            "_id": user_id,
            "email": "user@test.com",
            "password": "test",
            "role": "p",
            "checked_out_equipment": [equip_id],
            "inbox": [],
            "position": "Researcher",
            "name": "John Doe",
            "phone": "1234567890",
        }
    )
    user = db.get_user_by_equipment(equip_id)
    assert user is not None
    assert equip_id in user.checked_out_equipment


# Ensure that available equipment aren't marked as checked out to a user
def test_no_user_for_available_equipment(login_user):
    db = login_user.application.db
    all_equip = db.get_all_equipment()
    equip_id = all_equip[1].id  # Tractor 1
    assert db.get_user_by_equipment(equip_id) is None


# Test the flow of a user requesting & returning an equipment item
def test_request_equipment(login_user):
    # Request equipment
    res = login_user.post(
        "/request_equipment",
        json={"equip_id": "000000000000000000000000", "equip_name": "test_equip"},
    )
    assert res.get_json()["result"]

    # Admin approves the request
    db = login_user.application.db
    notifications = db.get_notifications_by_equipment("000000000000000000000000")
    notification_dict = notifications.to_dict(sender_name="test_sender_name")
    res = login_user.post(
        "/admin_account_decision",
        json={"result": True, "notification": notification_dict},
    )
    assert res.get_json()["result"]

    # Return equipment
    res = login_user.post(
        "/return_equipment", json={"equipment_id": "000000000000000000000000", "damage_description": ""}
    )
    assert res.get_json()["result"]

def test_equipment_editing(login_admin):
    res = login_admin.post(
        "/change_equipment_info",
        json={
            "equipment": {
                "id": "000000000000000000000000",
                "name": "Testing Changed Name Equipment",
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
                "description": "This is a placeholder equipment",
                "damaged": False
            }
        },
    )
    assert res.get_json()["result"]

def test_equipment_editing_fail(login_admin):
    res = login_admin.post(
        "/change_equipment_info",
        json={
            "equipment": {
                "id": "000000000000000000000000",
                "name": "Testing Changed Name Equipment",
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
                "description": "This is a placeholder equipment",
                "damaged": False,
                "extra_key": "this should fail",
            }
        },
    )
    assert not res.get_json()["result"]