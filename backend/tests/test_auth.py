import hashlib
from unittest.mock import patch
from helpers import hash_password
from bson.objectid import ObjectId
from main import create_app

# Tests related to user registration, authentication, sessions, and account management

### Registration -----------------------------------------

def test_register_success(client):
    with client.session_transaction() as sess:
        sess["id"] = str(ObjectId())
    res = client.post(
        "/register",
        json={
            "email": "user@gmail.com",
            "password": "test_Pass2!",
            "fname": "Joe",
            "lname": "Smith",
            "phone": "3333333333",
        },
    )
    assert res.get_json()["result"]

def test_register_duplicate_email(client):
    # Register once
    client.post(
        "/register",
        json={
            "email": "user@gmail.com",
            "password": "test_Pass2!",
            "fname": "Joe",
            "lname": "Smith",
            "phone": "3333333333",
        },
    )
    # Try to register again with the same email
    res = client.post(
        "/register",
        json={
            "email": "user@gmail.com",
            "password": "test_Pass2!",
            "fname": "Joe",
            "lname": "Smith",
            "phone": "3333333333",
        },
    )
    assert not res.get_json()["result"] and res.get_json()["message"]

def test_register_missing_name(client):
    res = client.post(
        "/register",
        json={
            "email": "test@example.com",
            "password": "Test_Pass1!",
            "fname": "",
            "lname": "",
            "phone": "2223334444",
        },
    )
    assert res.status_code == 400
    assert not res.get_json()["result"]

def test_register_invalid_email(client):
    res = client.post(
        "/register",
        json={
            "email": "not-an-email",
            "password": "Test_Pass1!",
            "fname": "John",
            "lname": "Doe",
            "phone": "2223334444",
        },
    )
    assert res.status_code == 400
    assert not res.get_json()["result"]

def test_register_invalid_phone(client):
    res = client.post(
        "/register",
        json={
            "email": "john@example.com",
            "password": "Test_Pass1!",
            "fname": "John",
            "lname": "Doe",
            "phone": "123",  # Too short
        },
    )
    assert res.status_code == 400
    assert not res.get_json()["result"]

def test_register_weak_password(client):
    res = client.post(
        "/register",
        json={
            "email": "john@example.com",
            "password": "password",  # No uppercase, digit, or special char
            "fname": "John",
            "lname": "Doe",
            "phone": "2223334444",
        },
    )
    assert res.status_code == 400
    assert not res.get_json()["result"]

### Authentication -----------------------------------------

def test_authentication_success(client, seed_db):
    res = client.post(
        "/authenticate", json={"email": "user@gmail.com", "password": "test_pass"}
    )
    assert res.get_json()["result"]

def test_authentication_wrong_email(client, seed_db):
    res = client.post(
        "/authenticate", json={"email": "notuser@gmail.com", "password": "test_pass"}
    )
    assert not res.get_json()["result"]

def test_authentication_wrong_password(client, seed_db):
    res = client.post(
        "/authenticate", json={"email": "user@gmail.com", "password": "not_test_pass"}
    )
    assert not res.get_json()["result"]

def test_login_pending_user_blocked(client):
    # Pending users (role='p') should not be granted access
    client.post(
        "/register",
        json={
            "email": "pending@example.com",
            "password": "Test_Pass1!",
            "fname": "Pend",
            "lname": "User",
            "phone": "2223334444",
        },
    )
    res = client.post(
        "/authenticate",
        json={"email": "pending@example.com", "password": "Test_Pass1!"},
    )
    data = res.get_json()
    assert data["result"] is False
    assert "pending" in data["message"].lower()

### Session -----------------------------------------

def test_check_session_logged_in(login_user):
    res = login_user.get("/check-session")
    data = res.get_json()
    assert data["result"] is True
    assert data["user"] == "user@gmail.com"

def test_check_session_not_logged_in(client):
    res = client.get("/check-session")
    data = res.get_json()
    assert data["result"] is False
    assert data["user"] is None

def test_logout(login_user):
    res = login_user.post("/logout")
    assert res.get_json()["result"] is True
    # Session should be cleared — check-session should now return False
    res2 = login_user.get("/check-session")
    assert res2.get_json()["result"] is False

### Account management (admin) -----------------------------------------

def test_delete_user_account_admin(login_admin):
    res = login_admin.post(
        "/delete_user_account",
        json={
            "user": login_admin.application.db.get_user_by_email(
                "user@gmail.com"
            ).to_dict()
        },
    )
    assert res.get_json()["result"]

def test_delete_user_account_not_admin(login_user):
    # Regular users should not be able to delete accounts
    db = login_user.application.db
    user = db.get_user_by_email("user@gmail.com")
    res = login_user.post("/delete_user_account", json={"user": user.to_dict()})
    data = res.get_json()
    assert data["result"] is False or res.status_code in (403, 401)

def test_change_user_role_admin(login_admin):
    db = login_admin.application.db
    user = db.get_user_by_email("user@gmail.com")
    res = login_admin.post(
        "/change_user_role",
        json={"user": {"id": str(user.id)}, "new_role": "s"},
    )
    assert res.get_json()["result"] is True
    updated = db.get_user_by_id(user.id)
    assert updated.role == "s"

def test_change_user_role_not_admin(login_user):
    db = login_user.application.db
    user = db.get_user_by_email("user@gmail.com")
    res = login_user.post(
        "/change_user_role",
        json={"user": {"id": str(user.id)}, "new_role": "a"},
    )
    assert res.status_code in (403, 200)
    if res.status_code == 200:
        assert res.get_json()["result"] is False

