# import pytest
# from main import create_app
# from database import DatabaseManager
# from bson.objectid import ObjectId


# def test_all_user_endpoints(client):
#     db = DatabaseManager(testing=True)

#     # fetch user
#     user = db.get_user_by_email("pytest@gmail.com")
#     assert user is not None


#     # authenticate
#     auth_response = client.post(
#         "/authenticate", json={"email": "pytest@gmail.com", "password": "test_pass"}
#     )
#     print(
#         "Authenticate Endpoint:",
#         auth_response.status_code,
#         auth_response.get_json(),
#         "\n",
#     )
#     assert auth_response.status_code == 200 and auth_response.get_json()["result"]

#     # get requests
#     user_info_response = client.get("/get_user_info")
#     print(
#         "User Info Endpoint:",
#         user_info_response.status_code,
#         user_info_response.get_json(),
#         "\n",
#     )
#     assert (
#         user_info_response.status_code == 200
#         and user_info_response.get_json()["result"]
#     )

#     user_equipment_response = client.get("/get_user_equipment")
#     print(
#         "User Equipment Endpoint:",
#         user_equipment_response.status_code,
#         user_equipment_response.get_json(),
#         "\n",
#     )
#     assert (
#         user_equipment_response.status_code == 200
#         and user_equipment_response.get_json()["result"]
#     )

#     requests_response = client.get("/get_requests")
#     print(
#         "Requests Endpoint:",
#         requests_response.status_code,
#         requests_response.get_json(),
#         "\n",
#     )
#     assert (
#         requests_response.status_code == 200 and requests_response.get_json()["result"]
#     )

#     notifications_response = client.get("/get_notifications")
#     print(
#         "Notifications Endpoint:",
#         notifications_response.status_code,
#         notifications_response.get_json(),
#         "\n",
#     )
#     assert (
#         notifications_response.status_code == 200
#         and notifications_response.get_json()["result"]
#     )

#     equipment_response = client.get("/get_equipment")
#     print(
#         "Get Equipment Endpoint:",
#         equipment_response.status_code,
#         equipment_response.get_json(),
#         "\n",
#     )
#     assert (
#         equipment_response.status_code == 200
#         and equipment_response.get_json()["result"]
#     )

#     dashboard_response = client.get("/get_dashboard_info")
#     print(
#         "Dashboard Endpoint:",
#         dashboard_response.status_code,
#         dashboard_response.get_json(),
#         "\n",
#     )
#     assert (
#         dashboard_response.status_code == 200
#         and dashboard_response.get_json()["result"]
#     )

#     profile_response = client.get("/get_profile_info")
#     print(
#         "Profile Info Endpoint:",
#         profile_response.status_code,
#         profile_response.get_json(),
#         "\n",
#     )
#     assert profile_response.status_code == 200 and profile_response.get_json()["result"]

#     # request equipment
#     equipment_request_response = client.post(
#         "/request_equipment",
#         json={
#             "equip_id": "000000000000000000000000",
#             "equip_name": "test_equip",
#         },
#     )
#     print(
#         "Equipment Request Endpoint:",
#         equipment_request_response.status_code,
#         equipment_request_response.get_json(),
#         "\n",
#     )
#     assert (
#         equipment_request_response.status_code == 200
#         and equipment_request_response.get_json()["result"]
#     )

#     # accept request
#     admin_decision_response = client.post(
#         "/admin_account_decision",
#         json={
#             "result": True,
#             "notification": db.get_notifications_by_equipment(
#                 equip_id="000000000000000000000000"
#             ).to_dict(sender_name="test_sender_name"),
#         },
#     )
#     print(
#         "Admin Equipment Aproval Endpoint:",
#         admin_decision_response.status_code,
#         admin_decision_response.get_json(),
#         "\n",
#     )
#     assert (
#         admin_decision_response.status_code == 200
#         and admin_decision_response.get_json()["result"]
#     )

#     # return equipment
#     return_response = client.post(
#         "/return_equipment", json={"equipment_id": "000000000000000000000000"}
#     )
#     print(
#         "Equipment Return Endpoint:",
#         return_response.status_code,
#         return_response.get_json(),
#         "\n",
#     )

#     # TODO: Tests that still need to be written
#     # - Add Equipment
#     # - Delete Equipement

#     # delete new user
#     delete_account_response = client.post(
#         "/delete_user_account",
#         json={"user": db.get_user_by_email("pytest@gmail.com").to_dict()},
#     )
#     print(
#         "Equipment Return Endpoint:",
#         delete_account_response.status_code,
#         delete_account_response.get_json(),
#         "\n",
#     )
#     assert (
#         delete_account_response.status_code == 200
#         and delete_account_response.get_json()["result"]
#     )

#     db.notifications_db.delete_many({})
