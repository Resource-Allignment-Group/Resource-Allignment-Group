import logging
from datetime import datetime


class System_Logger:
    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.log = logging.basicConfig(
            filename="test_log.log",
            filemode="w",
            level=logging.INFO,
        )

    def log_information(self, message: str, level: str):
        self.log.log(msg=message, level=level)
        if (
            level >= 40
        ):  # This is the level for errors, see https://docs.python.org/3/library/logging.html for integer conversions
            pass
            # This should send a notificaion (preferably an email) to the admin
