from uuid import UUID
from PIL import Image


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
        checked_out: bool = False,
        description: str = None,
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
        self.checked_out = checked_out
        self.description = description

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
            result = db.get_reports(report_id)
            if type(result) is str:
                return result
            else:
                report_bytes.append(result)

        return report_bytes

    def fill_from_json(self, json_info):
        print(json_info)
        self.id = json_info["_id"]
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
        return 1
