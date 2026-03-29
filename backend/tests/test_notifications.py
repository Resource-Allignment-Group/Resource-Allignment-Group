from bson import ObjectId
from notifications import Notification
from unittest.mock import patch, MagicMock

# Tests for notification-related DatabaseManager methods and routes

### Helpers -----------------------------------------

def make_notification(sender_id, receiver_id, body="Test notification", notif_type="i"):
    """Helper to build a Notification object for use in tests"""
    note = Notification()
    note.sender = sender_id
    note.receiver = receiver_id
    note.body = body
    note.date = "2026-01-01"
    note.type = notif_type
    note.equipment_id = None
    note.read = False
    note.status = "p"
    return note

### send_notification / get_notifications_by_user -----------------------------------------

def test_send_and_get_notification(login_user):
    db = login_user.application.db
    user = db.get_user_by_email("user@gmail.com")
    admin = db.get_user_by_email("admin@gmail.com")

    note = make_notification(user.id, admin.id, body="Hello admin")
    result = db.send_notification(note)
    assert result["result"] is True

    inbox = db.get_notifications_by_user(str(admin.id))
    assert any(n.body == "Hello admin" for n in inbox)

def test_get_notifications_endpoint(login_user):
    res = login_user.get("/get_notifications")
    assert res.get_json()["result"]

def test_get_requests_endpoint(login_user):
    res = login_user.get("/get_requests")
    assert res.get_json()["result"]

### set_notification_read / set_notification_status -----------------------------------------

def test_set_notification_read(login_user):
    db = login_user.application.db
    user = db.get_user_by_email("user@gmail.com")
    notif_id = ObjectId()
    db.notifications_db.insert_one({
        "_id": notif_id,
        "sender": user.id,
        "receiver": user.id,
        "body": "Test",
        "date": "2026-01-01",
        "type": "i",
        "equipment_id": None,
        "read": False,
        "status": "p",
    })
    db.set_notification_read(id=notif_id, read=True)
    notif = db.notifications_db.find_one({"_id": notif_id})
    assert notif["read"] is True

def test_set_notification_status(login_user):
    db = login_user.application.db
    notif_id = ObjectId()
    db.notifications_db.insert_one({
        "_id": notif_id,
        "sender": ObjectId(),
        "receiver": ObjectId(),
        "body": "Test",
        "date": "2026-01-01",
        "type": "r",
        "equipment_id": None,
        "read": False,
        "status": "p",
    })
    db.set_notification_status(id=notif_id, status="a")
    notif = db.notifications_db.find_one({"_id": notif_id})
    assert notif["status"] == "a"

### get_unread_messages_by_user -----------------------------------------

def test_get_unread_messages_by_user(login_user):
    db = login_user.application.db
    user = db.get_user_by_email("user@gmail.com")

    note = make_notification(user.id, user.id, body="Unread message")
    db.send_notification(note)

    unread = db.get_unread_messages_by_user(user_id=user.id)
    assert len(unread) >= 1
    assert all(n.read is False for n in unread)

### delete_notification_completely -----------------------------------------

def test_delete_notification_completely(login_user):
    db = login_user.application.db
    user = db.get_user_by_email("user@gmail.com")

    note = make_notification(user.id, user.id, body="To be deleted")
    db.send_notification(note)

    db.delete_notification_completely(note_id=note.id)
    inbox = db.get_notifications_by_user(str(user.id))
    assert not any(n.body == "To be deleted" for n in inbox)

### remove_notifications_from_all_admin_inboxes -----------------------------------------

def test_remove_notifications_from_all_admin_inboxes(login_admin):
    db = login_admin.application.db
    user = db.get_user_by_email("user@gmail.com")
    admin = db.get_user_by_email("admin@gmail.com")

    note = make_notification(user.id, admin.id, body="Admin inbox test")
    db.send_notification(note)

    db.remove_notifications_from_all_admin_inboxes(notification_ids=[note.id])
    updated_admin = db.users_db.find_one({"_id": admin.id})
    assert note.id not in updated_admin.get("inbox", [])

