import pytest
import io
import openpyxl
from PIL import Image
from bson import ObjectId
from equipment import Equipment

# Tests for equipment-related DB methods and routes:
# sidebar filters, search, availability, checkout/return,
# CRUD operations, file management, and admin access control

### Sidebar filter options -----------------------------------------

def test_farms(login_user):
    # Ensure that the farm options are returned/loaded
    db = login_user.application.db
    farms = {eq.farm for eq in db.get_all_equipment() if eq.farm and eq.farm != "None"}
    assert farms == {"Aroostook", "Highmoor", "Rogers", "Witter"}

def test_classes(login_user):
    # Ensure that the equipment classes are returned/loaded
    db = login_user.application.db
    classes = {
        eq._class
        for eq in db.get_all_equipment()
        if eq._class and eq._class != "None"
    }
    assert classes == {"Tractor", "Forklift", "Truck"}

def test_makes(login_user):
    # Ensure that the equipment makes are returned/loaded
    db = login_user.application.db
    makes = {eq.make for eq in db.get_all_equipment() if eq.make and eq.make != "None"}
    assert makes == {"John Deere", "Ford", "Yale", "Chevrolet"}

def test_get_filter_options_endpoint(login_user):
    # Verify the /get_filter_options route returns all categories
    res = login_user.get("/get_filter_options")
    data = res.get_json()
    assert data["result"] is True
    assert "farms" in data
    assert "classes" in data
    assert "makes" in data
    assert "uses" in data
    assert "statuses" in data
    assert "Aroostook" in data["farms"]
    assert "Tractor" in data["classes"]

### Get equipment -----------------------------------------

def test_get_all_equipment(login_user):
    # Get all equipment items
    db = login_user.application.db
    all_equip = db.get_all_equipment()
    assert len(all_equip) == 5

def test_get_equipment_by_id(login_user):
    # Get 1 equipment item by its ID
    db = login_user.application.db
    all_equip = db.get_all_equipment()
    equip_id = all_equip[1].id  # Tractor 1
    equipment = db.get_equipment_by_id(equip_id)
    assert equipment.id == equip_id

def test_get_equipment_by_id_not_found(login_user):
    db = login_user.application.db
    result = db.get_equipment_by_id(ObjectId())
    assert result is None

def test_get_equipment_endpoint(login_user):
    res = login_user.get("/get_equipment")
    data = res.get_json()
    assert data["result"] is True
    assert len(data["equip_list"]) == 5

def test_get_equipment_sorted_by_status(login_user):
    # Available items should come before checked out / damaged / unavailable
    res = login_user.get("/get_equipment")
    data = res.get_json()
    statuses = []
    for e in data["equip_list"]:
        if e["unavailable"]:
            statuses.append(4)
        elif e["damaged"]:
            statuses.append(3)
        elif e["checked_out"]:
            statuses.append(2)
        else:
            statuses.append(1)
    assert statuses == sorted(statuses)

def test_get_equipment_by_user(login_user):
    db = login_user.application.db
    user = db.get_user_by_email("user@gmail.com")
    equip_list = db.get_equipment_by_user(user.id)
    # Seeded user has Tractor 2 checked out
    assert len(equip_list) == 1
    assert equip_list[0].name == "Tractor 2"

def test_get_equipment_by_user_no_equipment(login_admin):
    db = login_admin.application.db
    admin = db.get_user_by_email("admin@gmail.com")
    equip_list = db.get_equipment_by_user(admin.id)
    assert equip_list == []

def test_get_equipment_by_user_nonexistent_user(login_user):
    db = login_user.application.db
    result = db.get_equipment_by_user(ObjectId())
    assert result == []

def test_get_user_equipment_endpoint(login_user):
    res = login_user.get("/get_user_equipment")
    data = res.get_json()
    assert data["result"] is True
    # Seeded user has Tractor 2 checked out
    assert len(data["equip_list"]) == 1

### Search -----------------------------------------

def test_search_no_query_returns_all(login_user):
    # If the search bar is empty, return all equipment as usual
    res = login_user.post("/search_equipment", json={"query": ""})
    data = res.get_json()
    assert data["result"] is True
    assert len(data["equip_list"]) == 5

