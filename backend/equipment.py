from uuid import UUID
from PIL import Image
from database import Database


class Equipment:
    def __init__(
        self,
        uuid: str,
        _class: str,
        year: int,
        images: list[UUID],
        reports: list[UUID],
        checked_out: bool,
    ):
        self.id = (uuid,)
        self._class = (_class,)
        self.year = year
        self.images = images
        self.reports = reports
        self.checked_out = checked_out

    def get_images(self, db: Database):
        img_bytes = []
        for image_id in self.images:
            result = db.get_image(image_id)
            if type(result) == str:
                return result
            else:
                img_bytes.append(result)

        return img_bytes

    def get_reports(self, db: Database):
        report_bytes = []
        for report_id in self.reports:
            result = db.get_reports(report_id)
            if type(result) == str:
                return result
            else:
                report_bytes.append(result)

        return report_bytes