### get_pending_request_info -----------------------------------------

def test_get_pending_request_info(login_user):
    db = login_user.application.db
    all_equip = db.get_all_equipment()
    equip_id = all_equip[1].id  # Tractor 1
    user = db.get_user_by_email("user@gmail.com")
    notif_id = ObjectId()
    db.notifications_db.insert_one({
        "_id": notif_id,
        "sender": user.id,
        "receiver": ObjectId(),
        "body": "Request",
        "date": "2026-01-01",
        "type": "r",
        "equipment_id": equip_id,
        "read": False,
        "status": "p",
    })
    notif_ids, sender_ids = db.get_pending_request_info([equip_id])
    assert notif_id in notif_ids
    assert user.id in sender_ids

def test_get_pending_request_info_exclude(login_user):
    # Excluded notification IDs should not appear in the result
    db = login_user.application.db
    all_equip = db.get_all_equipment()
    equip_id = all_equip[1].id
    user = db.get_user_by_email("user@gmail.com")
    notif_id = ObjectId()
    db.notifications_db.insert_one({
        "_id": notif_id,
        "sender": user.id,
        "receiver": ObjectId(),
        "body": "Request",
        "date": "2026-01-01",
        "type": "r",
        "equipment_id": equip_id,
        "read": False,
        "status": "p",
    })
    notif_ids, _ = db.get_pending_request_info(
        [equip_id], exclude_notification_id=notif_id
    )
    assert notif_id not in notif_ids

### dismiss_notification route -----------------------------------------

def test_dismiss_notification(login_user):
    db = login_user.application.db
    user = db.get_user_by_email("user@gmail.com")

    note = make_notification(user.id, user.id, body="Dismiss me")
    db.send_notification(note)

    res = login_user.post(
        "/dismiss_notification", json={"notification": {"id": str(note.id)}}
    )
    assert res.get_json()["result"] is True

    remaining = db.get_notifications_by_user(str(user.id))
    assert not any(n.body == "Dismiss me" for n in remaining)

def test_dismiss_notification_missing_id(login_user):
    # Should return False if no notification ID is provided
    res = login_user.post("/dismiss_notification", json={"notification": {}})
    assert res.get_json()["result"] is False

### Dashboard -----------------------------------------

def test_get_dashboard_info_db(login_admin):
    db = login_admin.application.db
    total, available, used, damaged, unavailable = db.get_dashboard_info()
    assert total == 5
    assert used == 1        # Tractor 2
    assert damaged == 1     # Forklift 1
    assert unavailable == 1 # Truck 1
    assert available == 2   # Tractor 1 + Testing Equipment

def test_get_dashboard_info_endpoint(login_admin):
    res = login_admin.get("/get_dashboard_info")
    assert res.get_json()["result"]

def test_get_dashboard_info_user_forbidden(login_user):
    # Regular users cannot access the admin dashboard
    res = login_user.get("/get_dashboard_info")
    data = res.get_json()
    assert data["result"] is False or res.status_code == 403

### update_report_preference -----------------------------------------

def test_update_report_preference_admin(login_admin):
    res = login_admin.post(
        "/update_report_preference", json={"receive_reports": True}
    )
    assert res.get_json()["result"] is True

def test_update_report_preference_user_forbidden(login_user):
    res = login_user.post(
        "/update_report_preference", json={"receive_reports": True}
    )
    assert res.status_code in (403, 200)
    if res.status_code == 200:
        assert res.get_json()["result"] is False

### Notification class -----------------------------------------

def test_notification_populate_from_json(client):
    notif_id = ObjectId()
    sender_id = ObjectId()
    receiver_id = ObjectId()
    data = {
        "_id": notif_id,
        "sender": sender_id,
        "receiver": receiver_id,
        "date": "2026-01-01",
        "body": "Test body",
        "type": "r",
        "equipment_id": None,
        "read": True,
        "status": "a",
    }
    note = Notification()
    note.populate_from_json(data)
    assert note.id == notif_id
    assert note.sender == sender_id
    assert note.body == "Test body"
    assert note.type == "r"
    assert note.read is True
    assert note.status == "a"