def test_search_exact_name_match(login_user):
    # If the search param is an exact match, that item should be returned first
    res = login_user.post("/search_equipment", json={"query": "Tractor 1"})
    data = res.get_json()
    names = [e["name"] for e in data["equip_list"]]
    assert "Tractor 1" in names
    assert data["equip_list"][0]["name"] == "Tractor 1"

def test_search_partial_name(login_user):
    # Partial inputs (like 'tract' for tractor) should be accepted
    res = login_user.post("/search_equipment", json={"query": "tract"})
    data = res.get_json()
    names = [e["name"] for e in data["equip_list"]]
    assert "Tractor 1" in names
    assert "Tractor 2" in names
    assert "Forklift 1" not in names
    assert "Truck 1" not in names
    assert "Testing Equipment" not in names

def test_search_fuzzy_typo(login_user):
    # Accept typos and/or missed characters in the search params
    res = login_user.post("/search_equipment", json={"query": "tractr"})
    data = res.get_json()
    names = [e["name"] for e in data["equip_list"]]
    assert "Tractor 1" in names
    assert "Tractor 2" in names

def test_search_multi_word_across_fields(login_user):
    # Allow multiple words to be searched at a time (search diff equipment fields)
    res = login_user.post("/search_equipment", json={"query": "Ford Tractor"})
    data = res.get_json()
    names = [e["name"] for e in data["equip_list"]]
    assert "Tractor 2" in names
    assert data["equip_list"][0]["name"] == "Tractor 2"

def test_search_by_status_checked_out(login_user):
    # Should be able to search equipment by status
    res = login_user.post("/search_equipment", json={"query": "checked out"})
    data = res.get_json()
    names = [e["name"] for e in data["equip_list"]]
    assert "Tractor 2" in names
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
    assert "Tractor 1" in names
    assert "Testing Equipment" in names

def test_search_combined_fields(login_user):
    # Ensure the search params parse multiple equipment fields (make, desc., etc)
    res = login_user.post(
        "/search_equipment", json={"query": "5075E John Deere Test Aroostook"}
    )
    data = res.get_json()
    names = [e["name"] for e in data["equip_list"]]
    assert "Tractor 1" in names
    assert data["equip_list"][0]["name"] == "Tractor 1"

def test_search_case_insensitive(login_user):
    # Allow capitalization and lowercase in searches
    res = login_user.post("/search_equipment", json={"query": "trAcToR"})
    data = res.get_json()
    names = [e["name"] for e in data["equip_list"]]
    assert "Tractor 1" in names
    assert "Tractor 2" in names

def test_search_score_threshold(login_user):
    # Ensure search results that are weak don't appear
    res = login_user.post(
        "/search_equipment", json={"query": "zzzzxyzzzzzxyxyxyzyzyyxy"}
    )
    data = res.get_json()
    assert len(data["equip_list"]) == 0

### Availability (mark unavailable/available) -----------------------------------------

def test_mark_single_unavailable(login_user):
    # Mark a single equipment as unavailable (DB layer)
    db = login_user.application.db
    all_equip = db.get_all_equipment()
    equip_id = all_equip[1].id
    count = db.bulk_update_equipment_unavailable([equip_id], True)
    assert count == 1
    assert db.get_equipment_by_id(equip_id).unavailable is True

def test_mark_multiple_unavailable(login_user):
    # Mark multiple equipment as unavailable
    db = login_user.application.db
    all_equip = db.get_all_equipment()
    equip_ids = [
        eq.id
        for eq in all_equip
        if not eq.unavailable and not eq.checked_out and not eq.damaged
    ]
    count = db.bulk_update_equipment_unavailable(equip_ids, True)
    assert count == len(equip_ids)
    for eq_id in equip_ids:
        assert db.get_equipment_by_id(eq_id).unavailable is True

def test_mark_unavailable_to_available(login_user):
    # Mark an unavailable equipment as available
    db = login_user.application.db
    all_equip = db.get_all_equipment()
    equip_id = all_equip[4].id  # Truck 1
    count = db.bulk_update_equipment_unavailable([equip_id], False)
    assert count == 1
    assert db.get_equipment_by_id(equip_id).unavailable is False

