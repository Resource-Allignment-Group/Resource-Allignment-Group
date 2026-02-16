class User:
    def __init__(self):
        self.password = None
        self.id = None
        self.role = None
        self.email = None
        self.inbox = []
        self.checked_out_equipment = []
        self.position = None
        self.phone = None
        self.name = None
        self.department = None

    def fill_inbox(self, db):
        notifications = db.get_notifications_by_user(self.id)

        for n in notifications.sort("date", -1):
            self.inbox.append(n)

    def fill_user_information(self, db_object):
            # If the user wasn't found in DB, stop here to avoid crashes
            if db_object is None:
                return 

            self.id = db_object.get("_id")
            self.role = db_object.get("role", "u")
            self.inbox = db_object.get("inbox", [])
            self.checked_out_equipment = db_object.get("checked_out_equipment", [])
            self.position = db_object.get("position", "")
            self.department = db_object.get("department", "")
            self.phone = db_object.get("phone", "")
            self.name = db_object.get("name", "Unknown")
            self.email = db_object.get("email", "")

    def to_dict(self):
        return {
            "id": str(self.id),
            "role": self.role,
            "email": self.email,
            "inbox": [str(id) for id in self.inbox],
            "position": self.position,
            "department": self.department,
            "name": self.name,
            "phone": self.phone,
            "checked_out_equipment": [
                str(equip) for equip in self.checked_out_equipment
            ],
        }