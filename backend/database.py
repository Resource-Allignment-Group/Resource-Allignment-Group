import pymongo
import os
from pymongo import MongoClient
from pathlib import Path
from uuid import UUID


class Database:
    def __init__(self):
        client = MongoClient(os.environ.get("DATABASE_URI"))
        self.db = client["Users"]
        self.users_db = self.db["users"]
        self.equipment_db = self.db["equipment"]
        self.requests_db = self.db["requests"]
        self.notifications_db = self.db["notifications"]
        self.images_db = Path("backend/large_files_db/images")
        self.reports_db = Path("backend/large_files_db/reports")

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

    def find_reports_for_equipment(self, equipment_uuid):
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
