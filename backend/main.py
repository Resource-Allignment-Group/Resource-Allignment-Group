from flask import Flask, session, jsonify, request, send_file, Response
from flask_cors import CORS
import os
from dotenv import load_dotenv
from database import DatabaseManager
from helpers import *
from notifications import Notification_Manager, Notification
from bson.objectid import ObjectId
from user import User
from datetime import datetime, timezone
from rapidfuzz import fuzz
import re
from report_gen import ReportGenerator
from report_scheduler import init_scheduler
from reports import setup_report_routes

# Regex patterns to match valid registration parameters
# This logic is in the frontend and backend, as it is good practice
EMAIL_REGEX = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
PHONE_REGEX = re.compile(r"^(\+1\s?)?(\(?\d{3}\)?[\s.-]?)\d{3}[\s.-]?\d{4}$")
PASSWORD_REGEX = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$"
)

def create_app(testing=False):
    load_dotenv()

    app = Flask(__name__)
    app.secret_key = os.environ.get("FLASK_SECRET_KEY")
    CORS(app, supports_credentials=True, origins="*")

    db = DatabaseManager(testing=testing)
    nm = Notification_Manager(db=db)

    app.db = db
    app.nm = nm

    if testing:
        app.config["TESTING"] = True
        app.secret_key = "testing_key"

    else:
        app.config["SESSION_COOKIE_HTTPONLY"] = True
        app.config["SESSION_COOKIE_SECURE"] = (
            False  # Keep False for localhost (no HTTPS)
        )
        app.config["SESSION_TYPE"] = "filesystem"
        # Change None to 'Lax' - macOS browsers often reject 'None' without HTTPS
        app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    # Initialize monthly reports
    report_generator = ReportGenerator(db)
    scheduler = init_scheduler(db, nm, report_generator)
    setup_report_routes(app, report_generator)

    # region LOGGING IN / REGISTERING

    @app.before_request
    def check_user_exists():
        """
        This function will run before each API call
        Users that've been deleted from the sys will have their session
        cleared. /authenticate will read the 401 error and redirect that user to the login page
        """
        # We still want to get user input in these routes, so ignore them
        if request.endpoint in ['authenticate', 'register'] or not request.endpoint:
            return

        # If there is a session, verify the user still exists in the DB
        if "user" in session:
            user = db.get_user_by_id(ObjectId(session["id"]))
            if not user:
                # The account was deleted
                # Remove the session cookie
                session.clear() 
                return jsonify({
                    "result": False, 
                    "message": "Account no longer exists. Logging out."
                }), 401

    @app.route("/authenticate", methods=["POST", "GET"])
    def authenticate():
        data = request.json
        email = data["email"]
        password = data["password"]
        
        if not email or not password:
            return jsonify({"result": False, "message": "Email and password are required"})
        
        # TODO: make sure that this try and except actually works the way it should
        try:
            user = db.get_user_by_email(email=email)
            if not user:
                return jsonify({"result": False, "message": "No account found with that email"})
            
            hashed_passowrd = db.get_password_by_email(email=email)
            if check_password(
                origional_password=password, hashed_password=hashed_passowrd
            ): 
                if user.role == "p":
                    return jsonify({"result": False, "message": "Account is still pending approval from admin"})
                else:
                    session["user"] = email
                    session["role"] = user.role
                    session["id"] = str(user.id) 
                    session["name"] = user.name
                    return jsonify(
                        {"result": True, "message": "success", "role": user.role}
                    )
            else:
                return jsonify({"result": False, "message": "Incorrect Credentials"})
        except Exception as e:
            return jsonify({"result": False, "message": str(e)})

    @app.route("/forgot_password", methods=["POST"])
    def forgot_password():
        email = request.json["email"]
        try:
            user = db.get_user_by_email(email=email)
            token, token_hash = generate_reset_token()
            link = db.create_password_reset(
                user_id=user.id, token=token, token_hash=token_hash
            )
            nm.send_forgot_password_email(email=email, link=link)
            return jsonify({"result": True, "message": "Email Was Sent"})
        except Exception as e:
            if "No user with email" in str(e):  # check this
                return jsonify({"result": False, "message": "Email doesn't exist"})
            else:
                return jsonify({"result": False, "message": str(e)})

    @app.route("/reset_password", methods=["POST"])
    def reset_password():
        token = request.json["token"]
        new_password = request.json["password"]

        try:
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            reset = db.get_password_reset(token_hash=token_hash)
            if not reset:
                return jsonify({"result": False, "message": "Invalid or expired token"})
            expires_at = reset["expires_at"]

            # Convert naive datetime from Mongo into UTC-aware
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            if expires_at < datetime.now(timezone.utc):
                return jsonify({"result": False, "message": "Invalid or expired token"})

            password_hash = hash_password(new_password)
            db.set_user_password(id=reset["user_id"], password=password_hash)
            db.set_password_reset_used(id=ObjectId(reset["_id"]), used=True)

            return {"result": True}
        except Exception as e:
            return jsonify({"result": False, "message": str(e)})

    @app.route("/check-session", methods=["GET"])
    def check_session():
        user = session.get("user")  
        role = session.get("role")

        if user:
            return jsonify({"result": True, "user": user, "role": role})
        else:
            return jsonify({"result": False, "user": None, "role": None})

    @app.route("/logout", methods=["POST"])
    def logout():
        try:
            session.pop("user", None)
            session.pop("role", None)
            session.pop("id", None)
            return jsonify({"result": True, "message": "logged out"})
        except Exception as e:
            return jsonify({"result": False, "message": str(e)})

    @app.route("/register", methods=["POST"])
    def register():
        try:
            data = request.json
            # Remove extra whitespaces and normalize input
            fname = data.get("fname", "").strip()
            lname = data.get("lname", "").strip()
            email = data.get("email", "").strip().lower()
            password = data.get("password", "")
            phone = data.get("phone", "").strip()
            # Remove any dashes, parenthesis, etc
            phone = re.sub(r"\D", "", phone)

            # Validate all inputs
            if not fname or not lname:
                return jsonify({"result": False, "message": "First and last name are required"}), 400
            if not EMAIL_REGEX.match(email):
                return jsonify({"result": False, "message": "Invalid email format"}), 400
            if not PHONE_REGEX.match(phone):
                return jsonify({"result": False, "message": "Invalid phone number"}), 400
            if not PASSWORD_REGEX.match(password):
                return jsonify({
                    "result": False,
                    "message": (
                        "Password must be at least 8 characters and include "
                        "uppercase, lowercase, number, and special character"
                    )
                }), 400
            
            hashed_password = hash_password(password=password)
            result = db.add_user(
                email=email, 
                password=hashed_password, 
                fname=fname, 
                lname=lname, 
                phone=phone,
            )

            if result["result"]:
                # send a notification to admin and update user management
                try:
                    new_user = db.get_user_by_email(email=email)
                    db.set_user_role(id=new_user.id, role="p")  #'p' stands for 'pending'
                    nm.send_account_approval_message(new_user=new_user)
                    return jsonify({"result": True, "message": "success"})
                except Exception as e:
                    return jsonify({"result": False, "message": str(e)})
            else:
                return jsonify({"result": False, "message": result["message"]})
        except Exception as e:
            return jsonify({"result": False, "message": str(e)})
        
    @app.route("/get_user_info", methods=["GET"])
    def get_user_info():
        #TODO: add profile pic retrevial and any other import stuff here
        try:
            unread_messages = db.get_unread_messages_by_user(
                user_id=ObjectId(session["id"])
            )
            return jsonify(
                {"result": True, "num_notifications": len(unread_messages)}
            )
        except Exception as e:
            return jsonify({"result": False, "message": str(e)})
        
    @app.route("/get_notifications", methods=["GET"])
    def get_notifications():
        """Get notifications to display in the user's inbox"""
        if "id" not in session:
            return jsonify({"result": False, "message": []})
        try:
            user_id = session["id"]
            notifications = db.get_notifications_by_user(user_id=user_id)
            if not notifications:
                return jsonify({"result": True, "messages": []})
            # Collect all unique sender IDs
            sender_ids = list(set([note.sender for note in notifications if note.sender])) 
            # Get all of the sender data (1 query)
            sender_map = {}
            if sender_ids:
                senders = db.users_db.find({"_id": {"$in": sender_ids}})
                for sender_doc in senders:
                    sender_map[sender_doc["_id"]] = sender_doc.get("name", "Unknown User")
            
            # Convert to dict
            messages = []
            for note in notifications:
                sender_name = sender_map.get(note.sender, "Unknown User")
                note_dict = note.to_dict(sender_name=sender_name)
                if note.type == "r" and note.equipment_id:
                    equip = db.get_equipment_by_id(note.equipment_id)
                    if equip:
                        if equip.display_image and equip.images and equip.display_image in equip.images:
                            note_dict["equipment_display_image_id"] = equip.display_image
                        elif equip.images and len(equip.images) > 0:
                            note_dict["equipment_display_image_id"] = equip.images[0]
                messages.append(note_dict)

            return jsonify({"result": True, "messages": messages})
        except Exception as e:
            return jsonify({"result": False, "message": str(e)})

    
    @app.route("/dismiss_notification", methods=["POST"])
    def dismiss_notification():
        """Used to remove notifications that the user clicked "X" on"""
        try:
            data = request.json
            note_info = data["notification"]
            # Get the notification ID
            note_id = note_info.get("id") or note_info.get("_id")
            if not note_id:
                return jsonify({"result": False, "error": "No notification ID provided"})
            # Delete the notification from inbox and DB
            db.delete_notification_completely(note_id=note_id)
            return jsonify({"result": True})
        except Exception as e:
            return jsonify({"result": False, "message": str(e)})

    @app.route("/admin_account_decision", methods=["POST"])
    def account_decision():
        data = request.json
        note_info = data["notification"]
        new_note = Notification()
        new_note.populate_from_json(json_info=note_info)

        match new_note.type:
            case (
                "a"
            ):  # if it is an account creation notification, update the users role
                try:
                    db.remove_notification_from_inbox(notification=new_note)
                    db.set_notification_read(id=new_note.id, read=True)

                    target_user = db.get_user_by_id(user_id=new_note.sender)
                    if not target_user:
                        return jsonify({"result": False, "message": "User no longer exists"})
                    admin_name = session.get("name")

                    if data["result"]:
                        result_message = f"{target_user.email} has been added to the system"
                        db.set_user_role(id=target_user.id, role="u")  # u for 'user'
                        db.add_log(
                            user_id=admin_name, 
                            action="ADD_USER", 
                            target_id=f"{target_user.name} : {target_user.email}",
                            details="New Account Approved by Admin"
                        )
                    else:
                        result_message = f"{target_user.email} has been rejected from the system"
                        db.delete_user(user=target_user, admin_name=admin_name, reason="DENIED")

                    for admin in db.get_administrators():
                        nm.send_inform_notification(
                            sender=target_user,
                            receiver=admin,
                            message=result_message,
                        )  # might want to make the sender a "system" sender or something like that

                    return jsonify({"result": True})
                except Exception as e:
                    return jsonify({"result": False, "message": str(e)})
            case (
                "r"
            ):  
                # If the notification is a equipment request, update the equipment
                try:
                    db.remove_notification_from_inbox(notification=new_note)
                    db.set_notification_read(id=ObjectId(new_note.id), read=True)
                    # Request is approved
                    if data["result"]:
                        admin_session_id = session.get("id")
                        
                        if not admin_session_id:
                            return jsonify({"result": False, "message": "Session expired. Please log in again."}), 401
                        
                        admin_id = ObjectId(admin_session_id)
                        equipment = db.get_equipment_by_id(id=new_note.equipment_id)
                        
                        # Mark the uses equipment request as approved, then checkout the equip
                        db.set_notification_status(id=new_note.id, status="a")
                        db.add_user_equipment(
                            user_id=ObjectId(new_note.sender),
                            equipment_id=ObjectId(equipment.id),
                            admin_name=session.get("name")
                        )
                        db.set_equipment_checked_out(id=ObjectId(new_note.equipment_id), checked_out=True)

                        # Get info about pending requests
                        pending_notification_ids, pending_user_ids = db.get_pending_request_info(
                            equipment_ids=[new_note.equipment_id],
                            exclude_notification_id=new_note.id
                        )
                        # Auto-deny all other pending requests for this equipment
                        db.cancel_pending_requests_for_equipment(
                            equipment_ids=[new_note.equipment_id],
                            exclude_notification_id=new_note.id
                        )
                        [db.remove_notification_from_inbox(id) for id in pending_notification_ids]
                        
                        # Notify users whose requests were auto-denied
                        for user_id in pending_user_ids:
                            nm.send_inform_notification(
                                sender=db.get_user_by_id(user_id=admin_id),
                                receiver=db.get_user_by_id(user_id=user_id),
                                message=f"Your request for {equipment.name} was denied because it was approved for another user."
                            )

                        # send notification to user that their equipment is theirs
                        nm.send_inform_notification(
                            sender=db.get_user_by_id(user_id=admin_id),
                            receiver=db.get_user_by_id(user_id=ObjectId(new_note.sender)),
                            equipment_id=ObjectId(equipment.id),
                            message=f"Your request for {equipment.name} has been approved."
                        )

                    # send notification to user that their equipment is theirs
                    nm.send_inform_notification(
                        sender=db.get_user_by_id(user_id=admin_id),
                        receiver=db.get_user_by_id(user_id=ObjectId(new_note.sender)),
                        equipment_id=ObjectId(equipment.id),
                        message=f"Your request for {equipment.name} has been approved."
                    )
                    
                    # Fetch the real inbox count for admin after all removals
                    updated_inbox = db.get_inbox_by_user(user_id=admin_id)
                    remaining_count = len([n for n in updated_inbox if n is not None])
                    # Return the number of notifs removed, that way the notif bubble is accurate
                    return jsonify({
                        "result": True,
                        "message": "Equipment successfully checked out",
                        "remaining_notification_count": remaining_count,
                        "removed_notification_ids": [str(nid) for nid in pending_notification_ids]
                    })
                except Exception as e:
                    return jsonify({"result": False, "message": str(e)})
                # Request was denied
                else:
                    try:
                        db.set_notification_status(id=new_note.id, status="r")
                        equipment = db.get_equipment_by_id(new_note.equipment_id)
                        # Check if equipment exists before asking for its name
                        if equipment:
                            equip_name = equipment.name
                        else:
                            equip_name = "Unknown Equipment (Deleted)"
                        nm.send_inform_notification(
                            sender=db.get_user_by_id(user_id=ObjectId(session["id"])),
                            receiver=db.get_user_by_id(user_id=new_note.sender),
                            message=f"Your request has been denied for {equip_name}",
                        )
                        return jsonify({"result": True})
                    except Exception as e:
                        return jsonify({"result": False, "message": str(e)})

    
    @app.route("/get_equipment", methods=["GET"])
    def get_equipment():
        try:
            equipment_cur = db.get_all_equipment()
            equip_list = [equip.to_dict() for equip in equipment_cur]
            # Get the IDs of all checked out equipment
            checked_out_ids = [ObjectId(equip["id"]) for equip in equip_list if equip["checked_out"]]
            equip_list
            # One DB call to get all users who have these equip checked out to them
            # This prevents multiple calls to the DB from the loop
            checkout_map = {}
            if checked_out_ids:
                users = [db.get_user_by_equipment(ObjectId(id)) for id in checked_out_ids]
                for user in users:
                    for equip_id in user.checked_out_equipment:
                        checkout_map[str(equip_id)] = user.email

            # Assign the chekedOutBy value based on the map
            for equip in equip_list:
                equip["checkedOutBy"] = checkout_map.get(equip["id"])
            # Sort the output equipment by their assigned status
            # (ie. Available, Checked Out, Damaged, Unavailable)
            def get_priority(equip):
                if equip["unavailable"]:
                    return 4
                elif equip["damaged"]:
                    return 3
                elif equip["checked_out"]:
                    return 2
                else:
                    return 1
            # This will sort the returned equipment by their status
            equip_list.sort(key=get_priority)
            return jsonify({"result": True, "equip_list": equip_list})
        except Exception as e:
            return jsonify({"result": False, "message": str(e)})
        
    @app.route("/request_equipment", methods=["POST"])
    def request_equipment():
        data = request.json
        equip_id = data["equip_id"]
        try:
            # Making extra sure that equipment can't be requested if it's
            # unavailable or already checked out
            equipment = db.get_equipment_by_id(id=ObjectId(equip_id))
            if equipment:
                if equipment.unavailable:
                    return jsonify(
                        {
                            "result": False,
                            "message": "This equipment is unavailable and cannot be checked out",
                        }
                    )
                if equipment.checked_out:
                    return jsonify(
                        {
                            "result": False,
                            "message": "This equipment is already checked out",
                        }
                    )

            note_result = nm.send_equipment_request(
                id=ObjectId(),
                sender=db.get_user_by_email(email=session["user"]),
                equip_name=data["equip_name"],
                equipment_id=ObjectId(equip_id),
            )
            if note_result:
                return jsonify({"result": True, "message": "this is the success message"})
            else:
                return jsonify({"result": False, "message": "Something went wrong, please refresh and try again"})
        except Exception as e:
            return jsonify({"result": False, "message": str(e)})
        
    @app.route("/get_user_equipment", methods=["GET"])
    def get_user_equipment():
        try:
            user_equipment = db.get_equipment_by_user(user_id=ObjectId(session["id"]))
            equip_list = [equip.to_dict() for equip in user_equipment]
            return jsonify({"result": True, "equip_list": equip_list})
        except Exception as e:
            return jsonify({"result": False, "message": str(e)})
                
    @app.route("/return_equipment", methods=["POST"])
    def return_equipment():
        data = request.json
        try:
            equipment_id = ObjectId(data["equipment_id"])
            user_id = ObjectId(session["id"])
            is_damaged = data.get("damaged", False)
            damage_description = data["damage_description"]

            db.delete_user_equipment(
                user_id=user_id, equipment_id=equipment_id, damaged=is_damaged, damage_description=damage_description
            )

            equipment = db.get_equipment_by_id(id=equipment_id)
            for admin in db.get_administrators():
                nm.send_inform_notification(
                    sender=db.get_user_by_id(user_id),
                    receiver=admin,
                    message=(
                        f"The Equipment {equipment.name} has been returned" 
                        + (f" DAMAGED: {damage_description}" if is_damaged else "")
                    ),
                )

            return jsonify({"result": True})
        except Exception as e:
            return jsonify({"result": False, "message": str(e)})

    @app.route("/get_requests", methods=["GET"])
    def get_requests():
        try:
            notifications, equipment = db.get_requests_by_user(
                user_id=ObjectId(session["id"]) 
            )

            notifications_list, equipment_list = [], []

            for i, note in enumerate(notifications):
                if equipment[i] is None:
                    continue
                
                notifications_list.append(
                    note.to_dict(db.get_email_by_id(user_id=str(note.sender)))
                )
                equipment_list.append(equipment[i].to_dict())
            return jsonify(
                {
                    "result": True,
                    "notifications": notifications_list,
                    "equipment": equipment_list,
                }
            )
        except Exception as e:
            return jsonify({"result": False, "message": str(e)})
        
    @app.route("/get_dashboard_info")
    def get_dashboard_info():
        try:
            num_total, num_available, num_used, num_damaged, num_unavailable = (
                db.get_dashboard_info()
            )
            #TODO:  Get the admins preference for monthly report gen
            admin_id = session["id"]
            user = db.get_user_by_id(ObjectId(admin_id))

            return jsonify(
                {
                    "result": True,
                    "total": num_total,
                    "available": num_available,
                    "used": num_used,
                    "damaged": num_damaged,
                    "unavailable": num_unavailable,
                    "receive_reports": user.receive_reports,
                }
            )
        except Exception as e:
            return jsonify({"result": False, "message": str(e)})
        
    @app.route("/get_users", methods=["GET"])
    def get_users():
        try:
            users = db.get_all_users()
            user_dicts = []
            for user in users:
                user_dict = user.to_dict()
                # Populate equipment details if user has checked out equipment
                if user_dict.get("checked_out_equipment"):
                    equipment_details = []
                    for equip_id in user_dict["checked_out_equipment"]:
                        equipment = db.get_equipment_by_id(equip_id)
                        if equipment:
                            equipment_details.append({
                                "name": equipment.name,
                            })
                    user_dict["checked_out_equipment"] = equipment_details
                user_dicts.append(user_dict)
            return jsonify({"result": True, "users": user_dicts})
        except Exception as e:
            return jsonify({"result": False, "message": str(e)})
        
    @app.route("/change_user_role", methods=["POST"])
    def change_user_role():
        # Get the admin session name for verification and logging
        try:
            admin_name = session.get("name") 
            if not admin_name:
                return jsonify({"result": False, "message": "Not logged in"})
            
            data = request.json
            user_id = ObjectId(data["user"]["id"])
            db.set_user_role(id=user_id, role=data["new_role"])
            user = db.get_user_by_id(user_id)
            # Log the role change
            db.add_log(
                user_id=admin_name, 
                action="UPDATE_ROLE", 
                target_id=f"{user.name} : {user.email}", 
                details=f"{data['new_role']}"
            )
            return jsonify({"result": True})
        except Exception as e:
            return jsonify({"result": False, "message": str(e)})

    @app.route("/delete_user_account", methods=["POST"])
    def delete_user_account():
        try:
            data = request.json
            admin_name = session.get("name")
            if not admin_name:
                return jsonify({"result": False, "message": "Admin session expired"}), 401
            
            cur_session_id = session["id"]
            target_user_id = ObjectId(data["user"]["id"])
            # Remove that users notifications from the database
            notifications = db.get_notifications_by_user(target_user_id)
            for note in notifications:
                db.delete_notification(note_id=note.id)
                db.remove_notification_from_inbox(notification=note)
            
            # Delete the user
            user = db.get_user_by_id(ObjectId(data["user"]["id"]))
            result = db.delete_user(user=user, admin_name=admin_name, reason="DELETED")
            
            if result:
                # Check if the user just deleted themselves
                if str(target_user_id) == str(cur_session_id):
                    session.clear()
                    return jsonify({"result": True, "self_deleted": True})
                return jsonify({"result": True, "self_deleted": False})
            else:
                return jsonify({"result": False, "message": "User was not able to be deleted"})
        except Exception as e:
            return jsonify({"result": False, "message": str(e)})

    @app.route("/add_equipment", methods=["POST"])
    def add_equipment():
        # Get admin name for validation and logging
        admin_name = session.get("name")
        if not admin_name:
            return jsonify({"result": False, "message": "Not logged in"})
        if session.get("role") != "a":
            return jsonify({"result": False, "message": "Admin only"})

        if request.content_type and "multipart/form-data" in request.content_type:
            form_data = request.form
            year_val = form_data["year"] if "year" in form_data else ""
            try:
                year_int = int(year_val) if year_val else None
            except ValueError:
                year_int = None
            equip_data = {
                "_id": ObjectId(),
                "name": form_data["name"],
                "class": form_data["class"],
                "year": year_int,
                "farm": form_data["farm"],
                "model": form_data["model"],
                "make": form_data["make"],
                "use": form_data["use"],
                "description": form_data["description"] if "description" in form_data and form_data["description"] else "",
                "images": [],
                "reports": [],
                "checked_out": False,
                "damaged": False,
            }
            new_equip = Equipment()
            new_equip.fill_from_json(equip_data)
            db.add_equipment(new_equip)
            if "images" in request.files:
                for file in request.files.getlist("images"):
                    if file.filename:
                        img_id, err = db.add_equipment_image(equip_data["_id"], file)
                        if err:
                            pass
            if "reports" in request.files:
                for file in request.files.getlist("reports"):
                    if file.filename:
                        db.add_equipment_report(equip_data["_id"], file)
        else:
            equip_data = request.json["data"]
            equip_data["_id"] = ObjectId()
            equip_data["images"] = request.json["images"] if "images" in request.json else []
            equip_data["reports"] = request.json["reports"] if "reports" in request.json else []
            equip_data["checked_out"] = False
            equip_data["damaged"] = False
            new_equip = Equipment()
            new_equip.fill_from_json(equip_data)
            db.add_equipment(new_equip)

        db.add_log(
            user_id=admin_name,
            action="ADD_EQUIPMENT",
            target_id=f"{equip_data['name']}",
            details="Admin Added Equipment",
        )
        return jsonify({"result": True})

    @app.route("/upload_equipment_file", methods=["POST"])
    def upload_equipment_file():
        if session.get("role") != "a":
            return jsonify({"result": False, "message": "Admin only"})
        equipment_id = ObjectId(request.form["equipment_id"])
        file_type = request.form["file_type"]
        file = request.files["file"] if "file" in request.files else None
        if not file:
            return jsonify({"result": False, "message": "No file provided"})
        if file_type == "image":
            file_id, err = db.add_equipment_image(equipment_id, file)
        elif file_type == "report":
            file_id, err = db.add_equipment_report(equipment_id, file)
        else:
            return jsonify({"result": False, "message": "Invalid file_type"})
        if err:
            return jsonify({"result": False, "message": err})
        return jsonify({"result": True, "file_id": file_id})

    @app.route("/get_equipment_image/<equipment_id>/<image_id>", methods=["GET"])
    def get_equipment_image(equipment_id, image_id):
        equipment = db.get_equipment_by_id(ObjectId(equipment_id))
        if not equipment or not equipment.images or image_id not in equipment.images:
            return jsonify({"result": False, "message": "Not found"}), 404
        result = db.get_image(image_id)
        if isinstance(result, str):
            return jsonify({"result": False, "message": result}), 404
        return Response(result, mimetype="image/png")

    @app.route("/get_equipment_report/<equipment_id>/<report_id>", methods=["GET"])
    def get_equipment_report(equipment_id, report_id):
        equipment = db.get_equipment_by_id(ObjectId(equipment_id))
        if not equipment or not equipment.reports or report_id not in equipment.reports:
            return jsonify({"result": False, "message": "Not found"}), 404
        result = db.get_report(report_id)
        if isinstance(result, str):
            return jsonify({"result": False, "message": result}), 404
        return Response(result.getvalue(), mimetype="application/pdf")

    @app.route("/set_equipment_display_image", methods=["POST"])
    def set_equipment_display_image():
        if session.get("role") != "a":
            return jsonify({"result": False, "message": "Admin only"})
        data = request.json
        equipment_id = ObjectId(data["equipment_id"])
        image_id = data["image_id"]
        if db.set_equipment_display_image(equipment_id, image_id):
            return jsonify({"result": True})
        return jsonify({"result": False, "message": "Failed to set display image"})

    @app.route("/remove_equipment_file", methods=["POST"])
    def remove_equipment_file():
        if session.get("role") != "a":
            return jsonify({"result": False, "message": "Admin only"})
        data = request.json
        equipment_id = ObjectId(data["equipment_id"])
        file_id = data["file_id"]
        file_type = data["file_type"]
        if file_type == "image":
            ok = db.remove_equipment_image(equipment_id, file_id)
        elif file_type == "report":
            ok = db.remove_equipment_report(equipment_id, file_id)
        else:
            return jsonify({"result": False, "message": "Invalid file_type"})
        if ok:
            return jsonify({"result": True})
        return jsonify({"result": False, "message": "Failed to remove file"})

    @app.route("/upload_profile_image", methods=["POST"])
    def upload_profile_image():
        file = request.files["file"] if "file" in request.files else None
        if not file:
            return jsonify({"result": False, "message": "No file provided"})
        user_id = ObjectId(session["id"])
        img_id, err = db.add_profile_picture(user_id, file)
        if err:
            return jsonify({"result": False, "message": err})
        return jsonify({"result": True, "file_id": img_id})

    @app.route("/get_profile_image/<user_id>", methods=["GET"])
    def get_profile_image(user_id):
        img_id = db.get_profile_image_id(ObjectId(user_id))
        if not img_id:
            return jsonify({"result": False, "message": "No profile image"}), 404
        path = db.profile_images_db / img_id
        if not path.exists():
            return jsonify({"result": False, "message": "File not found"}), 404
        from PIL import Image as PILImage
        import io
        img = PILImage.open(path)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return Response(buffer.getvalue(), mimetype="image/png")

    @app.route("/delete_profile_image", methods=["POST"])
    def delete_profile_image():
        user_id = ObjectId(session["id"])
        if db.delete_profile_picture(user_id):
            return jsonify({"result": True})
        return jsonify({"result": False, "message": "No profile image to delete"})

    @app.route("/change_equipment_info", methods=["POST"])
    def change_equipment_info():
        equipment_info = request.json["equipment"]
        try:
            for key in equipment_info.keys():
                if key == "id":
                    continue
                db.update_equipment_field(
                    equip_id=ObjectId(equipment_info["id"]),
                    field_name=key,
                    value=equipment_info[key],
                )
            return jsonify(
                {"result": True, "message": "Equipment info has been changed"}
            )
        except Exception as e:
            return jsonify({"result": False, "message": str(e)})

    @app.route("/get_profile_info", methods=["GET"])
    def get_profile_equipment():
        try:
            user = db.get_user_by_id(user_id=ObjectId(session["id"]))
            return jsonify({"result": True, "user": user.to_dict()})
        except Exception as e:
            return jsonify({"result": False, "message": str(e)})
        
    @app.route("/save_new_profile_info", methods=["POST"])
    def save_new_profile_info():
        try:
            data = request.json
            db.set_user_name(
                id=ObjectId(session["id"]),
                new_name=f"{data['fname'].strip()} {data['lname'].strip()}",
            )
            db.set_user_email(id=ObjectId(session["id"]), new_email=data["email"])
            db.set_user_phone(id=ObjectId(session["id"]), new_phone=data["phone"])
            db.set_user_position(id=ObjectId(session["id"]), new_position=data["position"])
            db.set_user_department(id=ObjectId(session["id"]), new_department=data["department"])
            return jsonify({"result": True})
        except Exception as e:
            return jsonify({"result": False, "message": str(e)})
        

    @app.route("/mark_equipment_unavailable", methods=["POST"])
    def mark_equipment_unavailable():
        """A route that flags equipment as unavailable/available based
        on the checkboxes selected on the hompage"""
        try:
            data = request.get_json()
            unavailable = data["unavailable"]

            # Convert to ObjectIds
            # Get all equipment in one query to check status
            all_equipment = db.get_all_equipment()
            # Will track how many items were skipped/not
            skipped_count = 0
            allowed_ids = []

            for equipment in all_equipment:
                if unavailable:
                    # Skip if checked out, damaged, or already unavailable
                    if equipment.checked_out or equipment.damaged or equipment.unavailable:
                        skipped_count += 1
                    else:
                        allowed_ids.append(equipment.id)
                else:
                    # Skip if NOT currently unavailable
                    if not equipment.unavailable:
                        skipped_count += 1
                    else:
                        allowed_ids.append(equipment.id)

            # Update many equipment status at once
            if allowed_ids:
                updated_count = db.bulk_update_equipment_unavailable(
                    allowed_ids, unavailable
                )

                # Cancel pending requests
                if unavailable:
                    db.cancel_pending_requests_for_equipment(allowed_ids)
            else:
                updated_count = 0

            # Create message to return to the user as feedback
            if unavailable:
                # Marking as unavailable
                if updated_count == 0 and skipped_count > 0:
                    message = "No equipment marked as unavailable. Selected items are already unavailable, checked out, or damaged."
                elif skipped_count > 0:
                    message = f"Marked {updated_count} item(s) as unavailable. {skipped_count} item(s) skipped (already unavailable, checked out, or damaged)."
                else:
                    message = f"Successfully marked {updated_count} item(s) as unavailable."
            else:
                # Marking as available
                if updated_count == 0 and skipped_count > 0:
                    message = "No equipment marked as available. Selected items are not currently unavailable."
                elif skipped_count > 0:
                    message = f"Marked {updated_count} item(s) as available. {skipped_count} item(s) skipped (not currently unavailable)."
                else:
                    message = f"Successfully marked {updated_count} item(s) as available."

            return jsonify(
                {
                    "result": True,
                    "updated_count": updated_count,
                    "skipped_count": skipped_count,
                    "message": message,
                }
            )
        except Exception as e:
            return jsonify({"result": False, "message": str(e)})
        

    @app.route("/get_filter_options", methods=["GET"])
    def get_filter_options():
        """Go through the database and find the possible filter options
        for farm locations, equipment class, makes, and years"""
        try:
            # Get all equipment
            equipment_cursor = db.get_all_equipment()

            # Use sets to collect unique values
            farms = set()
            classes = set()
            makes = set()

            # Helper function to format text properly
            def format_text(text):
                if not text:
                    return text

                # Handle items with slashes like "HAY/FEED"
                if "/" in text:
                    parts = text.split("/")
                    return "/".join(part.capitalize() for part in parts)
                elif " " in text:
                    parts = text.split(" ")
                    return " ".join(part.capitalize() for part in parts)

                # Regular capitalization
                return text.capitalize()

            for equip in equipment_cursor:
                # Add farm if it exists and is not None/empty
                if equip.farm and equip.farm.strip():
                    farms.add(format_text(equip.farm.strip()))

                # Add class if it exists
                if equip._class and equip._class.strip():
                    classes.add(format_text(equip._class.strip()))

                # Add make if it exists
                if equip.make and equip.make.strip():
                    makes.add(format_text(equip.make.strip()))

            statuses = ["Available", "Checked Out", "Damaged", "Unavailable"]
            # Convert sets to sorted lists
            return jsonify(
                {
                    "result": True,
                    "farms": sorted(list(farms)),
                    "classes": sorted(list(classes)),
                    "makes": sorted(list(makes)),
                    "statuses": statuses,
                }
            )
        except Exception as e:
            return jsonify({"result": False, "message": str(e)})


    @app.route("/search_equipment", methods=["POST"])
    def search_equipment():
        """
        Endpoint for user entered search parameters
        Allows fuzzy searching (eg. tractor, tractr, tract)
        Supports multi-word queries accross equipment fields
        """
        try:
            data = request.get_json()
            query = (data["query"] or "").strip().lower()

            # If no search query was entered, load equipment normally
            if not query:
                return get_equipment()

            # Split search into tokens
            query_tokens = query.split()
            all_equipment = db.get_all_equipment()
            results = []

            # Iterate through equipment items and score them
            for equip in all_equipment:
                # Searchable fields
                fields = {
                    "name": equip.name or "",
                    "make": equip.make or "",
                    "model": equip.model or "",
                    "class": equip._class or "",
                    "farm": equip.farm or "",
                    "description": equip.description or "",
                }

                # Normalize status
                if equip.unavailable:
                    fields["status"] = "unavailable"
                elif equip.damaged:
                    fields["status"] = "damaged"
                elif equip.checked_out:
                    fields["status"] = "checked out"
                else:
                    fields["status"] = "available"

                # Normalize field values (lowercase)
                fields = {k: str(v).lower() for k, v in fields.items() if v}
                token_scores = []

                # Combine all field values into one searchable text
                combined_text = " ".join(fields.values())

                for token in query_tokens:
                    # Use token_sort_ratio for queries where word order matters
                    # Use partial_ratio for substring matching for misspelling, etc
                    token_score = max(
                        fuzz.partial_ratio(token, combined_text),
                        fuzz.token_sort_ratio(token, combined_text),
                    )
                    token_scores.append(token_score)

                # For multi word queries, use the average score
                if token_scores:
                    score = sum(token_scores) / len(token_scores)
                else:
                    score = 0

                # Only display the equipment that closely match the search params
                if score >= 80:
                    equip_dict = equip.to_dict()
                    # Show who has that equipment checked out if any
                    if equip_dict["checked_out"]:
                        user = db.get_user_by_equipment(ObjectId(equip_dict["id"]))
                        equip_dict["checkedOutBy"] = user.email if user else None
                    else:
                        equip_dict["checkedOutBy"] = None

                    results.append((score, equip_dict))

            # Sort by relevance (highest first)
            results.sort(key=lambda x: x[0], reverse=True)

            return jsonify(
                {
                    "result": True,
                    "equip_list": [r[1] for r in results],
                    "query": query,
                    "count": len(results),
                }
            )
        except Exception as e:
            return jsonify({"result": False, "message": str(e)})
        
    @app.route("/delete_equipment", methods=["POST"])
    def delete_equipment():
        try:
            # Get admin name for validation and logging
            admin_name = session.get("name")
            if not admin_name:
                return jsonify({"result": False, "message": "Not logged in"})
            
            data = request.json
            equipment_id = ObjectId(data["equipment_id"])
            equip = db.get_equipment_by_id(equipment_id)
            equip_info = f"{equip.name}"

            if equip is None:
                return jsonify({
                    "result": False,
                    "message": "Equipment not found"
                }), 404

            #Don't allow deletion if equipment is checked out
            if equip.checked_out:
                return jsonify({
                    "result": False,
                    "message": "This equipment is currently checked out and cannot be deleted"
                }), 400
            
            # Get info on pending requests (notification IDs and user IDs who made requests)
            pending_notification_ids, pending_user_ids = db.get_pending_request_info(
                equipment_ids=[equipment_id]
            )

            #Deny pending requests for equipment
            db.cancel_pending_requests_for_equipment(
                equipment_ids=[equipment_id]
            )

            #Remove notifications from all admin inboxes
            [db.remove_notification_from_inbox(id) for id in pending_notification_ids]

            # Send notifications to users whose requests were denied
            if "id" in session and pending_user_ids:
                admin_id = ObjectId(session["id"])
                admin_user = db.get_user_by_id(user_id=admin_id)
                for user_id in pending_user_ids:
                    nm.send_inform_notification(
                        sender=admin_user,
                        receiver=db.get_user_by_id(user_id=user_id),
                        message=f"Your request for {equip.name} was denied because the equipment was deleted from the system."
                    )

            #Delete the equipment and its related data (this will also update notifications to [DELETED])
            result = db.delete_equipment(equipment_id=equipment_id)
            if result:
                db.add_log(
                    user_id=admin_name, 
                    action="DELETE_EQUIPMENT", 
                    target_id=equip_info,
                    details="Admin Deleted Equipment"
                )
                return jsonify({"result": True, "message": "Equipment was deleted"})
            else:
                return jsonify(
                    {
                        "result": False,
                        "message": "Equipment not found or could not be deleted",
                    }
                )
        except Exception as e:
            return jsonify({"result": False, "message": str(e)}), 500


    @app.route('/update_report_preference', methods=['POST'])
    def update_report_pref():
        """Updates the admins preference for receiving monthly reports or not"""
        try:
            admin_id = ObjectId(session['id'])
            # Get the toggle value (True/False) from the frontend
            data = request.get_json()
            receive_reports = data['receive_reports']
            
            res = db.update_admin_report_preference(admin_id=admin_id, action=receive_reports)
            if res:
                return jsonify({"result": True, "message": "Preference updated"})
            else:
                return jsonify({"result": False, "message": "Database update failed"})
        except Exception as e:
            return jsonify({"result": False, "message": str(e)})

    return app

if __name__ == "__main__":
    app = create_app(testing=False)
    app.run(
        host="0.0.0.0",
        debug=os.environ.get("FLASK_DEBUG"),
        port=5000,
        use_reloader=False,
    )
