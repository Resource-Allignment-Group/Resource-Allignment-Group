import pymongo
import os
from pymongo import MongoClient
from pathlib import Path
from uuid import UUID, uuid4
import logging
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
    def set_notfication_sender(self, id: UUID, sender: UUID):
        change_result = self.notifications_db.update_one(
            {"_id": id}, {"$set": {"sender": sender}}
        )
        if change_result.acknowledged:
            return f"Sender {sender} has changed for notification {id}"
        else:
            return f"Sender was not changed for notification {id}"

    def set_notfication_receiver(self, id: UUID, receiver: UUID):
        change_result = self.notifications_db.update_one(
            {"_id": id}, {"$set": {"receiver": receiver}}
        )
        if change_result.acknowledged:
            return f"Receiver {receiver} has changed for notification {id}"
        else:
            return f"Receiver was not changed for notification {id}"

    def set_notfication_result(self, id: UUID, result: str):
        change_result = self.notifications_db.update_one(
            {"_id": id}, {"$set": {"result": result}}
        )
        if change_result.acknowledged:
            return f"Result {result} has changed for notification {id}"
        else:
            return f"Result was not changed for notification {id}"

    def set_request_active(self, id: UUID, active: bool):
        change_result = self.requests_db.update_one(
            {"_id": id}, {"$set": {"active": active}}
        )
        if change_result.acknowledged:
            return f"Active {active} has changed for request {id}"
        else:
            return f"Active was not changed for request {id}"

    def set_request_equipment(self, id: UUID, equipment_id: UUID):
        change_result = self.requests_db.update_one(
            {"_id": id}, {"$set": {"equipment": equipment_id}}
        )
        if change_result.acknowledged:
            return f"Equipment {equipment_id} has changed for request {id}"
        else:
            return f"Equipment was not changed for request {id}"

    def set_request_user(self, id: UUID, user_id: UUID):
        change_result = self.requests_db.update_one(
            {"_id": id}, {"$set": {"user": user_id}}
        )
        if change_result.acknowledged:
            return f"User {user_id} has changed for request {id}"
        else:
            return f"User was not changed for request {id}"

    def set_user_username(self, id: UUID, username: str):
        change_result = self.users_db.update_one(
            {"_id": id}, {"$set": {"username": username}}
        )
        if change_result.acknowledged:
            return f"Username {username} has changed for user {id}"
        else:
            return f"Username was not changed for user {id}"

    def set_user_password(self, id: UUID, password: str):
        change_result = self.users_db.update_one(
            {"_id": id}, {"$set": {"password": password}}
        )
        if change_result.acknowledged:
            return f"Password {password} has changed for user {id}"
        else:
            return f"Password was not changed for user {id}"

    def set_user_role(self, id: UUID, role: str):
        change_result = self.users_db.update_one({"_id": id}, {"$set": {"role": role}})
        if change_result.acknowledged:
            return f"Role {role} has changed for user {id}"
        else:
            return f"Role was not changed for user {id}"

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
        ):
            equipment.id = str(uuid4())

        print(equipment.id)
        result = self.equipment_db.insert_one(
            {
                "_id": equipment.id,
                "name": equipment.name,
                "class": equipment._class,
                "year": equipment.year,
                "images": [],
                "reports": [],
                "checked_out": False,
            }
        )
        print(result.acknowledged)

    def add_user_equipment(self, user_id: UUID, equipment_id: UUID):
        equipment = self.equipment_db.find_one({"_id": equipment_id})
        if equipment["checked_out"]:
            return f"Equipment {equipment_id} is already checked out"

        change_result = self.users_db.update_one(
            {"_id": user_id}, {"$push": {"checked_out_equipment": equipment_id}}
        )
        if change_result.acknowledged:
            self.equipment_db.update_one(
                {"_id": equipment_id}, {"$set": {"checked_out": True}}
            )
            return f"User {user_id} has checked out equipment {equipment_id}"
        else:
            return f"User {user_id} was unable to check out equipment {equipment_id}"

    def delete_user_equipment(self, user_id: UUID, equipment_id: UUID):
        equipment = self.equipment_db.find_one({"_id": equipment_id})
        if not equipment["checked_out"]:
            return f"Equipment {equipment_id} is not checked out"

        change_result = self.users_db.update_one(
            {"_id": user_id}, {"$pull": {"checked_out_equipment": equipment_id}}
        )
        if change_result.acknowledged:
            self.equipment_db.update_one(
                {"_id": equipment_id}, {"$set": {"checked_out": False}}
            )
            return f"User {user_id} has released equipment {equipment_id}"
        else:
            return f"User {user_id} was unable to release equipment {equipment_id}"

    def set_equipment_year(self, id: UUID, year: int):
        change_result = self.equipment_db.update_one(
            {"_id": id}, {"$set": {"year": year}}
        )
        if change_result.acknowledged:
            return f"Year {year} has changed for equipment {id}"
        else:
            return f"Year was not changed for equipment {id}"

    def set_equipment_name(self, id: UUID, name: str):
        change_result = self.equipment_db.update_one(
            {"_id": id}, {"$set": {"name": name}}
        )
        if change_result.acknowledged:
            return f"Name {name} has changed for equipment {id}"
        else:
            return f"Name was not changed for equipment {id}"

    def set_equipment_class(self, id: UUID, _class: str):
        change_result = self.equipment_db.update_one(
            {"_id": id}, {"$set": {"class": _class}}
        )
        if change_result.acknowledged:
            return f"Class {_class} has changed for equipment {id}"
        else:
            return f"Class was not changed for equipment {id}"

    def set_equipment_checked_out(self, id: UUID, checked_out: bool):
        change_result = self.equipment_db.update_one(
            {"_id": id}, {"$set": {"checked_out": checked_out}}
        )
        if change_result.acknowledged:
            return f"Checked_out {checked_out} has changed for equipment {id}"
        else:
            return f"Checked_out was not changed for equipment {id}"

    def get_user_by_username(self, username: str) -> User:
        querry = {"username": username}
        if self.users_db.count_documents(querry) > 1:
            return f"More then one user had the username {username}"

        # Pymongo returns a cursor object so must convert to a list
        # This line gets the user object
        new_user = User()
        new_user.fill_user_information(list(self.users_db.find(querry))[0])
        return new_user

    def add_image(self, equipment_id: UUID, image: Image):
        img_uuid = uuid4()
        while True:
            if (self.images_db / img_uuid).exists():
                img_uuid = uuid4()
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

    def add_report(self, equipment_id: UUID, report_content):
        report_uuid = uuid4()
        while True:
            if (self.reports_db / report_uuid).exists():
                report_uuid = uuid4()
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

    def get_image(self, uuid: UUID):
        if type(uuid) is not UUID:
            return f"{uuid} is not a UUID"

        if not (self.images_db / uuid).exists():
            return f"{uuid} image does not exist"

        img = Image.open(self.images_db / uuid)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")

        return buffer.getvalue()

    def delete_image(self, uuid: UUID):
        os.remove(self.images_db / uuid)
        return f"Sucessfully removed image {uuid}"

    def get_report(self, uuid: UUID):
        if type(uuid) is not UUID:
            return f"{uuid} is not a UUID"

        if not (self.images_db / uuid).exists():
            return f"{uuid} report does not exist"

        with open(self.reports_db / uuid, "rb") as f:
            report_data = io.BytesIO(f.read())

        return report_data

    def delete_report(self, uuid: UUID):
        os.remove(self.reports_db / uuid)
        return f"{uuid} report has been deleted"

    def get_notifications_by_user(self, user_id):
        return self.notifications_db.find({"receiver": ObjectId(user_id)})

    def get_username_by_id(self, user_id: UUID):
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

    def delete_data(self, uuid: UUID, *, collection: str = None):
        if collection:
            match collection:
                case "users":
                    user = self.users_db.find({"_id": uuid})
                    if not user:
                        raise ValueError(
                            f"UUID {uuid} does not exist in {collection} collection"
                        )

                    # future talks will have to be discussed regarding which data should be deleted with the user and which should stay

                case "equipment":
                    equipment = self.equipment_db
                    if not equipment:
                        raise ValueError(
                            f"UUID {uuid} does not exist in {collection} collection"
                        )

                    if equipment["checked_out"]:
                        return "Equipment is checked out by a user, have the user relinquish ownership so the equipment can be deleted"
                    else:
                        report_uuids = self.find_reports_for_equipment(
                            equipment_uuid=equipment["_id"]
                        )
                        for report_uuid in report_uuids:
                            self.delete_report(uuid=report_uuid)
                            # test to make sure that all reports are deleted

                        image_uuids = self.find_images_for_equipment(
                            equipment_uuid=["_id"]
                        )
                        for image_uuid in image_uuids:
                            self.delete_image(uuid=image_uuid)
                            # test to make sure that all reports are deleted

                        self.equipment_db.delete_one(
                            {"_id": equipment["_id"]}
                        )  # Check this with tests
                        return f"Equipment {uuid} has successfully been deleted"

                case "notification":
                    notification = self.notifications_db
                    if not notification:
                        raise ValueError(
                            f"UUID {uuid} does not exist in {collection} collection"
                        )

                    self.notifications_db.delete_one({"_id": uuid})

                    return f"Notification {uuid} has sucessfully been deleted"

                case "request":
                    request = self.reports_db
                    if not request:
                        raise ValueError(
                            f"UUID {uuid} does not exist in {collection} collection"
                        )

                    if request["active"]:
                        return "Request can not be deleted as it is still active, if we want to change this, delete this 'if' statement"
                    else:
                        self.reports_db.delete_one({"_id": uuid})
                        return f"Request {uuid} was successfuly deleted"

                case _:
                    raise ValueError(f"{collection} is not a colelction in MongoDB")
        else:
            collections = [
                self.users_db,
                self.equipment_db,
                self.requests_db,
                self.notifications_db,
            ]
            for c in collections:
                result = c.delete_many({"_id": uuid})
                if result.deleted_count != 0:
                    return f"{uuid} has been sucessfully deleted from {c}"

            for dir, _, files in os.walk(self.images_db):
                if uuid in files:
                    os.remove(self.images_db / dir / uuid)
                    return f"{uuid} has been sucessfully deleted from images"

            for dir, _, files in os.walk(self.reports_db):
                if uuid in files:
                    os.remove(self.images_db / dir / uuid)
                    return f"{uuid} has been sucessfully deleted from reports"

            return f"{uuid} could not be found in database"

    def send_notification(self, notification: Notification):
        note_id = str(uuid4())
        notification_json = {
            "_id": note_id,
            "sender": notification.sender.id,
            "receiver": notification.receiver.id,
            "body": notification.body,
            "date": notification.date,
            "type": notification.type,
        }
        result_user = self.users_db.update_one(
            {"_id": notification.receiver.id}, {"$push": {"inbox": note_id}}
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
