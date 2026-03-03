import logging
from pathlib import Path


class SystemLogger:
    def __init__(self, filename="system_logs.txt"):
        _backend_dir = Path(__file__).resolve().parent
        log_dir = _backend_dir / "large_files_db" / "reports"
        full_path = log_dir / filename

        self.logger = logging.getLogger("RAM_System")
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            file_handler = logging.FileHandler(full_path)
            file_handler.setFormatter(
                logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            )

            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))

            self.logger.addHandler(file_handler)

        logging.getLogger("werkzeug").setLevel(logging.ERROR)

    def log_action(self, user_id, action, details="", target_id=None):
        message = f"[User: {user_id}] [Action: {action}]"
        if target_id:
            message += f" [Target: {target_id}]"
        if details:
            message += f" [Details: {details}]"
        self.logger.info(message)

    def log_error(self, message):
        self.logger.error(message)
