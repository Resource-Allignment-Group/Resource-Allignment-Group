import pymongo
import os
from pymongo import MongoClient
from pathlib import Path
from datetime import datetime
from PIL import Image
import io
from dotenv import load_dotenv
from user import User
from notifications import Notification
from bson.objectid import ObjectId
from equipment import Equipment

_client = None  # Needed so that only one client call is made
load_dotenv()


class DatabaseManager:
    def get_client(self):
        global _client
        if _client is None:
            _client = MongoClient(os.environ.get("DATABASE_URI"))
        return _client

    def __init__(self):
        self.get_client()
        self.db = _client["RAM_DB"]
        self.users_db = self.db["users"]
        self.equipment_db = self.db["equipment"]
        self.requests_db = self.db["requests"]
        self.notifications_db = self.db["notifications"]
        self.images_db = Path("backend/large_files_db/images")
        self.reports_db = Path("backend/large_files_db/reports")

    # Setters
    def set_notfication_sender(self, id: ObjectId, sender: ObjectId):
        self.notifications_db.update_one({"_id": id}, {"$set": {"sender": sender}})

    def set_notfication_receiver(self, id: ObjectId, receiver: ObjectId):
        self.notifications_db.update_one({"_id": id}, {"$set": {"receiver": receiver}})

    def set_notfication_result(self, id: ObjectId, result: str):
        self.notifications_db.update_one({"_id": id}, {"$set": {"result": result}})

    def set_request_active(self, id: ObjectId, active: bool):
        self.requests_db.update_one({"_id": id}, {"$set": {"active": active}})

    def set_request_equipment(self, id: ObjectId, equipment_id: ObjectId):
        self.requests_db.update_one({"_id": id}, {"$set": {"equipment": equipment_id}})

    def set_request_user(self, id: ObjectId, user_id: ObjectId):
        self.requests_db.update_one({"_id": id}, {"$set": {"user": user_id}})

    def set_user_username(self, id: ObjectId, username: str):
        self.users_db.update_one({"_id": id}, {"$set": {"username": username}})

    def set_user_password(self, id: ObjectId, password: str):
        self.users_db.update_one({"_id": id}, {"$set": {"password": password}})

    def set_user_role(self, id: ObjectId, role: str):
        self.users_db.update_one({"_id": id}, {"$set": {"role": role}})

    def set_equipment_year(self, id: ObjectId, year: int):
        self.equipment_db.update_one({"_id": id}, {"$set": {"year": year}})

    def set_equipment_name(self, id: ObjectId, name: str):
        self.equipment_db.update_one({"_id": id}, {"$set": {"name": name}})

    def set_equipment_class(self, id: ObjectId, _class: str):
        self.equipment_db.update_one({"_id": id}, {"$set": {"class": _class}})

    def set_equipment_checked_out(self, id: ObjectId, checked_out: bool):
        self.equipment_db.update_one(
            {"_id": id}, {"$set": {"checked_out": checked_out}}
        )

    def add_user(self, email: str, password):
        if (
            self.users_db.count_documents({"username": email}) != 0
        ):  # Checks to make sure username does not already exist
            return {"result": False, "message": f"Username {email} already exists"}

        result = self.users_db.insert_one(
            {
                "username": email,
                "password": password,
                "role": "p",
                "checked_out_equipment": [],
                "inbox": [],
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
            }
        )

    def add_user_equipment(self, user_id: ObjectId, equipment_id: ObjectId):
        equipment = self.equipment_db.find_one({"_id": equipment_id})

        if equipment["checked_out"] is True:
            return f"Equipment {equipment_id} is already checked out"

        self.users_db.update_one(
            {"_id": user_id}, {"$push": {"checked_out_equipment": equipment_id}}
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

    def get_user_by_username(self, username: str) -> User:
        new_user = User()
        new_user.fill_user_information(
            list(self.users_db.find({"username": username}))[0]
        )
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
            return "User does not exist"

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
        note = Notification().populate_from_json(json_info=note_info)
        return note

    def get_username_by_id(self, user_id: str):
        user = self.users_db.find_one({"_id": ObjectId(user_id)})
        return user["username"]

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
        return result

    def send_notification(self, notification: Notification):
        if notification.id is None:
            notification.id = ObjectId()

        notification_json = {
            "_id": notification.id,
            "sender": notification.sender.id,
            "receiver": notification.receiver.id,
            "body": notification.body,
            "date": notification.date,
            "type": notification.type,
            "equipment_id": notification.equipment_id,
        }
        result_user = self.users_db.update_one(
            {"_id": notification.receiver.id}, {"$push": {"inbox": notification.id}}
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
        return self.equipment_db.find({})

    def get_equipment_by_id(self, id: ObjectId):
        equip_info = self.equipment_db.find_one({"_id": id})
        equip = Equipment()
        equip.fill_from_json(json_info=equip_info)
        return equip