def test_checked_out_skipped(login_user):
    # Ensure checked out equipment is skipped when marking items unavailable
    db = login_user.application.db
    all_equip = db.get_all_equipment()
    equip_id = all_equip[2].id  # Tractor 2
    count = db.bulk_update_equipment_unavailable([equip_id], True)
    assert count == 0
    assert db.get_equipment_by_id(equip_id).unavailable is False

def test_damaged_skipped(login_user):
    # Ensure damaged equipment is skipped when marking items unavailable
    db = login_user.application.db
    all_equip = db.get_all_equipment()
    equip_id = all_equip[3].id  # Forklift 1
    count = db.bulk_update_equipment_unavailable([equip_id], True)
    assert count == 0
    assert db.get_equipment_by_id(equip_id).unavailable is False

def test_mark_equipment_unavailable_endpoint_admin(login_admin):
    res = login_admin.post(
        "/mark_equipment_unavailable",
        json={"equipment_ids": ["000000000000000000000001"], "unavailable": True},
    )
    data = res.get_json()
    assert data["result"] is True
    assert data["updated_count"] == 1

def test_mark_equipment_available_endpoint_admin(login_admin):
    login_admin.post(
        "/mark_equipment_unavailable",
        json={"equipment_ids": ["000000000000000000000004"], "unavailable": False},
    )
    db = login_admin.application.db
    equip = db.get_equipment_by_id(ObjectId("000000000000000000000004"))
    assert equip.unavailable is False

def test_mark_checked_out_skipped_endpoint(login_admin):
    # Checked out equipment should be skipped and reported in skipped_count
    res = login_admin.post(
        "/mark_equipment_unavailable",
        json={"equipment_ids": ["000000000000000000000002"], "unavailable": True},
    )
    data = res.get_json()
    assert data["result"] is True
    assert data["skipped_count"] == 1
    assert data["updated_count"] == 0

def test_mark_equipment_unavailable_not_admin(login_user):
    # Regular users should not be able to mark equipment as unavailable
    res = login_user.post(
        "/mark_equipment_unavailable",
        json={"equipment_ids": ["000000000000000000000001"], "unavailable": True},
    )
    assert res.status_code in (403, 200)
    if res.status_code == 200:
        assert res.get_json()["result"] is False

def test_mark_equipment_unavailable_already_unavailable_message(login_admin):
    # All selected items already unavailable — should get the "no items marked" message
    res = login_admin.post("/mark_equipment_unavailable", json={
        "equipment_ids": ["000000000000000000000004"],  # Truck 1 (already unavailable)
        "unavailable": True,
    })
    data = res.get_json()
    assert data["result"] is True
    assert data["updated_count"] == 0
    assert "skipped" in data["message"].lower() or "unavailable" in data["message"].lower()

def test_mark_equipment_available_not_unavailable_message(login_admin):
    # Trying to mark available an item that isn't unavailable
    res = login_admin.post("/mark_equipment_unavailable", json={
        "equipment_ids": ["000000000000000000000001"],  # Tractor 1 (not unavailable)
        "unavailable": False,
    })
    data = res.get_json()
    assert data["result"] is True
    assert data["updated_count"] == 0

def test_mark_equipment_partial_skip_message(login_admin):
    # Mix of valid and skipped items — should get the partial message
    res = login_admin.post("/mark_equipment_unavailable", json={
        "equipment_ids": [
            "000000000000000000000001",  # Tractor 1 (available — will be marked)
            "000000000000000000000002",  # Tractor 2 (checked out — will be skipped)
        ],
        "unavailable": True,
    })
    data = res.get_json()
    assert data["result"] is True
    assert data["updated_count"] == 1
    assert data["skipped_count"] == 1

### Checkout / Return -----------------------------------------

def test_add_user_equipment(login_admin):
    db = login_admin.application.db
    user = db.get_user_by_email("user@gmail.com")
    equip_id = ObjectId("000000000000000000000001")  # Tractor 1 (available)
    db.add_user_equipment(user_id=user.id, equipment_id=equip_id, admin_name="Admin")
    equip = db.get_equipment_by_id(equip_id)
    assert equip.checked_out is True
    updated_user = db.get_user_by_id(user.id)
    assert equip_id in updated_user.checked_out_equipment

