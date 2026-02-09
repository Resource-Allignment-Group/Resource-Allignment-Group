import logging

class SystemLogger:
    def __init__(self, filename="system_logs.txt"):
        self.logger = logging.getLogger("RAM_System")
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            file_handler = logging.FileHandler(filename)
            file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
            
            self.logger.addHandler(file_handler)
            # self.logger.addHandler(stream_handler)


        logging.getLogger('werkzeug').setLevel(logging.ERROR) 

    def log_action(self, user_id, action, details="", target_id=None):
        message = f"[User: {user_id}] [Action: {action}]"
        if target_id:
            message += f" [Target: {target_id}]"
        if details:
            message += f" - Details: {details}"
        self.logger.info(message)

    def log_error(self, message):
        self.logger.error(message)