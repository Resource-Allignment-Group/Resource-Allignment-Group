import pytest

def test_register(client):
    res = client.post(
        "/register",
        json={
            "email": "user@gmail.com",
            "password": "test_pass",
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
            "password": "test_pass",
            "fname": "Joe",
            "lname": "Smith",
            "phone": "3333333333",
        },
    )
    #TODO: Impliment that the responded message says one already exists
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

