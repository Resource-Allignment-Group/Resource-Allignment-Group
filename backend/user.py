from uuid import UUID


class User:
    def __init__(self, username: str, uuid: UUID, role: str):
        self.username = username
        self.id = uuid
        self.role = role
