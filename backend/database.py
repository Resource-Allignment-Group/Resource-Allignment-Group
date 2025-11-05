import pymongo
import os
from pymongo import MongoClient
from pathlib import Path
from uuid import UUID
import logging
from datetime import datetime

_client = None


class Database:
    def get_client(self):
        global _client
        if _client is None:
            _client = MongoClient(os.environ["DATABASE_URI"])
        return _client

    def __init__(self):
        self.get_client()
        self.db = _client["Users"]
        self.users_db = self.db["users"]
        self.equipment_db = self.db["equipment"]
        self.requests_db = self.db["requests"]
        self.notifications_db = self.db["notifications"]
        self.images_db = Path("backend/large_files_db/images")
        self.reports_db = Path("backend/large_files_db/reports")

        if (self.reports_db / "test_log.txt").exists():
            self.log = logging.basicConfig(
                filename="test_log.log",
                filemode="a",
                level=logging.INFO,
            )
        else:
            self.log = logging.basicConfig(
                filename="test_log.log", filemode="w", level=logging.INFO
            )

    def find_images_for_equipment(self, equipment_uuid: UUID):
        if type(equipment_uuid) != UUID:  # noqa: E721
            return "'equipment_uuid' not a UUID"

        equipment = self.equipment_db.find_one({"_id": equipment_uuid})
        if equipment is None:
            return "equipment_uuid does not exist"

        images = []
        for image_uuid in equipment["images"]:
            image_path = self.images_db / image_uuid
            if image_path.exists():
                images.append(image_path)
            else:
                return f"image path {image_uuid} does not exist"

        return images

    def delete_image(self, uuid: UUID):
        os.remove(self.images_db / uuid)
        return 1

    def find_reports_for_equipment(self, equipment_uuid: UUID):
        if type(equipment_uuid) != UUID:  # noqa: E721
            return "'equipment_uuid' not a UUID"

        equipment = self.equipment_db.find_one({"_id": equipment_uuid})
        if equipment == None:
            return "equipment_uuid does not exist"

        reports = []
        for report_uuid in equipment["reports"]:
            report_path = self.reports_db / report_uuid
            if report_path.exists():
                reports.append(report_path)
            else:
                return f"report path {report_uuid} does not exist"
        return reports

    def delete_report(self, uuid: UUID):
        os.remove(self.reports_db / uuid)
        return 1

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

    def log(self, message: str, level: int):
        # The 'level' type hint isn't really true, but this does work as logging.INFO==10, logging.DEBUG==10, etc
        # It it just a Wrapper for integers

        if level >= 50:  # 50 is arbitrary
            # I think this should send an email once the email finctionality is set up in the code
            pass
