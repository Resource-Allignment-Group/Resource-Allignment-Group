from flask import Flask, session, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv
from database import DatabaseManager
from helpers import *
from notifications import Notification_Manager, Notification
from bson.objectid import ObjectId
from user import User


def create_app(testing=False):
    load_dotenv()

    app = Flask(__name__)
    app.secret_key = os.environ.get("FLASK_SECRET_KEY")
    CORS(app, supports_credentials=True, origins=["http://localhost:3000"])

    db = DatabaseManager(testing=testing)
    nm = Notification_Manager(db=db)

    app.db = db
    app.nm = nm

    if testing:
        app.config["TESTING"] = True
        app.secret_key = "testing_key"

    else:
        app.config["SESSION_COOKIE_HTTPONLY"] = True
        app.config["SESSION_COOKIE_SECURE"] = False
        app.config["SESSION_TYPE"] = "filesystem"
        app.config["SESSION_COOKIE_SAMESITE"] = None

    @app.route("/authenticate", methods=["POST", "GET"])
    def authenticate():
        data = request.json
        email = data.get("email")
        password = data.get("password")

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
                    return jsonify({"result": True, "message": "success"})

            else:
                return jsonify({"result": False, "message": "Something went wrong"})
        except Exception as e:
            return jsonify({"result": False, "message": str(e)})

    @app.route("/check-session", methods=["GET"])
    def check_session():
        user = session.get("user")  # Makes sure that the user is still logged in

        if user:
            return jsonify({"result": True, "user": user})
        else:
            return jsonify({"result": False, "user": None})

    @app.route("/logout", methods=["POST"])
    def logout():
        session.pop("user", None)
        session.pop("role", None)
        session.pop("id", None)
        return jsonify({"result": True, "message": "logged out"})

    @app.route("/register", methods=["POST"])
    def register():
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
            email=email, password=hashed_password, fname=fname, lname=lname, phone=phone
        )

        if result["result"]:
            # send a notification to admin and update user management
            try:
                new_user = db.get_user_by_email(email=email)
                db.set_user_role(id=new_user.id, role="p")  #'p' stands for 'pending'
                nm.send_account_approval_message(new_user=new_user)
                return jsonify({"result": True, "message": "success"})
            except Exception as e:
                return jsonify({"result": False, "message": e})
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
                    equipment = db.get_equipment_by_id(id=new_note.equipment_id)
                    db.set_notification_status(id=new_note.id, status="a")
                    db.add_user_equipment(
                        user_id=ObjectId(new_note.sender),
                        equipment_id=ObjectId(equipment.id),
                    )
                    user_email = db.get_email_by_id(user_id=str(new_note.sender))
                    db.set_equipment_checked_out(
                        id=ObjectId(new_note.equipment_id), checked_out=True
                    )
                    return jsonify({"result": True})
                    # send notification to user that their equipment is theirs
                else:
                    db.set_notification_status(id=new_note.id, status="r")
                    db.set_equipment_checked_out(id=new_note.id, checked_out=False)
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
            if equip_dict.get('checked_out'):
                # Find the user who has this equipment in their checked_out_equipment array
                user = db.users_db.find_one({
                    "checked_out_equipment": ObjectId(equip_dict['id'])
                })
                
                if user:
                    equip_dict['checkedOutBy'] = user.get('email', 'Unknown')
                else:
                    equip_dict['checkedOutBy'] = None
            else:
                equip_dict['checkedOutBy'] = None
            
            equip_list.append(equip_dict)

        # Sort the output equipment by their assigned status
        # (ie. Available, Checked Out, Damaged, Unavailable)
        def get_priority(equip):
            if equip.get('unavailable'): return 4
            elif equip.get('damaged'): return 3
            elif equip.get('checked_out'): return 2
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
        equipment = db.equipment_db.find_one({"_id": ObjectId(equip_id)})
        if equipment:
            if equipment.get('unavailable', False):
                return jsonify({
                    "result": False, 
                    "message": "This equipment is unavailable and cannot be checked out"
                })
            if equipment.get('checked_out', False):
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
            equipment = db.get_equipment_by_id(id=ObjectId(data["equipment_id"]))
            db.set_equipment_checked_out(id=equipment.id, checked_out=False)
            db.remove_equipment_from_inbox(
                equip_id=equipment.id, user_id=ObjectId(session["id"])
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
        user = db.get_user_by_id(ObjectId(data["user"]["id"]))
        result = db.delete_user(user=user)
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
        equipment_ids = data.get('equipment_ids', [])
        unavailable = data.get('unavailable', True)
        
        # Convert to ObjectIds
        object_ids = [ObjectId(equip_id) for equip_id in equipment_ids]
        # Get all equipment in one query to check status
        # Faster for bulk unavailable/available
        all_equipment = list(db.equipment_db.find({"_id": {"$in": object_ids}}))
        # Will track how many items were skipped/not
        # (Items that aren't allowed to be made available/unavailable at this time)
        skipped_count = 0
        allowed_ids = []

        # for equip_id in equipment_ids:
        #     # Check if equipment is checked out or damaged before marking unavailable
        #     equipment = db.equipment_db.find_one({"_id": ObjectId(equip_id)})
        #     if equipment:
        #         # Skipping invalid items when marking as unavailable
        #         if unavailable:
        #             # Skip if checked out or damaged
        #             if equipment.get('checked_out', False) or equipment.get('damaged', False) or equipment.get('unavailable', False):
        #                 skipped_count += 1
        #                 continue
        #         else:
        #             # Only mark equipment as available if they are 
        #             # currently marked as unavailable
        #             if not equipment.get('unavailable', False):
        #                 skipped_count += 1
        #                 continue

        #     success = db.update_equipment_field(equip_id, "unavailable", unavailable)
        #     if success:
        #         updated_count += 1

        #         # If marking equipment as unavailable, cancel any 
        #         # pending requests for that item
        #         if unavailable:
        #             pending_requests = db.notifications_db.find({
        #                 "equipment_id": ObjectId(equip_id),
        #                 "type": "r",
        #                 "status": {"$ne": "a"}  # Not approved
        #             })
                    
        #             # Reject any pending requests for that item
        #             for item in pending_requests:
        #                 db.set_notification_status(id=item["_id"], status="r")
        
        for equipment in all_equipment:
            if unavailable:
                # Skip if checked out, damaged, or already unavailable
                if equipment.get('checked_out') or equipment.get('damaged') or equipment.get('unavailable'):
                    skipped_count += 1
                else:
                    allowed_ids.append(equipment['_id'])
            else:
                # Skip if NOT currently unavailable
                if not equipment.get('unavailable'):
                    skipped_count += 1
                else:
                    allowed_ids.append(equipment['_id'])
        
        # Update many equipment status at once
        if allowed_ids:
            result = db.equipment_db.update_many(
                {"_id": {"$in": allowed_ids}},
                {"$set": {"unavailable": unavailable}}
            )
            updated_count = result.modified_count
            
            # Cancel pending requests for unavailable items
            if unavailable:
                db.notifications_db.update_many(
                    {
                        "equipment_id": {"$in": allowed_ids},
                        "type": "r",
                        "status": {"$ne": "a"}
                    },
                    {"$set": {"status": "r"}}
                )
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
            years = set()
            
            for equip in equipment_cursor:
                # Add farm if it exists and is not None/empty
                if equip.farm and equip.farm.strip():
                    farms.add(equip.farm.strip())
                
                # Add class if it exists
                if equip._class and equip._class.strip():
                    classes.add(equip._class.strip())
                
                # Add make if it exists
                if equip.make and equip.make.strip():
                    makes.add(equip.make.strip())
                
                # Add year if it exists
                if equip.year:
                    try:
                        # Ensure year is an int
                        years.add(int(equip.year))
                    # If it isn't an int, skip it
                    except (ValueError, TypeError):
                        # print("Uh Oh weird year") NOTE: There are quite a few cases where this is triggered, update DB
                        pass 

            # Convert sets to sorted lists
            return jsonify({
                "result": True,
                "farms": sorted(list(farms)),
                "classes": sorted(list(classes)),
                "makes": sorted(list(makes)),
                "years": sorted(list(years), reverse=True)
            })
            
        except Exception as e:
            print(f"Error getting filter options: {e}")
            return jsonify({"result": False, "error": str(e)})

    return app


# make sure to sanitize images for <script> tags, assigning UUID will happen in the back end
if __name__ == "__main__":
    app = create_app(testing=False)
    app.run(debug=os.environ.get("FLASK_DEBUG"), port=5000, use_reloader=False)