def test_add_user_equipment_already_checked_out(login_admin):
    db = login_admin.application.db
    user = db.get_user_by_email("user@gmail.com")
    equip_id = ObjectId("000000000000000000000002")  # Tractor 2 (already checked out)
    result = db.add_user_equipment(
        user_id=user.id, equipment_id=equip_id, admin_name="Admin"
    )
    assert "already checked out" in str(result)

def test_delete_user_equipment(login_admin):
    db = login_admin.application.db
    user = db.get_user_by_email("user@gmail.com")
    equip_id = ObjectId("000000000000000000000002")  # Tractor 2 (checked out to user)
    db.delete_user_equipment(user_id=user.id, equipment_id=equip_id)
    equip = db.get_equipment_by_id(equip_id)
    assert equip.checked_out is False

def test_delete_user_equipment_damaged(login_admin):
    db = login_admin.application.db
    user = db.get_user_by_email("user@gmail.com")
    equip_id = ObjectId("000000000000000000000002")
    db.delete_user_equipment(
        user_id=user.id,
        equipment_id=equip_id,
        damaged=True,
        damage_description="Cracked windshield",
    )
    equip = db.get_equipment_by_id(equip_id)
    assert equip.damaged is True
    assert equip.checked_out is False

def test_delete_user_equipment_not_checked_out(login_admin):
    db = login_admin.application.db
    user = db.get_user_by_email("user@gmail.com")
    equip_id = ObjectId("000000000000000000000001")  # Tractor 1 (available)
    result = db.delete_user_equipment(user_id=user.id, equipment_id=equip_id)
    assert "not checked out" in str(result)

def test_set_equipment_checked_out(login_admin):
    db = login_admin.application.db
    equip_id = ObjectId("000000000000000000000001")  # Tractor 1 (available)
    db.set_equipment_checked_out(id=equip_id, checked_out=True)
    updated = db.get_equipment_by_id(equip_id)
    assert updated.checked_out is True

def test_request_equipment_endpoint(login_user):
    # User requests to check out an available equipment item
    res = login_user.post(
        "/request_equipment",
        json={
            "equip_id": "000000000000000000000001",  # Tractor 1
            "equip_name": "Tractor 1",
        },
    )
    assert res.get_json()["result"] is True

def test_request_equipment_already_checked_out(login_user):
    # Cannot request equipment that is already checked out
    res = login_user.post(
        "/request_equipment",
        json={
            "equip_id": "000000000000000000000002",  # Tractor 2 (checked out)
            "equip_name": "Tractor 2",
        },
    )
    assert res.get_json()["result"] is False

def test_request_equipment_unavailable(login_user):
    # Cannot request equipment that is marked unavailable
    res = login_user.post(
        "/request_equipment",
        json={
            "equip_id": "000000000000000000000004",  # Truck 1 (unavailable)
            "equip_name": "Truck 1",
        },
    )
    assert res.get_json()["result"] is False

def test_return_equipment_endpoint(login_user):
    db = login_user.application.db
    res = login_user.post(
        "/return_equipment",
        json={
            "equipment_id": "000000000000000000000002",  # Tractor 2 (checked out to user)
            "damaged": False,
            "damage_description": "",
        },
    )
    assert res.get_json()["result"] is True
    equip = db.get_equipment_by_id(ObjectId("000000000000000000000002"))
    assert equip.checked_out is False

def test_return_equipment_damaged(login_user):
    db = login_user.application.db
    res = login_user.post(
        "/return_equipment",
        json={
            "equipment_id": "000000000000000000000002",
            "damaged": True,
            "damage_description": "Broken axle",
        },
    )
    assert res.get_json()["result"] is True
    equip = db.get_equipment_by_id(ObjectId("000000000000000000000002"))
    assert equip.damaged is True

### Find user by equipment -----------------------------------------

def test_find_user_checked_out(login_user):
    # Find which user has an equipment item checked out to them
    db = login_user.application.db
    all_equip = db.get_all_equipment()
    equip_id = all_equip[2].id  # Tractor 2
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
        "phone": "1234567890",
    })
    user = db.get_user_by_equipment(equip_id)
    assert user is not None
    assert equip_id in user.checked_out_equipment