def test_get_users_admin(login_admin):
    res = login_admin.get("/get_users")
    data = res.get_json()
    assert data["result"] is True
    assert len(data["users"]) == 2  # User + Admin from seed

def test_get_users_not_admin(login_user):
    res = login_user.get("/get_users")
    assert res.status_code in (403, 200)
    if res.status_code == 200:
        assert res.get_json()["result"] is False

### Admin account decisions -----------------------------------------

def test_account_decision_approve_user(login_admin):
    # Admin approving a pending account should change role to 'u'
    db = login_admin.application.db
    admin = db.get_user_by_email("admin@gmail.com")

    pending_id = ObjectId()
    db.users_db.insert_one({
        "_id": pending_id,
        "email": "pending2@example.com",
        "password": "pw",
        "role": "p",
        "checked_out_equipment": [],
        "inbox": [],
        "position": None,
        "name": "Pending User",
        "phone": "1234567890",
    })
    notif_id = ObjectId()
    db.notifications_db.insert_one({
        "_id": notif_id,
        "sender": pending_id,
        "receiver": admin.id,
        "body": "Account request",
        "date": "2026-01-01",
        "type": "a",
        "equipment_id": None,
        "read": False,
        "status": "p",
    })
    db.users_db.update_one({"_id": admin.id}, {"$push": {"inbox": notif_id}})

    res = login_admin.post(
        "/admin_account_decision",
        json={
            "notification": {
                "id": str(notif_id),
                "_id": str(notif_id),
                "sender": str(pending_id),
                "receiver": str(admin.id),
                "body": "Account request",
                "date": "2026-01-01",
                "type": "a",
                "equipment_id": None,
                "read": False,
                "status": "p",
            },
            "result": True,  # Approve
        },
    )
    assert res.get_json()["result"] is True
    updated_user = db.users_db.find_one({"_id": pending_id})
    assert updated_user["role"] == "u"

def test_account_decision_deny_user(login_admin):
    # Admin denying a pending account should remove the user
    db = login_admin.application.db
    admin = db.get_user_by_email("admin@gmail.com")

    pending_id = ObjectId()
    db.users_db.insert_one({
        "_id": pending_id,
        "email": "denied@example.com",
        "password": "pw",
        "role": "p",
        "checked_out_equipment": [],
        "inbox": [],
        "position": None,
        "name": "Denied User",
        "phone": "1234567890",
    })
    notif_id = ObjectId()
    db.notifications_db.insert_one({
        "_id": notif_id,
        "sender": pending_id,
        "receiver": admin.id,
        "body": "Account request",
        "date": "2026-01-01",
        "type": "a",
        "equipment_id": None,
        "read": False,
        "status": "p",
    })
    db.users_db.update_one({"_id": admin.id}, {"$push": {"inbox": notif_id}})

    res = login_admin.post(
        "/admin_account_decision",
        json={
            "notification": {
                "id": str(notif_id),
                "_id": str(notif_id),
                "sender": str(pending_id),
                "receiver": str(admin.id),
                "body": "Account request",
                "date": "2026-01-01",
                "type": "a",
                "equipment_id": None,
                "read": False,
                "status": "p",
            },
            "result": False,  # Deny
        },
    )
    assert res.get_json()["result"] is True
    # User should be deleted
    assert db.users_db.find_one({"_id": pending_id}) is None

def test_account_decision_not_admin(login_user):
    # Non-admins should not be able to make account decisions
    res = login_user.post(
        "/admin_account_decision",
        json={
            "notification": {"id": str(ObjectId()), "type": "a"},
            "result": True,
        },
    )
    assert res.status_code in (401, 403)

### Forgot Password Actions -----------------------------------------

def test_forgot_password_valid_email(client, seed_db):
    with patch("main.Notification_Manager.send_forgot_password_email"):
        res = client.post("/forgot_password", json={"email": "user@gmail.com"})
    assert res.get_json()["result"] is True

def test_forgot_password_invalid_email(client, seed_db):
    res = client.post("/forgot_password", json={"email": "nobody@gmail.com"})
    assert res.get_json()["result"] is False
    assert "doesn't exist" in res.get_json()["message"]

def test_reset_password_valid_token(client, seed_db):
    db = client.application.db
    user = db.get_user_by_email("user@gmail.com")
    token = "valid_test_token"
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    db.create_password_reset(user_id=user.id, token=token, token_hash=token_hash)
    res = client.post("/reset_password", json={"token": token, "password": "NewPass1!"})
    assert res.get_json()["result"] is True

def test_reset_password_invalid_token(client, seed_db):
    res = client.post("/reset_password", json={"token": "faketoken", "password": "NewPass1!"})
    assert res.get_json()["result"] is False
    assert "Invalid" in res.get_json()["message"]

def test_session_cleared_when_user_deleted(client, seed_db):
    # Log in as the regular user
    client.post("/authenticate", json={"email": "user@gmail.com", "password": "test_pass"})
    # Verify they're logged in
    assert client.get("/check-session").get_json()["result"] is True
    # Delete the user directly from the DB
    db = client.application.db
    user = db.get_user_by_email("user@gmail.com")
    db.users_db.delete_one({"_id": user.id})
    # Next request should trigger the before_request hook and return 401
    res = client.get("/get_user_info")
    assert res.status_code == 401