def test_notification_to_dict(client):
    note = Notification()
    note.populate_from_json({
        "_id": ObjectId(),
        "sender": ObjectId(),
        "receiver": ObjectId(),
        "date": "2026-01-01",
        "body": "Hello",
        "type": "i",
        "equipment_id": None,
        "read": False,
        "status": "p",
    })
    d = note.to_dict(sender_name="Jane Doe")
    assert d["sender_name"] == "Jane Doe"
    assert d["body"] == "Hello"
    assert d["type"] == "i"
    assert "read" in d

### Notification_Manager (email methods mocked) -----------------------------------------

def test_send_account_approval_message(login_admin):
    # send_account_approval_message should create a notification in each admin's inbox
    db = login_admin.application.db
    nm = login_admin.application.nm
    new_user = db.get_user_by_email("user@gmail.com")
    nm.send_account_approval_message(new_user=new_user)
    admin = db.get_user_by_email("admin@gmail.com")
    inbox = db.get_notifications_by_user(str(admin.id))
    assert any(n.type == "a" for n in inbox)

def test_send_equipment_request_notification(login_user):
    # send_equipment_request should create a notification in each admin's inbox
    db = login_user.application.db
    nm = login_user.application.nm
    user = db.get_user_by_email("user@gmail.com")
    equip_id = ObjectId("000000000000000000000001")
    result = nm.send_equipment_request(
        id=ObjectId(),
        sender=user,
        equip_name="Tractor 1",
        equipment_id=equip_id,
    )
    assert result is True
    admin = db.get_user_by_email("admin@gmail.com")
    inbox = db.get_notifications_by_user(str(admin.id))
    assert any(n.type == "r" for n in inbox)

def test_send_inform_notification(login_user):
    db = login_user.application.db
    nm = login_user.application.nm
    user = db.get_user_by_email("user@gmail.com")
    admin = db.get_user_by_email("admin@gmail.com")
    nm.send_inform_notification(sender=user, receiver=admin, message="Info note")
    inbox = db.get_notifications_by_user(str(admin.id))
    assert any(n.body == "Info note" for n in inbox)

@patch("notifications.smtplib.SMTP")
def test_send_email_calls_smtp(mock_smtp, client):
    nm = client.application.nm
    mock_server = MagicMock()
    mock_smtp.return_value = mock_server
    nm.send_email(message="Hi", receiver="test@example.com", subject="Test")
    assert mock_smtp.called
    assert mock_server.sendmail.called

@patch("notifications.smtplib.SMTP")
def test_send_forgot_password_email(mock_smtp, client, seed_db):
    nm = client.application.nm
    mock_server = MagicMock()
    mock_smtp.return_value = mock_server
    nm.send_forgot_password_email(email="user@gmail.com", link="http://reset.example.com")
    assert mock_server.sendmail.called

### Inbox and Requests -----------------------------------------

def test_account_decision_approve_equipment_request(login_admin):
    # Full approval flow: admin approves a checkout request
    db = login_admin.application.db
    admin = db.get_user_by_email("admin@gmail.com")
    user = db.get_user_by_email("user@gmail.com")
    equip_id = ObjectId("000000000000000000000001")  # Tractor 1 (available)

    notif_id = ObjectId()
    db.notifications_db.insert_one({
        "_id": notif_id,
        "sender": user.id,
        "receiver": admin.id,
        "body": "Request to checkout Tractor 1",
        "date": "2026-01-01",
        "type": "r",
        "equipment_id": equip_id,
        "read": False,
        "status": "p",
    })
    db.users_db.update_one({"_id": admin.id}, {"$push": {"inbox": notif_id}})

    res = login_admin.post("/admin_account_decision", json={
        "notification": {
            "id": str(notif_id), "_id": str(notif_id),
            "sender": str(user.id), "receiver": str(admin.id),
            "body": "Request to checkout Tractor 1",
            "date": "2026-01-01", "type": "r",
            "equipment_id": str(equip_id),
            "read": False, "status": "p",
        },
        "result": True,  # Approve
    })
    assert res.get_json()["result"] is True
    # Equipment should now be checked out
    assert db.get_equipment_by_id(equip_id).checked_out is True

