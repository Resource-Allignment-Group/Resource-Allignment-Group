from uuid import UUID
from database import Database

class User:
    def __init__(self, username: str, uuid: UUID, role: str, email: str):
        self.username = username
        self.id = uuid
        self.role = role
        self.email = email
        self.inbox = []

    def fill_inbox(self, db: Database):
        notifications = db.get_notifications_by_user(self.id)