from flask import Flask, session, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv
from database import DatabaseManager
from flask_session import Session
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
    if check_password(origional_password=password, hashed_password=user.password):
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
    user = session.get("user")

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
    email, password = data["email"], data["password"]  # data["admin_email"]
    hashed_password = hash_password(password=password)
    result = db.add_user(email=email, password=hashed_password)

    if result["result"]:
        # send a notification to admin and update user management
        new_user = db.get_user_by_username(username=email)
        db.set_user_role(id=new_user.id, role="p")
        nm.send_account_approval_message(new_user=new_user)
        return jsonify({"message": "success"})
    else:
        return jsonify({"message": result["message"]})


@app.route("/get_user_info", methods=["GET"])
def get_user_info():
    # add profile pic retrevial and any other import stuff here
    inbox_notifications = db.get_inbox_by_user(user_id=ObjectId(session["id"]))
    return jsonify(
        {"messages": [], "num_notifications": len(list(inbox_notifications))}
    )


@app.route("/get_notifications", methods=["GET"])
def get_notifications():
    user_notifications = db.get_notifications_by_user(user_id=ObjectId(session["id"]))
    msgs = []
    for note in user_notifications:
        msgs.append(
            {
                "sender_username": db.get_username_by_id(user_id=str(note["sender"])),
                "sender": str(note["sender"]),
                "receiver": str(note["receiver"]),
                "date": str(note["date"]),
                "body": note["body"],
                "type": note["type"],
                "_id": str(note["_id"]),
            }
        )
    return jsonify({"messages": msgs})


@app.route("/admin_account_decision", methods=["POST"])
def account_decision():
    data = request.json
    note = data["notification"]
    new_note = Notification(
        id=ObjectId(note["_id"]),
        sender=note["sender"],
        receiver=note["receiver"],
        date=note["date"],
        body=note["body"],
        _type=note["type"],
    )
    note_res = db.remove_notification_from_inbox(notification=new_note)
    if data["result"]:
        user_res = db.set_user_role(id=ObjectId(new_note.sender), role="u")
    else:
        pass  # Send notification for deckine

    return jsonify({"result": 0})

@app.route("/get_equipment", methods=["GET"])
def get_equipment():
    equipment_cur = db.get_all_equipment()
    equip_list = []
    for equip in equipment_cur:

        
        equip_list.append({
        "id": str(equip["_id"]) ,
        "name": equip["name"],
        "checkedOutBy": "test@gmail.com" if equip["name"] == "Manure Spreader, None, None, 1990 (MANURE/FERTILIZER)" else "None", #Change Later
        "class": equip["class"],
        "year": equip["year"],
        "farm": equip["farm"],
        "model": equip["model"],
        "make": equip["make"],
        "use": equip["use"],
        "images": equip["images"],
        "reports": equip["reports"],
        "checked_out": "Checked Out" if equip["name"] == "Manure Spreader, None, None, 1990 (MANURE/FERTILIZER)" else "Available",
        "description": equip["description"],
        "attachments": 0, #Change later
        "replacementCost": 100000 #change lateer
        })
    return jsonify(equip_list)
    
@app.route("/request_equipment")
def request_equipment():
    data = request.json
    equip_id = data["equip_id"]
    result = db.set_equipment_checked_out(id=ObjectId(equip_id), checked_out="Requested") #Should move all of these to chars to save database space
    note_result = nm.sen

# make sure to sanitize images for <script> tags, assigning UUID will happen in the back end
if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG"), port=5000, use_reloader=False)
