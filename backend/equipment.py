from uuid import UUID


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
