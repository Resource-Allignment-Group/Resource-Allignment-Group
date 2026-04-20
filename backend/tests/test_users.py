import pytest
from bson import ObjectId
import hashlib
from helpers import generate_reset_token, hash_password, check_password
from user import User

# Tests for user-related DatabaseManager methods and profile routes

### User retrieval -----------------------------------------

def test_get_user_by_email(login_user):
    db = login_user.application.db
    user = db.get_user_by_email("user@gmail.com")
    assert user is not None
    assert user.email == "user@gmail.com"

def test_get_user_by_email_not_found(login_user):
    db = login_user.application.db
    with pytest.raises(Exception):
        db.get_user_by_email("doesnotexist@gmail.com")

def test_get_user_by_id(login_user):
    db = login_user.application.db
    user = db.get_user_by_email("user@gmail.com")
    fetched = db.get_user_by_id(user.id)
    assert fetched.id == user.id

def test_get_all_users(login_admin):
    db = login_admin.application.db
    users = db.get_all_users()
    # Seed inserts one user and one admin
    assert len(users) == 2

def test_get_administrators(login_admin):
    db = login_admin.application.db
    admins = db.get_administrators()
    assert all(a.role == "a" for a in admins)
    assert len(admins) == 1

def test_get_password_by_email(login_user):
    db = login_user.application.db
    pwd = db.get_password_by_email("user@gmail.com")
    assert pwd is not None

### add_user -----------------------------------------

def test_add_user_success(client):
    db = client.application.db
    result = db.add_user(
        fname="Alice",
        lname="Smith",
        phone="2223334444",
        email="alice@example.com",
        password="hashed_pw",
    )
    assert result["result"] is True
    user = db.get_user_by_email("alice@example.com")
    assert user.name == "Alice Smith"

def test_add_user_duplicate_email(client, seed_db):
    db = client.application.db
    result = db.add_user(
        fname="Dup",
        lname="User",
        phone="0000000000",
        email="user@gmail.com",  # Already seeded
        password="some_pw",
    )
    assert result["result"] is False
    assert "already exists" in result["message"]

### delete_user -----------------------------------------

def test_db_delete_user(login_admin):
    db = login_admin.application.db
    user = db.get_user_by_email("user@gmail.com")
    success = db.delete_user(user=user, admin_name="Admin")
    assert success is True
    with pytest.raises(Exception):
        db.get_user_by_email("user@gmail.com")

def test_delete_user_clears_checked_out_equipment(login_admin):
    # Deleting a user who has equipment checked out should mark that equipment as available
    db = login_admin.application.db
    user = db.get_user_by_email("user@gmail.com")
    # Seeded user has Tractor 2 (000000000000000000000002) checked out
    db.delete_user(user=user, admin_name="Admin")
    equip = db.get_equipment_by_id(ObjectId("000000000000000000000002"))
    assert equip.checked_out is False

### User setters -----------------------------------------

def test_set_user_role(login_admin):
    db = login_admin.application.db
    user = db.get_user_by_email("user@gmail.com")
    db.set_user_role(id=user.id, role="a")
    updated = db.get_user_by_id(user.id)
    assert updated.role == "a"

def test_set_user_name(login_user):
    db = login_user.application.db
    user = db.get_user_by_email("user@gmail.com")
    db.set_user_name(id=user.id, new_name="Jane Doe")
    updated = db.get_user_by_id(user.id)
    assert updated.name == "Jane Doe"

def test_set_user_email(login_user):
    db = login_user.application.db
    user = db.get_user_by_email("user@gmail.com")
    db.set_user_email(id=user.id, new_email="newemail@gmail.com")
    updated = db.get_user_by_id(user.id)
    assert updated.email == "newemail@gmail.com"

def test_set_user_phone(login_user):
    db = login_user.application.db
    user = db.get_user_by_email("user@gmail.com")
    db.set_user_phone(id=user.id, new_phone="5555555555")
    updated = db.get_user_by_id(user.id)
    assert updated.phone == "5555555555"