def test_no_user_for_available_equipment(login_user):
    # Ensure that available equipment aren't marked as checked out to a user
    db = login_user.application.db
    all_equip = db.get_all_equipment()
    equip_id = all_equip[1].id  # Tractor 1
    assert db.get_user_by_equipment(equip_id) is None

### Canceling pending requests -----------------------------------------

def test_cancel_pending(login_user):
    # Cancel pending request when the equipment becomes unavailable
    db = login_user.application.db
    all_equip = db.get_all_equipment()
    equip_id = all_equip[1].id  # Tractor 1
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
        "phone": "1234567890",
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
        "status": "p",  # Pending
    })
    count = db.cancel_pending_requests_for_equipment([equip_id])
    assert count == 1
    # Ensure that when the request is cancelled, the notif is rejected ('r')
    assert db.notifications_db.find_one({"_id": notif_id})["status"] == "r"

def test_does_not_cancel_approved(login_user):
    # Ensure that approved equipment requests aren't canceled
    db = login_user.application.db
    all_equip = db.get_all_equipment()
    equip_id = all_equip[1].id  # Tractor 1
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
        "phone": "1234567890",
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
        "status": "a",  # Already approved
    })
    count = db.cancel_pending_requests_for_equipment([equip_id])
    assert count == 0
    assert db.notifications_db.find_one({"_id": notif_id})["status"] == "a"

### Add / edit / delete equipment (admin) -----------------------------------------

def test_add_equipment_endpoint(login_admin):
    res = login_admin.post(
        "/add_equipment",
        json={
            "data": {
                "name": "Endpoint Tractor",
                "class": "Tractor",
                "year": 2024,
                "farm": "Aroostook",
                "model": "Z200",
                "make": "Kubota",
                "use": "Farming",
                "description": "Added via endpoint",
                "damaged": False,
                "unavailable": False,
                "replacement_cost": 60000,
            }
        },
    )
    assert res.get_json()["result"] is True

def test_add_equipment_not_admin(login_user):
    res = login_user.post(
        "/add_equipment",
        json={"data": {"name": "Sneaky Tractor", "class": "Tractor"}},
    )
    assert res.status_code in (403, 200)
    if res.status_code == 200:
        assert res.get_json()["result"] is False

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
                "damaged": False,
            }
        },
    )
    assert res.get_json()["result"]

def test_equipment_editing_fail(login_admin):
    # Extra keys not in the allowed_fields set should be rejected
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

def test_change_equipment_info_not_admin(login_user):
    # Regular users cannot edit equipment fields
    res = login_user.post(
        "/change_equipment_info",
        json={
            "equipment": {
                "id": "000000000000000000000001",
                "name": "Hacked Name",
                "class": "Tractor",
                "year": 2020,
                "farm": "Aroostook",
                "model": "5075E",
                "make": "John Deere",
                "use": "Farming",
                "images": [],
                "reports": [],
                "checked_out": False,
                "unavailable": False,
                "description": "Test",
                "damaged": False,
            }
        },
    )
    assert res.status_code in (403, 200)
    if res.status_code == 200:
        assert res.get_json()["result"] is False

def test_update_equipment_field_valid(login_admin):
    db = login_admin.application.db
    equip_id = ObjectId("000000000000000000000001")
    result = db.update_equipment_field(equip_id, "name", "Tractor One Updated")
    assert result is True
    updated = db.get_equipment_by_id(equip_id)
    assert updated.name == "Tractor One Updated"

def test_update_equipment_field_invalid(login_admin):
    # Fields not in the allowed set should raise an exception
    db = login_admin.application.db
    equip_id = ObjectId("000000000000000000000001")
    with pytest.raises(Exception):
        db.update_equipment_field(equip_id, "secret_field", "bad_value")

def test_delete_equipment_admin(login_admin):
    res = login_admin.post(
        "/delete_equipment",
        json={"equipment_id": "000000000000000000000001"},  # Tractor 1
    )
    assert res.get_json()["result"] is True

def test_delete_equipment_not_found(login_admin):
    fake_id = str(ObjectId())
    res = login_admin.post("/delete_equipment", json={"equipment_id": fake_id})
    assert res.status_code == 404
    assert res.get_json()["result"] is False

