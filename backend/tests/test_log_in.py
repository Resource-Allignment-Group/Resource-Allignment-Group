import pytest
from flask import session
from bson.objectid import ObjectId

# Tests related to user registration, authentication, deletion

def test_register(client):
    with client.session_transaction() as sess:
        sess['id'] = str(ObjectId())
    res = client.post(
        "/register",
        json={
            "email": "user@gmail.com",
            "password": "test_Pass2",
            "fname": "Joe",
            "lname": "Smith",
            "phone": "3333333333",
        },
    )
    assert res.get_json()["result"]

    res = client.post(
        "/register",
        json={
            "email": "user@gmail.com",
            "password": "test_Pass2",
            "fname": "Joe",
            "lname": "Smith",
            "phone": "3333333333",
        },
    )
    # TODO: Impliment that the responded message says one already exists
    assert not res.get_json()["result"] and res.get_json()["message"]


def test_authentication(client, seed_db):
    res = client.post(
        "/authenticate", json={"email": "user@gmail.com", "password": "test_pass"}
    )
    assert res.get_json()["result"]

    res = client.post(
        "/authenticate", json={"email": "notuser@gmail.com", "password": "test_pass"}
    )
    assert not res.get_json()["result"]

    res = client.post(
        "/authenticate", json={"email": "user@gmail.com", "password": "not_test_pass"}
    )
    assert not res.get_json()["result"]


# TODO: Test trying to do this with users instead of admin
def test_delete_user(login_admin):
    delete_account_res = login_admin.post(
        "/delete_user_account",
        json={"user": login_admin.application.db.get_user_by_email("user@gmail.com").to_dict()},
    )
    assert delete_account_res.get_json()["result"]
