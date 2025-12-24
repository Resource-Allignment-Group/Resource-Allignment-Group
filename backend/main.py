from flask import Flask, session, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv
from database import DatabaseManager
from helpers import *
from notifications import Notification_Manager, Notification
from bson.objectid import ObjectId

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")

CORS(app, supports_credentials=True, origins=["http://localhost:3000"])

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_COOKIE_SAMESITE"] = None


db = DatabaseManager()
nm = Notification_Manager(db=db)


@app.route("/authenticate", methods=["POST", "GET"])
def authenticate():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    user = db.get_user_by_username(username=username)
    if check_password(
        origional_password=password, hashed_password=user.password
    ):  # check with the the hashing algorithm
        if user.role == "p":
            return "Account is still pending approval from admin"
        else:
            session["user"] = username
            session["role"] = user.role
            session["id"] = str(user.id)  # Object ID can not be serialized
            return jsonify({"message": "success"})

    else:
        return jsonify({"message": "invalid credentials"})


@app.route("/check-session", methods=["GET"])
def check_session():
    user = session.get("user")  # Makes sure that the user is still logged in

    if user:
        return jsonify({"user": user})
    else:
        return jsonify({"user": None})


@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user", None)
    session.pop("role", None)
    session.pop("id", None)
    return jsonify({"message": "logged out"})


@app.route("/register", methods=["POST"])
def register():
    data = request.json
    email, password = data["email"], data["password"]
    hashed_password = hash_password(
        password=password
    )  # I belive this uses SHA256 but i would have to check
    result = db.add_user(email=email, password=hashed_password)

    if result["result"]:
        # send a notification to admin and update user management
        new_user = db.get_user_by_username(username=email)
        db.set_user_role(id=new_user.id, role="p")  #'p' stands for 'pending'
        nm.send_account_approval_message(new_user=new_user)
        return jsonify({"message": "success"})
    else:
        return jsonify({"message": result["message"]})


@app.route("/get_user_info", methods=["GET"])
def get_user_info():
    # add profile pic retrevial and any other import stuff here

    # This needs so re factoring once we get more features implimented
    inbox_notifications = db.get_inbox_by_user(user_id=ObjectId(session["id"]))
    unread_messages = db.get_unread_messages_by_user(user_id=ObjectId(session["id"]))
    return jsonify({"messages": [], "num_notifications": len(unread_messages)})


@app.route("/get_notifications", methods=["GET"])
def get_notifications():
    user_notifications = db.get_notifications_by_user(user_id=ObjectId(session["id"]))
    msgs = []
    for note in user_notifications:
        msgs.append(
            note.to_dict(db.get_username_by_id(user_id=str(note.sender)))
        )  # not the best way to do this, but once again, van not think of a better way
        if note.type == "i":
            # kind of a jerry-rigged way to see if the user has read the message but I can't really think of a better way without massive overhead in developments
            db.set_notification_read(id=note.id, read=True)

    return jsonify({"messages": msgs})


@app.route("/admin_account_decision", methods=["POST"])
def account_decision():
    data = request.json
    note_info = data["notification"]
    new_note = Notification()
    new_note.populate_from_json(json_info=note_info)

    match new_note.type:
        case "a":  # if it is an account creation notification, update the users role
            db.remove_notification_from_inbox(notification=new_note)
            db.set_notification_read(id=new_note.id, read=True)
            if data["result"]:
                result_message = f"{db.get_username_by_id(user_id=new_note.sender)} has been added to the system"
                db.set_user_role(id=ObjectId(new_note.sender), role="u")  # u for 'user'

            else:
                result_message = f"{db.get_username_by_id(user_id=new_note.sender)} has been rejected from the system"
                db.set_user_role(
                    id=ObjectId(new_note.sender), role="r"
                )  # r stand for 'rejected'

            for admin in db.get_administrators():
                nm.send_inform_notification(
                    sender=db.get_user_by_id(user_id=new_note.sender),
                    receiver=admin,
                    message=result_message,
                )  # might want to make the sender a "system" sender or something like that

            return jsonify({"result": 0})

        case "r":  # If the notification is a equipment request, update the equipment
            db.remove_notification_from_inbox(notification=new_note)
            db.set_notification_read(id=ObjectId(new_note.id), read=True)

            if data["result"]:
                equipment = db.get_equipment_by_id(id=new_note.equipment_id)
                db.add_user_equipment(
                    user_id=ObjectId(new_note.sender),
                    equipment_id=ObjectId(equipment.id),
                )
                db.set_equipment_checked_out(
                    id=ObjectId(new_note.equipment_id), checked_out=True
                )
                return jsonify({"result": True})
                # send notification to user that their equipment is theirs
            else:
                db.set_equipment_checked_out(id=new_note.id, checked_out=False)
                return jsonify({"result": True})


@app.route("/get_equipment", methods=["GET"])
def get_equipment():
    equipment_cur = db.get_all_equipment()
    equip_list = []
    for equip in equipment_cur:
        equip_list.append(equip.to_dict())
    return jsonify(equip_list)


@app.route("/request_equipment", methods=["POST"])
def request_equipment():
    data = request.json
    equip_id = data["equip_id"]

    note_result = nm.send_equipment_request(
        id=ObjectId(),
        sender=db.get_user_by_username(username=session["user"]),
        equip_name=data["equip_name"],
        equipment_id=ObjectId(equip_id),
    )
    if note_result:
        return jsonify({"success": True, "message": "this is the success message"})
    else:
        return jsonify({"success": True, "message": "this is the failure message"})


@app.route("/get_user_equipment", methods=["GET"])
def get_user_equipment():
    user_equipment = db.get_equipment_by_user(user_id=ObjectId(session["id"]))
    equip_list = []
    for equip in user_equipment:
        equip_list.append(equip.to_dict())

    return jsonify(equip_list)


@app.route("/return_equipment", methods=["POST"])
def return_equipment():
    data = request.json
    try:
        equipment = db.get_equipment_by_id(id=ObjectId(data["equipment_id"]))
        db.set_equipment_checked_out(id=equipment.id, checked_out=False)
        db.remove_equipment_from_inbox(
            equip_id=equipment.id, user_id=ObjectId(session["id"])
        )
        return jsonify({"result": True})
    except Exception as e:
        print(e)
        return jsonify({"result": False, "message": e})


@app.route("/get_requests", methods=["GET"])
def get_requests():
    notifications, equipment = db.get_requests_by_user(user_id=ObjectId(session["id"]))

    notifications_list, equipment_list = [], []

    for i, note in enumerate(notifications):
        notifications_list.append(
            note.to_dict(db.get_username_by_id(user_id=str(note.sender)))
        )
        equipment_list.append(equipment[i].to_dict())
    print(notifications_list, equipment_list)
    return jsonify({"notifications": notifications_list, "equipment": equipment_list})


# make sure to sanitize images for <script> tags, assigning UUID will happen in the back end
if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG"), port=5000, use_reloader=False)