def test_delete_checked_out_equipment_blocked(login_admin):
    # Checked out equipment must not be deleted
    res = login_admin.post(
        "/delete_equipment",
        json={"equipment_id": "000000000000000000000002"},  # Tractor 2 (checked out)
    )
    assert res.status_code == 400
    assert res.get_json()["result"] is False

def test_delete_equipment_not_admin(login_user):
    res = login_user.post(
        "/delete_equipment",
        json={"equipment_id": "000000000000000000000001"},
    )
    assert res.status_code in (403, 200)
    if res.status_code == 200:
        assert res.get_json()["result"] is False

def test_db_delete_equipment(login_admin):
    # Test the DB-layer delete directly
    db = login_admin.application.db
    equip = Equipment()
    equip.fill_from_json({
        "_id": ObjectId(),
        "name": "Temp Equipment",
        "class": "Tractor",
        "year": 2022,
        "farm": "TestFarm",
        "model": "T1",
        "make": "Brand",
        "use": "Farming",
        "images": [],
        "reports": [],
        "checked_out": False,
        "description": "Temporary",
        "damaged": False,
        "unavailable": False,
        "replacement_cost": 1000,
    })
    db.add_equipment(equip)
    result = db.delete_equipment(equip.id)
    assert result is True
    assert db.get_equipment_by_id(equip.id) is None

def test_delete_equipment_not_found_db(login_admin):
    db = login_admin.application.db
    result = db.delete_equipment(ObjectId())
    assert result is False

### Bulk Equipment Upload -----------------------------------------

def make_bulk_xlsx():
    """Creates a minimal valid .xlsx file with the expected columns"""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Name", "Category", "Year", "Farm", "Model", "Make", "Use", "Replacement Cost", "Description", "X", "Y"])
    ws.append(["Bulk Tractor", "Tractor", 2022, "Aroostook", "X100", "Kubota", "Farming", 50000, "Bulk added", "", ""])
    ws.append(["Bulk Forklift", "Forklift", 2021, "Rogers", "Y200", "Yale", "Warehouse", 30000, "Also bulk", "", ""])
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf

def test_add_bulk_equipment(login_admin):
    xlsx = make_bulk_xlsx()
    res = login_admin.post(
        "/add_bulk_equipment",
        data={"file": (xlsx, "equipment.xlsx")},
        content_type="multipart/form-data",
    )
    assert res.get_json()["result"] is True
    db = login_admin.application.db
    names = [e.name for e in db.get_all_equipment()]
    assert "Bulk Tractor" in names
    assert "Bulk Forklift" in names

def test_add_bulk_equipment_wrong_file_type(login_admin):
    res = login_admin.post(
        "/add_bulk_equipment",
        data={"file": (io.BytesIO(b"not excel"), "data.csv")},
        content_type="multipart/form-data",
    )
    assert res.get_json()["result"] is False

def test_add_bulk_equipment_no_file(login_admin):
    res = login_admin.post(
        "/add_bulk_equipment",
        data={},
        content_type="multipart/form-data",
    )
    assert res.get_json()["result"] is False

def test_add_bulk_equipment_not_admin(login_user):
    xlsx = make_bulk_xlsx()
    res = login_user.post(
        "/add_bulk_equipment",
        data={"file": (xlsx, "equipment.xlsx")},
        content_type="multipart/form-data",
    )
    assert res.status_code in (403, 200)
    if res.status_code == 200:
        assert res.get_json()["result"] is False

def test_add_equipment_multipart_form(login_admin):
    # Covers the multipart/form-data branch of /add_equipment
    img_buf = io.BytesIO()
    Image.new("RGB", (10, 10)).save(img_buf, format="PNG")
    img_buf.seek(0)
    res = login_admin.post(
        "/add_equipment",
        data={
            "name": "Form Tractor",
            "class": "Tractor",
            "year": "2023",
            "farm": "Aroostook",
            "model": "Z100",
            "make": "Kubota",
            "use": "Farming",
            "description": "Added via form",
            "images": (img_buf, "tractor.png"),
        },
        content_type="multipart/form-data",
    )
    assert res.get_json()["result"] is True