def test_account_decision_deny_equipment_request(login_admin):
    db = login_admin.application.db
    admin = db.get_user_by_email("admin@gmail.com")
    user = db.get_user_by_email("user@gmail.com")
    equip_id = ObjectId("000000000000000000000001")

    notif_id = ObjectId()
    db.notifications_db.insert_one({
        "_id": notif_id,
        "sender": user.id,
        "receiver": admin.id,
        "body": "Request to checkout Tractor 1",
        "date": "2026-01-01",
        "type": "r",
        "equipment_id": equip_id,
        "read": False,
        "status": "p",
    })
    db.users_db.update_one({"_id": admin.id}, {"$push": {"inbox": notif_id}})

    res = login_admin.post("/admin_account_decision", json={
        "notification": {
            "id": str(notif_id), "_id": str(notif_id),
            "sender": str(user.id), "receiver": str(admin.id),
            "body": "Request to checkout Tractor 1",
            "date": "2026-01-01", "type": "r",
            "equipment_id": str(equip_id),
            "read": False, "status": "p",
        },
        "result": False,  # Deny
    })
    assert res.get_json()["result"] is True
    # Equipment should still be available
    assert db.get_equipment_by_id(equip_id).checked_out is False

def test_get_requests_with_data(login_user):
    # User has made a request — get_requests should return it with equipment info
    db = login_user.application.db
    user = db.get_user_by_email("user@gmail.com")
    admin = db.get_user_by_email("admin@gmail.com")
    equip_id = ObjectId("000000000000000000000001")

    notif_id = ObjectId()
    db.notifications_db.insert_one({
        "_id": notif_id,
        "sender": user.id,
        "receiver": admin.id,
        "body": "Request",
        "date": "2026-01-01",
        "type": "r",
        "equipment_id": equip_id,
        "read": False,
        "status": "p",
    })

    res = login_user.get("/get_requests")
    data = res.get_json()
    assert data["result"] is True
    assert len(data["notifications"]) == 1
    assert len(data["equipment"]) == 1

def test_get_inbox_by_user(login_user):
    db = login_user.application.db
    user = db.get_user_by_email("user@gmail.com")

    note = Notification()
    note.sender = user.id
    note.receiver = user.id
    note.body = "Inbox test"
    note.date = "2026-01-01"
    note.type = "i"
    note.equipment_id = None
    note.read = False
    note.status = "p"
    db.send_notification(note)

    inbox = db.get_inbox_by_user(user_id=user.id)
    assert len(inbox) >= 1

def test_get_inbox_by_user_empty(login_user):
    db = login_user.application.db
    # User with no inbox
    result = db.get_inbox_by_user(user_id=ObjectId())
    assert result == []

def test_get_notifications_with_equipment_request(login_user):
    # Covers the branch where a notification of type 'r' enriches with equipment image info
    db = login_user.application.db
    user = db.get_user_by_email("user@gmail.com")
    equip_id = ObjectId("000000000000000000000001")

    notif_id = ObjectId()
    db.notifications_db.insert_one({
        "_id": notif_id,
        "sender": user.id,
        "receiver": user.id,
        "body": "Request",
        "date": "2026-01-01",
        "type": "r",
        "equipment_id": equip_id,
        "read": False,
        "status": "p",
    })
    db.users_db.update_one({"_id": user.id}, {"$push": {"inbox": notif_id}})

    res = login_user.get("/get_notifications")
    assert res.get_json()["result"] is True