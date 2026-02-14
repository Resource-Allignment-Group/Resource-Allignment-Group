import pymongo
import os
from pymongo import MongoClient
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
import io
from dotenv import load_dotenv
from user import User
from notifications import Notification
from bson.objectid import ObjectId
from equipment import Equipment
from typing import Literal
from datetime import timedelta
from logger import SystemLogger

_client = None  # Needed so that only one client call is made
load_dotenv()


class DatabaseManager:
    def get_client(self):
        global _client
        if _client is None:
            _client = MongoClient(os.environ.get("DATABASE_URI"))
        return _client

    def __init__(self, testing=False):
        self.get_client()
        if testing:
            self.db = _client["TEST_RAM_DB"]
            self.txt_logger = SystemLogger("test_log.txt")
        else:
            self.db = _client["RAM_DB"]
            self.txt_logger = SystemLogger("system_logs.txt")

        self.users_db = self.db["users"]
        self.equipment_db = self.db["equipment"]
        self.requests_db = self.db["requests"]
        self.notifications_db = self.db["notifications"]
        self.password_resets = self.db["password_resets"]
        self.images_db = Path("backend/large_files_db/images")
        self.reports_db = Path("backend/large_files_db/reports")
        self.profile_images_db = Path("backend/large_files_db/profile_images")

        #Byte file upload limits
        self.MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
        self.MAX_REPORT_SIZE = 10 * 1024 * 1024  # 10MB
        self.MAX_PROFILE_IMAGE_SIZE = 2 * 1024 * 1024  # 2MB

    def set_notfication_sender(self, id: ObjectId, sender: ObjectId):
        self.notifications_db.update_one({"_id": id}, {"$set": {"sender": sender}})

    def set_notfication_receiver(self, id: ObjectId, receiver: ObjectId):
        self.notifications_db.update_one({"_id": id}, {"$set": {"receiver": receiver}})

    def set_notfication_result(self, id: ObjectId, result: str):
        self.notifications_db.update_one({"_id": id}, {"$set": {"result": result}})

    def set_notification_read(self, id: ObjectId, read: bool):
        self.notifications_db.update_one({"_id": id}, {"$set": {"read": read}})

    def set_notification_status(self, id: ObjectId, status: Literal["a", "r", "p"]):
        self.notifications_db.update_one({"_id": id}, {"$set": {"status": status}})

    def set_notification_body(self, id: ObjectId, body: str):
        self.notifications_db.update_one({"_id": id}, {"$set": {"body": body}})

    def set_request_active(self, id: ObjectId, active: bool):
        self.requests_db.update_one({"_id": id}, {"$set": {"active": active}})

    def set_request_equipment(self, id: ObjectId, equipment_id: ObjectId):
        self.requests_db.update_one({"_id": id}, {"$set": {"equipment": equipment_id}})

    def set_request_user(self, id: ObjectId, user_id: ObjectId):
        self.requests_db.update_one({"_id": id}, {"$set": {"user": user_id}})

    def set_user_password(self, id: ObjectId, password: str):
        self.users_db.update_one({"_id": id}, {"$set": {"password": password}})

    def set_user_role(self, id: ObjectId, role: str):
        self.users_db.update_one({"_id": id}, {"$set": {"role": role}})

    def set_user_name(self, id: ObjectId, new_name: str):
        self.users_db.update_one({"_id": id}, {"$set": {"name": new_name}})

    def set_user_email(self, id: ObjectId, new_email: str):
        self.users_db.update_one({"_id": id}, {"$set": {"email": new_email}})

    def set_user_phone(self, id: ObjectId, new_phone: str):
        self.users_db.update_one({"_id": id}, {"$set": {"phone": new_phone}})

    def set_user_position(self, id: ObjectId, new_position: str):
        self.users_db.update_one({"_id": id}, {"$set": {"position": new_position}})

    def set_user_department(self, id: ObjectId, new_department: str):
        self.users_db.update_one({"_id": id}, {"$set": {"department": new_department}})

    def set_equipment_year(self, id: ObjectId, year: int):
        self.equipment_db.update_one({"_id": id}, {"$set": {"year": year}})

    def set_equipment_name(self, id: ObjectId, name: str):
        self.equipment_db.update_one({"_id": id}, {"$set": {"name": name}})

    def set_equipment_class(self, id: ObjectId, _class: str):
        self.equipment_db.update_one({"_id": id}, {"$set": {"class": _class}})

    def set_equipment_checked_out(self, id: ObjectId, checked_out: bool):
        self.equipment_db.update_one(
            {"_id": ObjectId(id)}, {"$set": {"checked_out": checked_out}}
        )

    def add_log(
        self,
        user_id: ObjectId,
        action: str,
        details: str = None,
        target_id: ObjectId = None,
    ):
        self.txt_logger.log_action(user_id, action, details, target_id)

    def add_user(
        self,
        fname: str,
        lname: str,
        phone: int,
        email: str,
        password,
        admin_id: ObjectId,
    ):
        if (
            self.users_db.count_documents({"email": email}) != 0
        ):  # Checks to make sure email does not already exist
            return {"result": False, "message": f"Email {email} already exists"}

        result = self.users_db.insert_one(
            {
                "password": password,
                "email": email,
                "role": "p",
                "checked_out_equipment": [],
                "inbox": [],
                "position": None,
                "name": fname.capitalize() + " " + lname.capitalize(),
                "phone": phone,
            }
        )

        if result.acknowledged:
            new_user_id = result.inserted_id

            self.add_log(
                user_id=admin_id,
                action="ADD_USER",
                details=f"Added new user: {email} (ID: {new_user_id})",
            )
            return {
                "result": True,
                "message": f"User {email} has sucessfully been added to the system",
            }
        else:
            return {
                "result": False,
                "message": f"User {email} has not been added to the system",
            }

    def add_equipment(self, equipment: Equipment):
        if not isinstance(equipment, Equipment):
            return "This is not part of the equipment class"

        if (
            equipment.id is None
            or self.equipment_db.count_documents(({"_id": equipment.id})) != 0
        ):  # Check to see if it has a valid ID
            equipment.id = str(ObjectId())

        self.equipment_db.insert_one(
            {
                "_id": equipment.id,
                "name": equipment.name,
                "class": equipment._class,
                "year": equipment.year,
                "farm": equipment.farm,
                "model": equipment.model,
                "make": equipment.make,
                "use": equipment.model,
                "images": [],
                "reports": [],
                "display_image": None,
                "checked_out": False,
                "description": equipment.description,
                "damaged": equipment.damaged,
                "unavailable": equipment.unavailable if hasattr(equipment, 'unavailable') else False,
            }
        )

    def add_user_equipment(
        self, user_id: ObjectId, equipment_id: ObjectId, admin_id: ObjectId
    ):
        equipment = self.equipment_db.find_one({"_id": equipment_id})

        if equipment["checked_out"] is True:
            return f"Equipment {equipment_id} is already checked out"

        self.users_db.update_one(
            {"_id": user_id}, {"$addToSet": {"checked_out_equipment": equipment_id}}
        )

        self.equipment_db.update_one(
            {"_id": equipment_id}, {"$set": {"checked_out": True}}
        )
        self.add_log(
            user_id=admin_id,
            action="CHECK_OUT",
            target_id=equipment_id,
            details=f"Assigned to user: {user_id}",
        )

    def delete_user_equipment(self, user_id: ObjectId, equipment_id: ObjectId, damaged: bool = False, damage_description: str | None = None):
        equipment = self.equipment_db.find_one({"_id": equipment_id})

        if not equipment or not equipment.get("checked_out"):
            return f"Equipment {equipment_id} is not checked out"

        self.users_db.update_one(
            {"_id": user_id}, {"$pull": {"checked_out_equipment": equipment_id}}
        )

        self.equipment_db.update_one(
            {"_id": equipment_id}, {"$set": {"checked_out": False, "damaged": damaged}}
        )

        if damaged:
            status_msg = (
                "Item returned DAMAGED"
                + (f": {damage_description}" if damage_description else "")
            )
        else:
            status_msg = "Item returned in good condition"

        self.add_log(
            user_id=user_id,
            action="CHECK_IN",
            target_id=equipment_id,
            details=status_msg,
        )

    def get_password_by_email(self, email: str):
        return self.users_db.find_one({"email": email})["password"]

    def get_user_by_email(self, email: str) -> User:
        result = self.users_db.find_one({"email": email})

        if result is None:
            raise ValueError(f"No user with email {email}")

        user = User()
        user.fill_user_information(result)
        return user

    def get_user_by_id(self, user_id: ObjectId) -> User:
        new_user = User()
        new_user.fill_user_information(self.users_db.find_one({"_id": user_id}))
        return new_user

    def _ensure_dirs(self):
        self.images_db.mkdir(parents=True, exist_ok=True)
        self.reports_db.mkdir(parents=True, exist_ok=True)
        self.profile_images_db.mkdir(parents=True, exist_ok=True)

    def add_image(self, equipment_id: ObjectId, image_data: bytes, filename: str):
        """Add image to equipment. image_data is raw bytes, filename used for extension."""
        ext = Path(filename).suffix.lower()
        if ext not in (".png", ".jpg", ".jpeg"):
            return {"error": "Invalid file type. Allowed: PNG, JPG, JPEG"}
        if len(image_data) > self.MAX_IMAGE_SIZE:
            return {"error": f"File too large. Max size: {self.MAX_IMAGE_SIZE // (1024*1024)}MB"}

        self._ensure_dirs()
        img_uuid = str(ObjectId())
        storage_name = f"{img_uuid}{ext}"
        image_path = self.images_db / storage_name

        try:
            img = Image.open(io.BytesIO(image_data))
            img.save(image_path, format=img.format or "PNG")
        except Exception as e:
            return {"error": f"Invalid image file: {str(e)}"}

        #First image becomes the display image automatically
        equipment = self.equipment_db.find_one({"_id": equipment_id})
        updates = {"$push": {"images": storage_name}}
        if not equipment.get("images"):
            updates["$set"] = {"display_image": storage_name}
        change_result = self.equipment_db.update_one(
            {"_id": equipment_id}, updates
        )
        if change_result.acknowledged:
            return {"success": True, "id": storage_name}
        return {"error": "Failed to add image"}

    def add_report(self, equipment_id: ObjectId, report_data: bytes, filename: str):
        """Add report (PDF) to equipment."""
        ext = Path(filename).suffix.lower()
        if ext != ".pdf":
            return {"error": "Invalid file type. Allowed: PDF only"}
        if len(report_data) > self.MAX_REPORT_SIZE:
            return {"error": f"File too large. Max size: {self.MAX_REPORT_SIZE // (1024*1024)}MB"}

        self._ensure_dirs()
        report_uuid = str(ObjectId())
        storage_name = f"{report_uuid}.pdf"
        report_path = self.reports_db / storage_name

        with open(report_path, "wb") as f:
            f.write(report_data)

        change_result = self.equipment_db.update_one(
            {"_id": equipment_id}, {"$push": {"reports": storage_name}}
        )
        if change_result.acknowledged:
            return {"success": True, "id": storage_name}
        return {"error": "Failed to add report"}

    def set_equipment_display_image(self, equipment_id: ObjectId, image_id: str):
        """Set which image shows on equipment cards. image_id is the stored filename."""
        equipment = self.equipment_db.find_one({"_id": equipment_id})
        if not equipment or not equipment.get("images"):
            return False
        images = equipment.get("images", [])
        if image_id not in images:
            return False
        result = self.equipment_db.update_one(
            {"_id": equipment_id}, {"$set": {"display_image": image_id}}
        )
        return result.modified_count > 0

    def remove_equipment_image(self, equipment_id: ObjectId, image_id: str):
        """Remove image from equipment and clear display_image if it was this image."""
        path = self.images_db / image_id
        if path.exists():
            path.unlink()
        equip = self.equipment_db.find_one({"_id": equipment_id})
        if not equip:
            return False
        updates = {"$pull": {"images": image_id}}
        if equip.get("display_image") == image_id:
            updates["$unset"] = {"display_image": ""}
        result = self.equipment_db.update_one({"_id": equipment_id}, updates)
        return result.modified_count > 0

    def remove_equipment_report(self, equipment_id: ObjectId, report_id: str):
        """Remove report from equipment."""
        path = self.reports_db / report_id
        if path.exists():
            path.unlink()
        result = self.equipment_db.update_one(
            {"_id": equipment_id}, {"$pull": {"reports": report_id}}
        )
        return result.modified_count > 0

    def get_image(self, image_id: str):
        """Get image bytes. image_id can be 'uuid' or 'uuid.png'."""
        if not image_id:
            return None
        base = image_id.split(".")[0] if "." in image_id else image_id
        for ext in [".png", ".jpg", ".jpeg"]:
            path = self.images_db / f"{base}{ext}"
            if path.exists():
                with open(path, "rb") as f:
                    return f.read()
        # Legacy: try exact match
        path = self.images_db / image_id
        if path.exists():
            with open(path, "rb") as f:
                return f.read()
        return None

    def get_image_content_type(self, image_id: str):
        """Get content type for image."""
        if not image_id:
            return "image/png"
        ext = Path(image_id).suffix.lower() if "." in image_id else ""
        if ext in (".jpg", ".jpeg"):
            return "image/jpeg"
        return "image/png"

    def delete_image(self, uuid: str):
        base = uuid.split(".")[0] if "." in uuid else uuid
        for ext in [".png", ".jpg", ".jpeg", ""]:
            path = self.images_db / (f"{base}{ext}" if ext else base)
            if path.exists():
                path.unlink()
                return

    def get_report(self, report_id: str):
        """Get report bytes. report_id is filename like 'uuid.pdf'."""
        path = self.reports_db / report_id
        if not path.exists():
            return None
        with open(path, "rb") as f:
            return f.read()

    def delete_report(self, report_id: str):
        path = self.reports_db / report_id
        if path.exists():
            path.unlink()

    def add_profile_image(self, user_id: ObjectId, image_data: bytes, filename: str):
        """Add or replace profile image for user."""
        ext = Path(filename).suffix.lower()
        if ext not in (".png", ".jpg", ".jpeg"):
            return {"error": "Invalid file type. Allowed: PNG, JPG, JPEG"}
        if len(image_data) > self.MAX_PROFILE_IMAGE_SIZE:
            return {"error": f"File too large. Max size: {self.MAX_PROFILE_IMAGE_SIZE // (1024*1024)}MB"}

        self._ensure_dirs()
        # Remove old profile image if exists
        user = self.users_db.find_one({"_id": user_id})
        if user and user.get("profile_image"):
            old_path = self.profile_images_db / user["profile_image"]
            if old_path.exists():
                old_path.unlink()

        img_uuid = str(ObjectId())
        storage_name = f"{img_uuid}{ext}"
        image_path = self.profile_images_db / storage_name

        try:
            img = Image.open(io.BytesIO(image_data))
            img.save(image_path, format=img.format or "PNG")
        except Exception as e:
            return {"error": f"Invalid image file: {str(e)}"}

        result = self.users_db.update_one(
            {"_id": user_id}, {"$set": {"profile_image": storage_name}}
        )
        if result.acknowledged:
            return {"success": True, "id": storage_name}
        return {"error": "Failed to add profile image"}

    def get_profile_image(self, image_id: str):
        """Get profile image bytes."""
        if not image_id:
            return None
        path = self.profile_images_db / image_id
        if path.exists():
            with open(path, "rb") as f:
                return f.read()
        return None

    def get_inbox_by_user(self, user_id: ObjectId):
        user_doc = self.users_db.find_one({"_id": user_id})
        if not user_doc:
            return []

        notification_ids = user_doc.get("inbox", [])
        return [self.notifications_db.find_one({"_id": n}) for n in notification_ids]

    # Get all notifs assigned to a given user in a single query
    def get_notifications_by_user(self, user_id):
        user = self.users_db.find_one({"_id": ObjectId(user_id)})
        if not user: return []
        inbox_ids = user.get("inbox", [])
        if not inbox_ids: return []
        
        object_ids = []
        for item in inbox_ids:
            try:
                # This may be able to simplified if we find out that the weird issue with notifs
                # was due to malformed old notifications. On DB clean, if this is still needed, 
                # the error is likely elswhere in the codebase.
                if isinstance(item, dict):
                    obj_id = item.get("_id") or item.get("id")
                    object_ids.append(ObjectId(obj_id))
                elif isinstance(item, ObjectId):
                    object_ids.append(item)
                else:
                    object_ids.append(ObjectId(item))
            except Exception as e:
                print(f"Error processing inbox item: {e}")
                continue
        
        if not object_ids: return []
        notification_docs = list(self.notifications_db.find({
            "_id": {"$in": object_ids}
        }))
        
        # Convert to Notification objects
        notes = []
        for note_info in notification_docs:
            note = Notification()
            note.populate_from_json(json_info=note_info)
            notes.append(note)
        
        return notes

    def get_notification_by_id(self, note_id):
        if isinstance(note_id, dict):
            note_info = note_id
        else:
            # If it's a string/ObjectId, query the database
            try:
                note_info = self.notifications_db.find_one({"_id": ObjectId(note_id)})
            except Exception:
                note_info = None

        # Create the Notification object
        note = Notification()
        # Only populate if we actually found data
        if note_info:
            note.populate_from_json(json_info=note_info)
        else:
            return None

        return note

    def get_notifications_by_equipment(self, equip_id):
        note_info = self.notifications_db.find_one({"equipment_id": ObjectId(equip_id)})
        note = Notification()
        note.populate_from_json(json_info=note_info)
        return note

    def delete_notification(self, note_id):
        self.notifications_db.delete_one({"_id": ObjectId(note_id)})
        return True

    def get_email_by_id(self, user_id: str):
        user = self.users_db.find_one({"_id": ObjectId(user_id)})
        if user:
            return user.get("email", "No Email Found")
        return "Deleted User"

    def get_administrators(self):
        cursor = self.users_db.find({"role": "a"})
        user_list = []

        for user_info in cursor:
            user = User()
            user.fill_user_information(user_info)
            user_list.append(user)
        return user_list

    # Remove a notif from a user's inbox
    def remove_notification_from_inbox(self, notification):
        # Remove from all users who have it in their inbox
        self.users_db.update_many(
            {"inbox": ObjectId(notification.id)},
            {"$pull": {"inbox": ObjectId(notification.id)}}
        )
        return True
    
    # Delete a notification from the users inbox and the DB
    def delete_notification_completely(self, note_id):
        note_id_obj = ObjectId(note_id)
        # Remove from all user inboxes
        self.users_db.update_many(
            {"inbox": note_id_obj},
            {"$pull": {"inbox": note_id_obj}}
        )
        # Delete the notification from DB
        self.notifications_db.delete_one({"_id": note_id_obj})
        return True

    def send_notification(self, notification: Notification):
        if notification.id is None:
            notification.id = ObjectId()
        notification_json = {
            "_id": notification.id,
            "sender": notification.sender,
            "receiver": notification.receiver,
            "body": notification.body,
            "date": notification.date,
            "type": notification.type,
            "equipment_id": notification.equipment_id,
            "read": notification.read,
            "status": notification.status,
        }
        result_user = self.users_db.update_one(
            {"_id": notification.receiver}, {"$push": {"inbox": notification.id}}
        )
        result_note = self.notifications_db.insert_one(notification_json)

        if result_note.acknowledged and result_user.acknowledged:
            return {
                "result": True,
                "message": "Notification has sucessfully been added to the system",
            }
        else:
            return {
                "result": False,
                "message": "Notidication has not been added to the system",
            }

    def get_all_equipment(self):
        cursor = self.equipment_db.find({})
        equip_list = []
        for equip_info in cursor:
            equip = Equipment()
            equip.fill_from_json(equip_info)
            equip_list.append(equip)
        return equip_list

    # Allows you to edit a specific field on an equipment
    def update_equipment_field(self, equip_id, field_name, value):  #### I Don't think that this function if being called from anywhere?
        try:
            result = self.equipment_db.update_one(
                {"_id": ObjectId(equip_id)}, {"$set": {field_name: value}}
            )
            return result.modified_count > 0
        except:
            return False

    def get_equipment_by_id(self, id: ObjectId):
        equip_info = self.equipment_db.find_one({"_id": ObjectId(id)})
        if not equip_info:  # Added for handling when equipment doesnt exist
            return None

        equip = Equipment()
        equip.fill_from_json(json_info=equip_info)
        return equip

    # Get multiple equipment items from a list of ids
    def get_equipment_by_ids(self, equipment_ids: list):
        cursor = self.equipment_db.find({"_id": {"$in": equipment_ids}})
        equip_list = []
        for equip_info in cursor:
            equip = Equipment()
            equip.fill_from_json(equip_info)
            equip_list.append(equip)
        return equip_list

    def get_equipment_by_user(self, user_id: ObjectId):
        equip_list = []
        user = self.users_db.find_one({"_id": user_id})
        if not user:
            return []
        for equip_id in user["checked_out_equipment"]:
            equip_list.append(self.get_equipment_by_id(id=equip_id))
        return equip_list

    def remove_equipment_from_inbox(self, equip_id: ObjectId, user_id: ObjectId):
        self.users_db.update_one(
            {"_id": user_id},
            {"$pull": {"checked_out_equipment": equip_id}},
        )

    def get_unread_messages_by_user(self, user_id: ObjectId):
        note_infos = self.notifications_db.find({"receiver": user_id, "read": False})
        note_list = []
        for note_info in note_infos:
            note = Notification()
            note.populate_from_json(json_info=note_info)
            note_list.append(note)
        return note_list

    def get_requests_by_user(self, user_id: ObjectId):
        user = self.get_user_by_id(user_id=user_id)
        requests = self.notifications_db.find({"type": "r", "sender": user.id})
        request_list = []
        equipment_list = []
        for request in requests:
            new_request = Notification()
            new_request.populate_from_json(json_info=request)
            request_list.append(new_request)
            equipment_list.append(self.get_equipment_by_id(id=new_request.equipment_id))

        return request_list, equipment_list

    def get_dashboard_info(self):
        num_total = self.equipment_db.count_documents({})
        num_available = self.equipment_db.count_documents(
            {
                "checked_out": {"$ne": True},
                "damaged": {"$ne": True},
                "unavailable": {"$ne": True},
            }
        )
        num_used = self.equipment_db.count_documents({"checked_out": True})
        num_damaged = self.equipment_db.count_documents({"damaged": True})
        num_unavailable = self.equipment_db.count_documents({"unavailable": True})
        return num_total, num_available, num_used, num_damaged, num_unavailable

    def get_all_users(self):
        all_users = []
        users = self.users_db.find({})
        for user_info in users:
            all_users.append(self.get_user_by_id(user_id=ObjectId(user_info["_id"])))
        return all_users

    # See what equipment a user has checked out
    def get_user_by_equipment(self, equipment_id: ObjectId):
        user_info = self.users_db.find_one({"checked_out_equipment": equipment_id})

        if user_info:
            user = User()
            user.fill_user_information(user_info)
            return user
        return None

    # This is your version with the admin_id (Keep this)
    def delete_user(self, user: User, admin_id: ObjectId):
        for equipment_id in user.checked_out_equipment:
            self.equipment_db.update_one(
                {"_id": equipment_id}, {"$set": {"checked_out": False}}
            )

        result = self.users_db.delete_one({"_id": user.id})
        if result.acknowledged:
            self.add_log(
                user_id=admin_id, action="DELETE_USER", details=f"{user.id} is deleted"
            )
            return True
        else:
            return False

    def create_password_reset(self, user_id: ObjectId, token, token_hash):
        self.password_resets.insert_one(
            {
                "_id": ObjectId(),
                "user_id": user_id,
                "token_hash": token_hash,
                "expires_at": datetime.now(timezone.utc) + timedelta(minutes=5),
                "used": False,
            }
        )
        link = f"http://${os.environ.get('REACT_APP_API_BASE')}:3000/reset-password?token={token}"  # This will need to change when we host
        return link

    def get_password_reset(self, token_hash):
        return self.password_resets.find_one({"token_hash": token_hash, "used": False})

    def set_password_reset_used(self, id: ObjectId, used: bool):
        self.password_resets.update_one({"_id": id}, {"$set": {"used": used}})

    # Cancels pending equipment requests for equipment that have been
    # assigned to someone else, deleted, marked unavailable, etc based on a list of equip IDs
    # You can also, optionally, specify a notification ID to exclude an equip item
    # from being denied (when only one user is approved to chekout an equip, it cancels for all others)
    def cancel_pending_requests_for_equipment(self, equipment_ids: list, exclude_notification_id: ObjectId = None):
        query = {
            "equipment_id": {"$in": equipment_ids},
            "type": "r",
            "status": "p"  # Only pending
        }
        
        # If we want to exclude a specific notification (e.g., the one being approved)
        if exclude_notification_id is not None:
            query["_id"] = {"$ne": exclude_notification_id}
        
        result = self.notifications_db.update_many(
            query,
            {"$set": {"status": "r"}}
        )
        return result.modified_count
    
    # Get IDs of pending requests for specific equipment before denying them
    # Used to remove them from admin inboxes and notify affected users
    def get_pending_request_info(self, equipment_ids: list, exclude_notification_id: ObjectId = None):
        query = {
            "equipment_id": {"$in": equipment_ids},
            "type": "r",
            "status": "p"  # Pending
        }
        
        if exclude_notification_id is not None:
            query["_id"] = {"$ne": exclude_notification_id}
        
        denied_requests = self.notifications_db.find(query, {"_id": 1, "sender": 1})
        
        notification_ids = []
        # Use set to avoid duplicate user IDs
        sender_ids = set()
        
        for req in denied_requests:
            notification_ids.append(req["_id"])
            sender_ids.add(ObjectId(req["sender"]))
        
        return notification_ids, list(sender_ids)

    # Remove a notification from all admin inboxes 
    # EX: An equip is approved to a usr, all notifs requesting that same equip are removed
    def remove_notifications_from_all_admin_inboxes(self, notification_ids: list):
        if not notification_ids:
            return 0
        result = self.users_db.update_many(
            {"role": "a"},
            {"$pullAll": {"inbox": notification_ids}}
        )
        return result.modified_count

    # Update multiple equipment items as unavailable at once
    def bulk_update_equipment_unavailable(self, equipment_ids: list, unavailable: bool):
        if not equipment_ids:
            return 0

        result = self.equipment_db.update_many(
            {
                "_id": {"$in": equipment_ids},
                "checked_out": False,
                "damaged": False,
            },
            {"$set": {"unavailable": unavailable}},
        )
        return result.modified_count

    def delete_equipment(self, equipment_id: ObjectId):
        equipment = self.equipment_db.find_one({"_id": equipment_id})
        if not equipment:
            return False

        # Remove equipment from all users' checked_out_equipment arrays
        self.users_db.update_many(
            {"checked_out_equipment": equipment_id},
            {"$pull": {"checked_out_equipment": equipment_id}},
        )

        # Update all notifications referencing this equipment to mark as deleted
        notifications = self.notifications_db.find({"equipment_id": equipment_id})
        for notification in notifications:
            current_body = notification["body"] if "body" in notification else ""
            # Add [DELETED] prefix if not already present
            if not current_body.startswith("[DELETED]"):
                updated_body = f"[DELETED] {current_body}"
                self.notifications_db.update_one(
                    {"_id": notification["_id"]},
                    {"$set": {"body": updated_body}}
                )

        # Delete associated image files
        if "images" in equipment and equipment["images"]:
            for image_id in equipment["images"]:
                if image_id:
                    self.delete_image(str(image_id))

        # Delete associated report files
        if "reports" in equipment and equipment["reports"]:
            for report_id in equipment["reports"]:
                if report_id:
                    path = self.reports_db / str(report_id)
                    if path.exists():
                        path.unlink()

        # Finally, delete the equipment document itself
        result = self.equipment_db.delete_one({"_id": equipment_id})
        return result.acknowledged and result.deleted_count > 0
