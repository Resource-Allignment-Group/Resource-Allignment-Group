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
        images: list[UUID] = None,
        reports: list[UUID] = None,
        display_image: str = None,
        checked_out: bool = False,
        description: str = None,
        damaged: bool = False,
        unavailable: bool = False,
        replacement_cost: float = 0.0,

    ):
        self.id = uuid
        self._class = _class
        self.name = name
        self.year = year
        self.farm = farm
        self.make = make
        self.model = model
        self.use = use
        self.images = images
        self.reports = reports
        self.display_image = display_image
        self.checked_out = checked_out
        self.description = description
        self.damaged = damaged
        self.unavailable = unavailable
        self.replacement_cost = replacement_cost

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
        self.images = json_info["images"]
        self.reports = json_info["reports"]
        self.checked_out = json_info["checked_out"]
        self.description = json_info["description"]
        self.damaged = json_info["damaged"]
        self.replacement_cost = json_info.get("replacement_cost", 0)
        if "display_image" in json_info:
            self.display_image = json_info["display_image"]
        else:
            self.display_image = None
        if "unavailable" in json_info:
            self.unavailable = json_info["unavailable"]
        else:
            self.unavailable = False
        return 1

    def to_dict(self):
        return (
            {
                "id": str(self.id),
                "name": self.name,
                "checkedOutBy": None,
                "class": self._class,
                "year": self.year,
                "farm": self.farm,
                "model": self.model,
                "make": self.make,
                "use": self.use,
                "images": self.images,
                "reports": self.reports,
                "display_image": self.display_image,
                "checked_out": self.checked_out,
                "description": self.description,
                "replacement_cost": self.replacement_cost,
                "attachments": (len(self.images) if self.images else 0) + (len(self.reports) if self.reports else 0),
                "damaged": self.damaged,
                "unavailable": self.unavailable,
            }
        )
