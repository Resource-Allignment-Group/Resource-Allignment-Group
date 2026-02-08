from flask import Flask, session, jsonify, request
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


def create_app(testing=False):
    load_dotenv()

    app = Flask(__name__)
    app.secret_key = os.environ.get("FLASK_SECRET_KEY")
    CORS(app, supports_credentials=True, origins=["http://localhost:3000", "http://127.0.0.1:3000"])
    db = DatabaseManager(testing=testing)
    nm = Notification_Manager(db=db)

    app.db = db
    app.nm = nm

    if testing:
        app.config["TESTING"] = True
        app.secret_key = "testing_key"

    else:
        app.config["SESSION_COOKIE_HTTPONLY"] = True
        app.config["SESSION_COOKIE_SECURE"] = False  # Keep False for localhost (no HTTPS)
        app.config["SESSION_TYPE"] = "filesystem"
        # Change None to 'Lax' - macOS browsers often reject 'None' without HTTPS
        app.config["SESSION_COOKIE_SAMESITE"] = 'Lax'

    @app.route("/authenticate", methods=["POST", "GET"])
    def authenticate():
        data = request.json
        email = data["email"]
        password = data["password"]

        # TODO:make sure that this try and except actually works the way it should
        try:
            user = db.get_user_by_email(email=email)
            hashed_passowrd = db.get_password_by_email(email=email)
            if check_password(
                origional_password=password, hashed_password=hashed_passowrd
            ):  # check with the the hashing algorithm
                if user.role == "p":
                    return "Account is still pending approval from admin"
                else:
                    session["user"] = email
                    session["role"] = user.role
                    session["id"] = str(user.id)  # Object ID can not be serialized
                    print(email)
                    return jsonify({"result": True, "message": "success", "role": user.role})

            else:
                return jsonify({"result": False, "message": "Something went wrong"})
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
                return jsonify({"result": True, "message": "Email doesn't exist"})
            else:
                return jsonify({"result": False, "message": str(e)})

    @app.route("/reset_password", methods=["POST"])
    def reset_password():
        token = request.json["token"]
        new_password = request.json["password"]

        try:
            token_hash = hashlib.sha256(token.encode()).hexdigest()

            reset = db.get_password_reset(token_hash=token_hash)
            print(reset["expires_at"], datetime.now(timezone.utc))
            print(type(reset["expires_at"]), type(datetime.now(timezone.utc)))

            if not reset:
                return jsonify({"result": True, "message": "Invalid or expired token"})

            expires_at = reset["expires_at"]

            # Convert naive datetime from Mongo into UTC-aware
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)

            if expires_at < datetime.now(timezone.utc):
                return jsonify({"result": True, "message": "Invalid or expired token"})

            password_hash = hash_password(new_password)

            db.set_user_password(id=reset["user_id"], password=password_hash)

            db.set_password_reset_used(id=ObjectId(reset["_id"]), used=True)

            return {"result": True}
        except Exception as e:
            return jsonify({"result": False, "message": f"error {str(e)}"})

    @app.route("/check-session", methods=["GET"])
    def check_session():
        user = session.get("user")  # Makes sure that the user is still logged in
        role = session.get("role")

        if user:
            return jsonify({"result": True, "user": user, "role": role})
        else:
            return jsonify({"result": False, "user": None, "role": None})

    @app.route("/logout", methods=["POST"])
    def logout():
        session.pop("user", None)
        session.pop("role", None)
        session.pop("id", None)
        return jsonify({"result": True, "message": "logged out"})

    @app.route("/register", methods=["POST"])
    def register():
        admin_session_id = session.get("id")
        if not admin_session_id:
                return jsonify({"result": False, "message": "Admin session expired. Please log in again."}), 401
        
        admin_id = ObjectId(admin_session_id)

        data = request.json
        fname, lname, email, password, phone = (
            data["fname"],
            data["lname"],
            data["email"],
            data["password"],
            data["phone"],
        )
        hashed_password = hash_password(
            password=password
        )  # I belive this uses SHA256 but i would have to check
        result = db.add_user(
            email=email, password=hashed_password, fname=fname, lname=lname, phone=phone, admin_id=admin_id
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

    @app.route("/get_user_info", methods=["GET"])
    def get_user_info():
        # add profile pic retrevial and any other import stuff here

        # This needs so re factoring once we get more features implimented
        inbox_notifications = db.get_inbox_by_user(user_id=ObjectId(session["id"]))
        unread_messages = db.get_unread_messages_by_user(
            user_id=ObjectId(session["id"])
        )
        return jsonify(
            {"result": True, "messages": [], "num_notifications": len(unread_messages)}
        )

    @app.route("/get_notifications", methods=["GET"])
    def get_notifications():
        user_notifications = db.get_notifications_by_user(
            user_id=ObjectId(session["id"])
        )
        msgs = []
        for note in user_notifications:
            msgs.append(
                note.to_dict(db.get_email_by_id(user_id=str(note.sender)))
            )  # not the best way to do this, but once again, van not think of a better way
            if note.type == "i":
                # kind of a jerry-rigged way to see if the user has read the message but I can't really think of a better way without massive overhead in developments
                db.set_notification_read(id=note.id, read=True)

        return jsonify({"result": True, "messages": msgs})

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
                db.remove_notification_from_inbox(notification=new_note)
                db.set_notification_read(id=new_note.id, read=True)
                if data["result"]:
                    result_message = f"{db.get_email_by_id(user_id=new_note.sender)} has been added to the system"
                    db.set_user_role(
                        id=ObjectId(new_note.sender), role="u"
                    )  # u for 'user'

                else:
                    result_message = f"{db.get_email_by_id(user_id=new_note.sender)} has been rejected from the system"
                    db.set_user_role(
                        id=ObjectId(new_note.sender), role="r"
                    )  # r stand for 'rejected'

                for admin in db.get_administrators():
                    nm.send_inform_notification(
                        sender=db.get_user_by_id(user_id=new_note.sender),
                        receiver=admin,
                        message=result_message,
                    )  # might want to make the sender a "system" sender or something like that

                return jsonify({"result": True})

            case (
                "r"
            ):  # If the notification is a equipment request, update the equipment
                db.remove_notification_from_inbox(notification=new_note)
                db.set_notification_read(id=ObjectId(new_note.id), read=True)

                if data["result"]:
                    admin_session_id = session.get("id")
                    
                    if not admin_session_id:
                        return jsonify({"result": False, "message": "Session expired. Please log in again."}), 401
                    
                    admin_id = ObjectId(admin_session_id)
                    equipment = db.get_equipment_by_id(id=new_note.equipment_id)
                    
                    db.set_notification_status(id=new_note.id, status="a")
                    db.add_user_equipment(
                        user_id=ObjectId(new_note.sender),
                        equipment_id=ObjectId(equipment.id),
                        admin_id=admin_id
                    )
                    db.set_equipment_checked_out(id=ObjectId(new_note.equipment_id), checked_out=True)

                    nm.send_inform_notification(
                        sender=db.get_user_by_id(user_id=admin_id),
                        receiver=db.get_user_by_id(user_id=ObjectId(new_note.sender)),
                        equipment_id=ObjectId(equipment.id),
                        message=f"Your request for {equipment.name} has been approved."
                    )
                    
                    return jsonify({"result": True, "message": "Equipment successfully checked out"})
                    # send notification to user that their equipment is theirs
                else:
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

    # Get all equipment from the database to display
    @app.route("/get_equipment", methods=["GET"])
    def get_equipment():
        equipment_cur = db.get_all_equipment()
        equip_list = []

        # This will show the user who has an equipment item checked out
        # on its card display right below its status line
        for equip in equipment_cur:
            equip_dict = equip.to_dict()

            # If equipment is checked out, find who has it
            if equip_dict["checked_out"]:
                # Find the user who has this equipment in their checked_out_equipment array
                user = db.get_user_by_equipment(ObjectId(equip_dict['id']))
                
                if user:
                    equip_dict['checkedOutBy'] = user.email
                else:
                    equip_dict['checkedOutBy'] = None
            else:
                equip_dict['checkedOutBy'] = None
            
            equip_list.append(equip_dict)

        # Sort the output equipment by their assigned status
        # (ie. Available, Checked Out, Damaged, Unavailable)
        def get_priority(equip):
            if equip["unavailable"]: return 4
            elif equip["damaged"]: return 3
            elif equip["checked_out"]: return 2
            else: return 1

        # This will sort the returned equipment by their status
        equip_list.sort(key=get_priority)
        return jsonify({"result": True, "equip_list": equip_list})

    @app.route("/request_equipment", methods=["POST"])
    def request_equipment():
        data = request.json
        equip_id = data["equip_id"]
        
        # Making extra sure that equipment can't be requested if it's
        # unavailable or already checked out
        equipment = db.get_equipment_by_id(id=ObjectId(equip_id))
        if equipment:
            if equipment.unavailable:
                return jsonify({
                    "result": False, 
                    "message": "This equipment is unavailable and cannot be checked out"
                })
            if equipment.checked_out:
                return jsonify({
                    "result": False, 
                    "message": "This equipment is already checked out"
                })

        note_result = nm.send_equipment_request(
            id=ObjectId(),
            sender=db.get_user_by_email(email=session["user"]),
            equip_name=data["equip_name"],
            equipment_id=ObjectId(equip_id),
        )
        if note_result:
            return jsonify({"result": True, "message": "this is the success message"})
        else:
            return jsonify({"result": False, "message": "this is the failure message"})

    @app.route("/get_user_equipment", methods=["GET"])
    def get_user_equipment():
        user_equipment = db.get_equipment_by_user(user_id=ObjectId(session["id"]))
        equip_list = []
        for equip in user_equipment:
            equip_list.append(equip.to_dict())

        return jsonify({"result": True, "equip_list": equip_list})

    @app.route("/return_equipment", methods=["POST"])
    def return_equipment():
        data = request.json
        try:
            equipment_id = ObjectId(data["equipment_id"])
            user_id = ObjectId(session["id"])
            is_damaged = data.get("damaged", False) 

            db.delete_user_equipment(user_id=user_id, equipment_id=equipment_id, damaged=is_damaged)

            equipment = db.get_equipment_by_id(id=equipment_id)
            for admin in db.get_administrators():
                nm.send_inform_notification(
                    sender=db.get_user_by_id(user_id),
                    receiver=admin,
                    message=f"The Equipment {equipment.name} has been returned",
                )
                
            return jsonify({"result": True})
        except Exception as e:
            return jsonify({"result": False, "message": str(e)})

    @app.route("/get_requests", methods=["GET"])
    def get_requests():
        notifications, equipment = db.get_requests_by_user(
            user_id=ObjectId(session["id"]) 
        )

        notifications_list, equipment_list = [], []

        for i, note in enumerate(notifications):
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

    @app.route("/get_dashboard_info")
    def get_dashboard_info():
        num_total, num_available, num_used, num_damaged, num_unavailable = (
            db.get_dashboard_info()
        )
        return jsonify(
            {
                "result": True,
                "total": num_total,
                "available": num_available,
                "used": num_used,
                "damaged": num_damaged,
                "unavailable": num_unavailable,
            }
        )

    @app.route("/get_users", methods=["GET"])
    def get_users():
        users = db.get_all_users()
        user_dicts = [user.to_dict() for user in users]
        return jsonify({"result": True, "users": user_dicts})

    @app.route("/change_user_role", methods=["POST"])
    def change_user_role():
        data = request.json
        db.set_user_role(id=ObjectId(data["user"]["id"]), role=data["new_role"])

        return jsonify({"result": True})

    @app.route("/delete_user_account", methods=["POST"])
    def delete_user_account():
        data = request.json

        admin_session_id = session.get("id")
        if not admin_session_id:
            return jsonify({"result": False, "message": "Admin session expired"}), 401
    
        admin_id = ObjectId(admin_session_id)

        notifications = db.get_notifications_by_user(ObjectId(data["user"]["id"]))
        for note in notifications:
            db.delete_notification(note_id=note.id)
            db.remove_notification_from_inbox(notification=note)
        user = db.get_user_by_id(ObjectId(data["user"]["id"]))
        result = db.delete_user(user=user, admin_id=admin_id)
        if result:
            return jsonify({"result": True})
        else:
            return jsonify({"result": False})

    @app.route("/add_equipment", methods=["POST"])
    def add_equipment():
        equip_data = request.json["data"]
        equip_data["_id"] = ObjectId()
        equip_data["images"] = request.json["images"]
        equip_data["reports"] = request.json["reports"]
        equip_data["checked_out"] = False
        equip_data["damaged"] = False

        new_equip = Equipment()
        new_equip.fill_from_json(equip_data)
        db.add_equipment(new_equip)
        return jsonify({"result": True})

    @app.route("/get_profile_info", methods=["GET"])
    def get_profile_equipment():
        user = db.get_user_by_id(user_id=ObjectId(session["id"]))
        return jsonify({"result": True, "user": user.to_dict()})

    @app.route("/save_new_profile_info", methods=["POST"])
    def save_new_profile_info():
        data = request.json
        db.set_user_name(
            id=ObjectId(session["id"]),
            new_name=f"{data['fname'].capitalize()} {data['lname'].capitalize()}",
        )
        db.set_user_email(id=ObjectId(session["id"]), new_email=data["email"])
        db.set_user_phone(id=ObjectId(session["id"]), new_phone=data["phone"])
        db.set_user_position(id=ObjectId(session["id"]), new_position=data["position"])
        return jsonify({"result": True})

    # A route that flags equipment as unavailable/available based
    # on the checkboxes selected on the hompage
    @app.route("/mark_equipment_unavailable", methods=['POST'])
    def mark_equipment_unavailable():
        data = request.get_json()
        equipment_ids = data["equipment_ids"]
        unavailable = data["unavailable"]
        
        # Convert to ObjectIds
        object_ids = [ObjectId(equip_id) for equip_id in equipment_ids]
        # Get all equipment in one query to check status
        all_equipment = db.get_equipment_by_ids(object_ids)
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
            updated_count = db.bulk_update_equipment_unavailable(allowed_ids, unavailable)
        
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

        return jsonify({
            "result": True,
            "updated_count": updated_count,
            "skipped_count": skipped_count,
            "message": message
        })
    
    # Go through the database and find the possible filter options
    # for farm locations, equipment class, makes, and years
    @app.route("/get_filter_options", methods=["GET"])
    def get_filter_options():
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
                if '/' in text:
                    parts = text.split('/')
                    return '/'.join(part.capitalize() for part in parts)
                elif ' ' in text:
                    parts = text.split(' ')
                    return ' '.join(part.capitalize() for part in parts)
                
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
            return jsonify({
                "result": True,
                "farms": sorted(list(farms)),
                "classes": sorted(list(classes)),
                "makes": sorted(list(makes)),
                "statuses": statuses
            })
            
        except Exception as e:
            print(f"Error getting filter options: {e}")
            return jsonify({"result": False, "error": str(e)})

    # Endpoint for user entered search parameters
    # Allows fuzzy searching (eg. tractor, tractr, tract)
    # Supports multi-word queries accross equipment fields
    @app.route("/search_equipment", methods=["POST"])
    def search_equipment():
        # Take in the received search params and normalize them
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
                    fuzz.token_sort_ratio(token, combined_text)
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

        return jsonify({
            "result": True,
            "equip_list": [r[1] for r in results],
            "query": query,
            "count": len(results),
        })
    
    @app.route("/delete_equipment", methods=["POST"])
    def delete_equipment():
        data = request.json
        try:
            equipment_id = data["equipment_id"]
            result = db.delete_equipment(equipment_id=ObjectId(equipment_id))
            if result:
                return jsonify({"result": True})
            else:
                return jsonify({"result": False, "message": "Equipment not found or could not be deleted"})
        except Exception as e:
            return jsonify({"result": False, "message": str(e)})

    return app
# make sure to sanitize images for <script> tags, assigning UUID will happen in the back end
if __name__ == "__main__":
    app = create_app(testing=False)
    app.run(debug=os.environ.get("FLASK_DEBUG"), port=5000, use_reloader=False)