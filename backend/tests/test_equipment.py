import pytest


def test_request_equipment(login_user):
    equipment_res = login_user.post(
        "/request_equipment",
        json={
            "equip_id": "000000000000000000000000",
            "equip_name": "test_equip",
        },
    )
    assert equipment_res.get_json()["result"]

    admin_decision_res = login_user.post(
        "/admin_account_decision",
        json={
            "result": True,
            "notification": login_user.application.db.get_notifications_by_equipment(
                equip_id="000000000000000000000000"
            ).to_dict(sender_name="test_sender_name"),
        },
    )

    assert admin_decision_res.get_json()["result"]

    return_res = login_user.post(
        "/return_equipment", json={"equipment_id": "000000000000000000000000"}
    )
    assert return_res.get_json()["result"]
