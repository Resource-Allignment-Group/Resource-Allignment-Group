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
        self.images_db.mkdir(parents=True, exist_ok=True)
        self.reports_db.mkdir(parents=True, exist_ok=True)
        self.profile_images_db.mkdir(parents=True, exist_ok=True)
        self.ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}
        self.MAX_IMAGE_SIZE = 5 * 1024 * 1024
        self.ALLOWED_REPORT_EXTENSIONS = {".pdf"}
        self.MAX_REPORT_SIZE = 10 * 1024 * 1024
        self.MAX_PROFILE_IMAGE_SIZE = 2 * 1024 * 1024
        self.allowed_fields = {
            "_id",
            "name",
            "class",
            "year",
            "farm",
            "model",
            "make",
            "use",
            "images",
            "reports",
            "checked_out",
            "description",
            "damaged",
            "unavailable",
            "replacement_cost",
            "display_image",
        }

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
        self.notifications_db.update_one({"_id":id}, {"$set": {"body": body}})

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
        # Might have to change notifications that use this depending on functionality
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

    # Update the users preference to receive automatic monthly reports
    def update_admin_report_preference(self, admin_id: ObjectId, action: bool):
        try:
            # Use the internal collection (likely self.db.users or similar)
            # Check if your class uses 'self.db' or 'self.client' internally
            self.users_db.update_one(
                {"_id": ObjectId(admin_id)},
                {"$set": {"receive_reports": action}}
            )
            return True
        except Exception:
            return False

    def add_log(
        self,
        user_id: ObjectId,
        action: str,
        details: str = "",
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
                "name": fname + " " + lname,
                "phone": phone,
            }
        )

        if result.acknowledged:
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
                "unavailable": getattr(equipment, "unavailable", False),
            }
        )

    def add_user_equipment(
        self, user_id: ObjectId, equipment_id: ObjectId, admin_name: str
    ):
        equipment = self.equipment_db.find_one({"_id": equipment_id})
        user = self.users_db.find_one({"_id": user_id})

        if equipment["checked_out"] is True:
            return f"Equipment {equipment_id} is already checked out"

        self.users_db.update_one(
            {"_id": user_id}, {"$addToSet": {"checked_out_equipment": equipment_id}}
        )

        self.equipment_db.update_one(
            {"_id": equipment_id}, {"$set": {"checked_out": True}}
        )
        self.add_log(
            user_id=admin_name,
            action="CHECK_OUT",
            target_id=f"{equipment['name']}",
            details=f"{user['name']} : {user['email']}",
        )

    def delete_user_equipment(self, user_id: ObjectId, equipment_id: ObjectId, damaged: bool = False, damage_description: str | None = None):
        equipment = self.equipment_db.find_one({"_id": equipment_id})
        user = self.users_db.find_one({"_id": user_id})

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
            user_id=f"{user['name']}",
            action="CHECK_IN",
            target_id=f"{equipment.get('name')}",
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

    def add_image(self, equipment_id: ObjectId, image: Image):
        img_uuid = str(ObjectId())
        image_path = self.images_db / img_uuid
        image.save(image_path)
        while True:
            if (self.images_db / img_uuid).exists():
                img_uuid = str(ObjectId())
            else:
                break
        image.save(self.images_db / img_uuid)

        change_result = self.equipment_db.update_one(
            {"_id": equipment_id}, {"$push": {"images": img_uuid}}
        )
        if change_result.acknowledged:
            return f"Image {img_uuid} has been added for {equipment_id}"
        else:
            return f"Image {img_uuid} could not be added"

    def add_report(self, equipment_id: ObjectId, report_content):
        report_uuid = str(ObjectId())
        while True:
            if (self.reports_db / report_uuid).exists():
                report_uuid = str(ObjectId())
            else:
                break

        with open(self.reports_db / report_uuid, "w") as f:
            f.write(report_content)

        change_result = self.equipment_db.update_one(
            {"_id": equipment_id}, {"$push": {"reports": report_uuid}}
        )
        if change_result.acknowledged:
            return f"Report {report_uuid} has been added for {equipment_id}"
        else:
            return f"Report {report_uuid} could not be added"

    def get_image(self, uuid: str):
        if not (self.images_db / uuid).exists():
            return f"{uuid} image does not exist"

        img = Image.open(self.images_db / uuid)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")

        return buffer.getvalue()

    def delete_image(self, uuid: str):
        path = self.images_db / uuid
        if path.exists():
            path.unlink()

    def get_report(self, uuid: str):
        if not (self.reports_db / uuid).exists():
            return f"{uuid} report does not exist"

        with open(self.reports_db / uuid, "rb") as f:
            report_data = io.BytesIO(f.read())

        return report_data

    def delete_report(self, uuid: str):
        path = self.reports_db / uuid
        if path.exists():
            path.unlink()

    def add_equipment_image(self, equipment_id: ObjectId, file) -> tuple:
        if not file or not file.filename:
            return None,
        ext = Path(file.filename).suffix.lower()
        if ext not in self.ALLOWED_IMAGE_EXTENSIONS:
            return None, f"Invalid file type"
        file.seek(0, 2)
        size = file.tell()
        file.seek(0)
        if size > self.MAX_IMAGE_SIZE:
            return None, f"File too large. Max size: {self.MAX_IMAGE_SIZE // (1024*1024)}MB"
        try:
            img = Image.open(file)
            img.verify()
        except Exception:
            return None, "Invalid image file"
        file.seek(0)
        img_uuid = str(ObjectId())
        image_path = self.images_db / img_uuid
        with open(image_path, "wb") as f:
            f.write(file.read())
        change_result = self.equipment_db.update_one(
            {"_id": equipment_id}, {"$push": {"images": img_uuid}}
        )
        if change_result.acknowledged:
            return img_uuid, None
        image_path.unlink(missing_ok=True)
        return None, "Failed to add image to equipment"

    def add_equipment_report(self, equipment_id: ObjectId, file) -> tuple:
        if not file or not file.filename:
            return None, "No file provided"
        ext = Path(file.filename).suffix.lower()
        if ext not in self.ALLOWED_REPORT_EXTENSIONS:
            return None, f"Invalid file type. Allowed: PDF only"
        file.seek(0, 2)
        size = file.tell()
        file.seek(0)
        if size > self.MAX_REPORT_SIZE:
            return None, f"File too large. Max size: {self.MAX_REPORT_SIZE // (1024*1024)}MB"
        report_uuid = str(ObjectId())
        report_path = self.reports_db / report_uuid
        with open(report_path, "wb") as f:
            f.write(file.read())
        change_result = self.equipment_db.update_one(
            {"_id": equipment_id}, {"$push": {"reports": report_uuid}}
        )
        if change_result.acknowledged:
            return report_uuid, None
        report_path.unlink(missing_ok=True)
        return None, "Failed to add report to equipment"

    def set_equipment_display_image(self, equipment_id: ObjectId, image_id: str) -> bool:
        equipment = self.equipment_db.find_one({"_id": equipment_id})
        if not equipment:
            return False
        images = equipment["images"] if equipment["images"] else []
        if image_id not in images:
            return False
        self.equipment_db.update_one(
            {"_id": equipment_id}, {"$set": {"display_image": image_id}}
        )
        return True

    def remove_equipment_image(self, equipment_id: ObjectId, image_id: str) -> bool:
        equipment = self.equipment_db.find_one({"_id": equipment_id})
        if not equipment:
            return False
        images = equipment["images"] if equipment["images"] else []
        if image_id not in images:
            return False
        update_op = {"$pull": {"images": image_id}}
        if "display_image" in equipment and equipment["display_image"] == image_id:
            update_op["$unset"] = {"display_image": ""}
        self.equipment_db.update_one({"_id": equipment_id}, update_op)
        path = self.images_db / image_id
        path.unlink(missing_ok=True)
        return True

    def remove_equipment_report(self, equipment_id: ObjectId, report_id: str) -> bool:
        equipment = self.equipment_db.find_one({"_id": equipment_id})
        if not equipment:
            return False
        reports = equipment["reports"] if equipment["reports"] else []
        if report_id not in reports:
            return False
        self.equipment_db.update_one(
            {"_id": equipment_id}, {"$pull": {"reports": report_id}}
        )
        path = self.reports_db / report_id
        path.unlink(missing_ok=True)
        return True

    def add_profile_picture(self, user_id: ObjectId, file) -> tuple:
        if not file or not file.filename:
            return None, "No file provided"
        ext = Path(file.filename).suffix.lower()
        if ext not in self.ALLOWED_IMAGE_EXTENSIONS:
            return None, f"Invalid file type. Allowed: {', '.join(self.ALLOWED_IMAGE_EXTENSIONS)}"
        file.seek(0, 2)
        size = file.tell()
        file.seek(0)
        if size > self.MAX_PROFILE_IMAGE_SIZE:
            return None, f"File too large. Max size: {self.MAX_PROFILE_IMAGE_SIZE // (1024*1024)}MB"
        try:
            img = Image.open(file)
            img.verify()
        except Exception:
            return None, "Invalid image file"
        file.seek(0)
        img_uuid = str(ObjectId())
        image_path = self.profile_images_db / img_uuid
        with open(image_path, "wb") as f:
            f.write(file.read())
        user = self.users_db.find_one({"_id": user_id})
        if user and "profile_image" in user and user["profile_image"]:
            old_path = self.profile_images_db / user["profile_image"]
            old_path.unlink(missing_ok=True)
        self.users_db.update_one(
            {"_id": user_id}, {"$set": {"profile_image": img_uuid}}
        )
        return img_uuid, None

    def get_profile_image_id(self, user_id: ObjectId):
        user = self.users_db.find_one({"_id": user_id})
        if not user or "profile_image" not in user or not user["profile_image"]:
            return None
        return user["profile_image"]

    def delete_profile_picture(self, user_id: ObjectId) -> bool:
        user = self.users_db.find_one({"_id": user_id})
        if not user or "profile_image" not in user or not user["profile_image"]:
            return False
        img_id = user["profile_image"]
        path = self.profile_images_db / img_id
        path.unlink(missing_ok=True)
        self.users_db.update_one({"_id": user_id}, {"$unset": {"profile_image": ""}})
        return True

    def get_inbox_by_user(self, user_id: ObjectId):
        user_doc = self.users_db.find_one({"_id": user_id})
        if not user_doc: return []
        notification_ids = user_doc.get("inbox", [])
        if not notification_ids: return []
        # Get the notifs in the user inbox in 1 DB fetch
        notifications = list(self.notifications_db.find({"_id": {"$in": notification_ids}}))
        # Sort them by date
        notifications.sort(key=lambda n: n["date"])
        return notifications

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
        # result_note = self.notifications_db.insert_one(notification_json)
        result_note = self.notifications_db.update_one(
            {"_id": notification.id},
            {"$set": notification_json},
            upsert=True
        )

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
    def update_equipment_field(self, equip_id, field_name, value):
        if field_name not in self.allowed_fields:
            raise Exception(f"Field Name {field_name} is not permitted")
        result = self.equipment_db.update_one(
            {"_id": ObjectId(equip_id)},
            {"$set": {field_name: value}},
        )
        return result.modified_count > 0

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

    # See what equipment a user has checked out to them based on an ID
    def get_user_by_equipment(self, equipment_id: ObjectId):
        user_info = self.users_db.find_one({"checked_out_equipment": equipment_id})

        if user_info:
            user = User()
            user.fill_user_information(user_info)
            return user
        return None
    
    # See what equipment a user has checked out to them based on a list of equipment IDs
    def get_users_by_equipment_ids(self, equipment_ids: list[ObjectId]):
        users_info = self.users_db.find({"checked_out_equipment": {"$in": equipment_ids}})
        users = []
        for user_info in users_info:
            user = User()
            user.fill_user_information(user_info)
            users.append(user)
        return users

    def delete_user(self, user: User, admin_name: str, reason: str = "DELETED"):
        for equipment_id in user.checked_out_equipment:
            self.equipment_db.update_one(
                {"_id": equipment_id}, {"$set": {"checked_out": False}}
            )
        
        # Check to see if regular account deleting or account registration denied
        if reason == "DENIED":
            log_details = "Registration Request Denied by Admin"
        else:
            log_details = "Account Removed by Admin"

        user_info = f"{user.name} : {user.email}"
        if user.profile_image:
            profile_path = self.profile_images_db / user.profile_image
            profile_path.unlink(missing_ok=True)
        result = self.users_db.delete_one({"_id": user.id})
        if result.acknowledged:
            self.add_log(
                user_id=admin_name, 
                action="DELETE_USER", 
                target_id=user_info,
                details=log_details
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
        # Also mark them as read to keep the notif red bubble accurate
        result = self.notifications_db.update_many(
            {"_id": {"$in": notification_ids}},
            {"$set": {"read": True}}
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

        # Delete all notifications referencing this equipment
        notifications = self.notifications_db.find({"equipment_id": equipment_id})
        for notification in notifications:
            # Remove notification from users' inbox arrays
            self.users_db.update_many(
                {"inbox": notification["_id"]},
                {"$pull": {"inbox": notification["_id"]}},
            )
        # Delete the notifications
        self.notifications_db.delete_many({"equipment_id": equipment_id})

        # Delete associated image files
        if "images" in equipment and equipment["images"]:
            for image_id in equipment["images"]:
                if image_id:
                    path = self.images_db / str(image_id)
                    if path.exists():
                        path.unlink()

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
