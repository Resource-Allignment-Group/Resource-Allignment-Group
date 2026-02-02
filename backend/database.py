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
        else:
            self.db = _client["RAM_DB"]
        self.users_db = self.db["users"]
        self.equipment_db = self.db["equipment"]
        self.requests_db = self.db["requests"]
        self.notifications_db = self.db["notifications"]
        self.password_resets = self.db["password_resets"]
        self.images_db = Path("backend/large_files_db/images")
        self.reports_db = Path("backend/large_files_db/reports")

    # Setters
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

    def set_equipment_year(self, id: ObjectId, year: int):
        self.equipment_db.update_one({"_id": id}, {"$set": {"year": year}})

    def set_equipment_name(self, id: ObjectId, name: str):
        self.equipment_db.update_one({"_id": id}, {"$set": {"name": name}})

    def set_equipment_class(self, id: ObjectId, _class: str):
        self.equipment_db.update_one({"_id": id}, {"$set": {"class": _class}})

    def set_equipment_checked_out(self, id: ObjectId, checked_out: bool):
        self.equipment_db.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"checked_out": checked_out}}
        )

    def add_user(self, fname: str, lname: str, phone: int, email: str, password):
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
                "name": fname.capitalize() + lname.capitalize(),
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
                "checked_out": False,
                "description": equipment.description,
                "damaged": equipment.damaged,
            }
        )

    def add_user_equipment(self, user_id: ObjectId, equipment_id: ObjectId):
        equipment = self.equipment_db.find_one({"_id": equipment_id})

        if equipment["checked_out"] is True:
            return f"Equipment {equipment_id} is already checked out"

        self.users_db.update_one(
            {"_id": user_id}, {"$addToSet": {"checked_out_equipment": equipment_id}}
        )

        self.equipment_db.update_one(
            {"_id": equipment_id}, {"$set": {"checked_out": True}}
        )

    def delete_user_equipment(self, user_id: ObjectId, equipment_id: ObjectId):
        equipment = self.equipment_db.find_one({"_id": equipment_id})

        if not equipment["checked_out"]:
            return f"Equipment {equipment_id} is not checked out"

        self.users_db.update_one(
            {"_id": user_id}, {"$pull": {"checked_out_equipment": equipment_id}}
        )
        self.equipment_db.update_one(
            {"_id": equipment_id}, {"$set": {"checked_out": False}}
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
        img_uuid = ObjectId()
        while True:
            if (self.images_db / img_uuid).exists():
                img_uuid = ObjectId()
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
        report_uuid = ObjectId()
        while True:
            if (self.reports_db / report_uuid).exists():
                report_uuid = ObjectId()
            else:
                break

        with open(self.reports_db / report_uuid, "w") as f:
            f.write(report_content)
        f.close()
        change_result = self.equipment_db.update_one(
            {"_id": equipment_id}, {"$push": {"reports": report_uuid}}
        )
        if change_result.acknowledged:
            return f"Report {report_uuid} has been added for {equipment_id}"
        else:
            return f"Report {report_uuid} could not be added"

    def get_image(self, uuid: ObjectId):
        if type(uuid) is not ObjectId:
            return f"{uuid} is not a ObjectId"

        if not (self.images_db / uuid).exists():
            return f"{uuid} image does not exist"

        img = Image.open(self.images_db / uuid)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")

        return buffer.getvalue()

    def delete_image(self, uuid: ObjectId):
        os.remove(self.images_db / uuid)

    def get_report(self, uuid: ObjectId):
        if type(uuid) is not ObjectId:
            return f"{uuid} is not a ObjectId"

        if not (self.images_db / uuid).exists():
            return f"{uuid} report does not exist"

        with open(self.reports_db / uuid, "rb") as f:
            report_data = io.BytesIO(f.read())

        return report_data

    def delete_report(self, uuid: ObjectId):
        os.remove(self.reports_db / uuid)

    def get_inbox_by_user(self, user_id: ObjectId):
        user_doc = self.users_db.find_one({"_id": user_id})
        if not user_doc:
            return 0

        notification_ids = user_doc.get("inbox", [])
        return [self.notifications_db.find_one({"_id": n}) for n in notification_ids]

    def get_notifications_by_user(self, user_id):
        user = self.users_db.find_one({"_id": ObjectId(user_id)})
        notes = []
        for note_id in user["inbox"]:
            notes.append(self.get_notification_by_id(note_id=note_id))
        return notes

    def get_notification_by_id(self, note_id):
        note_info = self.notifications_db.find_one({"_id": ObjectId(note_id)})
        note = Notification()
        note.populate_from_json(json_info=note_info)
        return note

    def get_notifications_by_equipment(self, equip_id):
        note_info = self.notifications_db.find_one({"equipment_id": ObjectId(equip_id)})
        note = Notification()
        note.populate_from_json(json_info=note_info)
        return note

    def delete_notification(self, note_id):
        res = self.notifications_db.delete_one({"_id": note_id})
        return True

    def get_email_by_id(self, user_id: str):
        user = self.users_db.find_one({"_id": ObjectId(user_id)})
        return user["email"]

    def get_administrators(self):
        cursor = self.users_db.find({"role": "a"})
        user_list = []

        for user_info in cursor:
            user = User()
            user.fill_user_information(user_info)
            user_list.append(user)
        return user_list

    def remove_notification_from_inbox(self, notification: Notification):
        result = self.users_db.update_many(
            {"inbox": ObjectId(notification.id)},
            {"$pull": {"inbox": ObjectId(notification.id)}},
        )
        self.notifications_db.update_one(
            {"_id": notification.id}, {"$set": {"read": True}}
        )
        return result

    def send_notification(self, notification: Notification):
        if notification.id is None:
            notification.id = ObjectId()
        notification_json = notification_json = {
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
    def update_equipment_field(self, equip_id, field_name, value):
        try:
            result = self.equipment_db.update_one(
                {"_id": ObjectId(equip_id)},
                {"$set": {field_name: value}}
            )

            updated = self.equipment_db.find_one({"_id": ObjectId(equip_id)})

            return result.modified_count > 0
        except:
            return False

    def get_equipment_by_id(self, id: ObjectId):
        equip_info = self.equipment_db.find_one({"_id": ObjectId(id)})
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

        for equip_id in self.users_db.find_one({"_id": user_id})[
            "checked_out_equipment"
        ]:
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
        num_available = self.equipment_db.count_documents({
            "checked_out": {"$ne": True},
            "damaged": {"$ne": True},
            "unavailable": {"$ne": True}
        })
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
        user_info = self.users_db.find_one({
            "checked_out_equipment": equipment_id
        })
        
        if user_info:
            user = User()
            user.fill_user_information(user_info)
            return user
        return None

    def delete_user(self, user: User):
        [
            self.equipment_db.update_one(
                {"_id": equipment_id}, {"$set", {"checked_out": False}}
            )
            for equipment_id in user.checked_out_equipment
        ]

        result = self.users_db.delete_one({"_id": user.id})
        if result.acknowledged:
            return True
        else:
            return False

    def create_password_reset(self, user_id: ObjectId, token, token_hash):
        print(self.password_resets)
        res = self.password_resets.insert_one(
            {
                "_id": ObjectId(),
                "user_id": user_id,
                "token_hash": token_hash,
                "expires_at": datetime.now(timezone.utc) + timedelta(minutes=5),
                "used": False,
            }
        )
        print(res)
        link = f"http://localhost:3000/reset-password?token={token}"  # This will need to change when we host
        return link

    def get_password_reset(self, token_hash):
        return self.password_resets.find_one({"token_hash": token_hash, "used": False})

    def set_password_reset_used(self, id: ObjectId, used: bool):
        self.password_resets.update_one({"_id": id}, {"$set": {"used": used}})

    # If equipment marked as unavailable and there is a pending 
    # request for checkout, cancel the request
    def cancel_pending_requests_for_equipment(self, equipment_ids: list):
        result = self.notifications_db.update_many(
            {
                "equipment_id": {"$in": equipment_ids},
                "type": "r",
                "status": {"$ne": "a"}  # Not approved
            },
            {"$set": {"status": "r"}}  # Set to rejected
        )
        return result.modified_count
    
    # Update multiple equipment items as unavailable at once
    def bulk_update_equipment_unavailable(self, equipment_ids: list, unavailable: bool):
        result = self.equipment_db.update_many(
            {"_id": {"$in": equipment_ids}},
            {"$set": {"unavailable": unavailable}}
        )
        return result.modified_count