def test_set_user_position(login_user):
    db = login_user.application.db
    user = db.get_user_by_email("user@gmail.com")
    db.set_user_position(id=user.id, new_position="Researcher")
    updated = db.get_user_by_id(user.id)
    assert updated.position == "Researcher"

def test_update_admin_report_preference(login_admin):
    db = login_admin.application.db
    admin = db.get_user_by_email("admin@gmail.com")
    result = db.update_admin_report_preference(admin_id=admin.id, action=True)
    assert result is True
    updated = db.users_db.find_one({"_id": admin.id})
    assert updated["receive_reports"] is True

def test_set_user_password(login_user):
    db = login_user.application.db
    user = db.get_user_by_email("user@gmail.com")
    new_hash = hash_password("BrandNew1!")
    db.set_user_password(id=user.id, password=new_hash)
    stored = db.get_password_by_email("user@gmail.com")
    assert check_password("BrandNew1!", stored)

def test_get_email_by_id(login_user):
    db = login_user.application.db
    user = db.get_user_by_email("user@gmail.com")
    email = db.get_email_by_id(str(user.id))
    assert email == "user@gmail.com"

def test_get_email_by_id_deleted_user(login_user):
    db = login_user.application.db
    result = db.get_email_by_id(str(ObjectId()))
    assert result == "Deleted User"

def test_fill_user_information_none(client):
    user = User()
    user.fill_user_information(None)
    assert user.id is None
    assert user.email is None

### Profile routes -----------------------------------------

def test_get_user_info_endpoint(login_user):
    res = login_user.get("/get_user_info")
    assert res.get_json()["result"]

def test_get_profile_info_endpoint(login_user):
    res = login_user.get("/get_profile_info")
    assert res.get_json()["result"]

def test_save_new_profile_info(login_user):
    res = login_user.post(
        "/save_new_profile_info",
        json={
            "fname": "Updated",
            "lname": "Name",
            "email": "user@gmail.com",
            "phone": "9998887777",
            "position": "Technician",
            "department": "Engineering",
        },
    )
    assert res.get_json()["result"] is True

### Password reset -----------------------------------------

def test_create_and_get_password_reset(client, seed_db):
    db = client.application.db
    user = db.get_user_by_email("user@gmail.com")
    token = "test_token_abc"
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    db.create_password_reset(user_id=user.id, token=token, token_hash=token_hash)
    reset = db.get_password_reset(token_hash=token_hash)
    assert reset is not None
    assert reset["user_id"] == user.id
    assert reset["used"] is False

def test_set_password_reset_used(client, seed_db):
    db = client.application.db
    user = db.get_user_by_email("user@gmail.com")
    token = "test_token_xyz"
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    db.create_password_reset(user_id=user.id, token=token, token_hash=token_hash)
    reset = db.get_password_reset(token_hash=token_hash)
    result = db.set_password_reset_used(id=reset["_id"], used=True)
    assert result is True
    # Used tokens should not be returned by get_password_reset
    fetched = db.get_password_reset(token_hash=token_hash)
    assert fetched is None

### helpers.py -----------------------------------------

def test_hash_password_produces_valid_hash(client):
    hashed = hash_password("MyPassword1!")
    assert hashed != "MyPassword1!"
    assert isinstance(hashed, str)
    assert len(hashed) > 0

def test_check_password_correct(client):
    hashed = hash_password("MyPassword1!")
    assert check_password("MyPassword1!", hashed) is True

def test_check_password_incorrect(client):
    hashed = hash_password("MyPassword1!")
    assert check_password("WrongPassword!", hashed) is False

def test_generate_reset_token_returns_two_strings(client):
    token, token_hash = generate_reset_token()
    assert isinstance(token, str) and len(token) > 0
    assert isinstance(token_hash, str) and len(token_hash) == 64  # SHA-256 hex digest

def test_generate_reset_token_hash_matches(client):
    token, token_hash = generate_reset_token()
    assert hashlib.sha256(token.encode()).hexdigest() == token_hash

def test_generate_reset_token_unique(client):
    token1, _ = generate_reset_token()
    token2, _ = generate_reset_token()
    assert token1 != token2