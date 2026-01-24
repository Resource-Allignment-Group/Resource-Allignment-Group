import pytest


def test_user_information(login_user):
    res = login_user.get("/get_user_info")
    assert res.get_json()["result"]


def test_user_profile(login_user):
    res = login_user.get("/get_profile_info")
    assert res.get_json()["result"]


def test_user_equipment(login_user):
    res = login_user.get("/get_user_equipment")
    assert res.get_json()["result"]


def test_requests(login_user):
    res = login_user.get("/get_requests")
    assert res.get_json()["result"]


def test_notifications(login_user):
    res = login_user.get("/get_notifications")
    assert res.get_json()["result"]


def test_equipment(login_user):
    res = login_user.get("/get_equipment")
    assert res.get_json()["result"]


def test_dashboard_info(login_user):
    res = login_user.get("/get_dashboard_info")
    assert res.get_json()["result"]


def test_profile_info(login_user):
    res = login_user.get("/get_profile_info")
    assert res.get_json()["result"]
