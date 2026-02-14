from uuid import UUID
from PIL import Image
from bson import ObjectId


class Equipment:
    def __init__(
        self,
        uuid: str = None,
        name: str = None,
        _class: str = None,
        year: int = None,
        farm: str = None,
        model: str = None,
        make: str = None,
        use: str = None,
        images: list = None,
        reports: list = None,
        display_image: str = None,
        checked_out: bool = False,
        description: str = None,
        damaged: bool = False,
        unavailable: bool = False,
    ):
        self.id = uuid
        self._class = _class
        self.name = name
        self.year = year
        self.farm = farm
        self.make = make
        self.model = model
        self.use = use
        self.images = images or []
        self.reports = reports or []
        self.display_image = display_image
        self.checked_out = checked_out
        self.description = description
        self.damaged = damaged
        self.unavailable = unavailable

    def get_images(self, db):
        img_bytes = []
        for image_id in self.images:
            result = db.get_image(image_id)
            if type(result) is str:
                return result
            else:
                img_bytes.append(result)

        return img_bytes

    def get_reports(self, db):
        report_bytes = []
        for report_id in self.reports:
            result = db.get_report(report_id)
            if type(result) is str:
                return result
            else:
                report_bytes.append(result)

        return report_bytes

    def fill_from_json(self, json_info):
        self.id = ObjectId(json_info["_id"])
        self._class = json_info["class"]
        self.name = json_info["name"]
        self.year = json_info["year"]
        self.farm = json_info["farm"]
        self.make = json_info["make"]
        self.model = json_info["model"]
        self.use = json_info["use"]
        self.images = json_info.get("images") or []
        self.reports = json_info.get("reports") or []
        self.display_image = json_info.get("display_image")
        self.checked_out = json_info["checked_out"]
        self.description = json_info["description"]
        self.damaged = json_info["damaged"]
        self.unavailable = json_info.get("unavailable", False)
        return 1

    def to_dict(self):
        total_attachments = len(self.images or []) + len(self.reports or []) # should really look through this in order to see what we need and what we don't
        return (
            {
                "id": str(self.id),
                "name": self.name,
                "checkedOutBy": "Need to impliment who is checked out by",  # need to impliment by looking at users who have this in their equipment
                "class": self._class,
                "year": self.year,
                "farm": self.farm,
                "model": self.model,
                "make": self.make,
                "use": self.use,
                "images": self.images or [],
                "reports": self.reports or [],
                "display_image": self.display_image,
                "checked_out": self.checked_out,
                "description": self.description,
                "attachments": total_attachments,
                "replacementCost": 100000,  # change lateer
                "damaged": self.damaged,
                "unavailable": self.unavailable,
            }
        )
