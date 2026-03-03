# The base user class

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
        self.receive_reports = True
        self.profile_image = None

    def fill_inbox(self, db):
        notifications = db.get_notifications_by_user(self.id)

        for n in notifications.sort("date", -1):
            self.inbox.append(n)

    def fill_user_information(self, db_object):
            # If the user wasn't found in DB, stop here to avoid crashes
            if db_object is None:
                return

            self.id = db_object["_id"]
            self.role = db_object["role"]
            self.inbox = db_object["inbox"] if "inbox" in db_object else []
            self.checked_out_equipment = db_object["checked_out_equipment"] if "checked_out_equipment" in db_object else []
            self.position = db_object["position"] if "position" in db_object else None
            self.department = db_object["department"] if "department" in db_object else None
            self.phone = db_object["phone"] if "phone" in db_object else None
            self.name = db_object["name"] if "name" in db_object else "Unknown"
            self.email = db_object["email"]
            self.receive_reports = db_object["receive_reports"] if "receive_reports" in db_object else True
            self.profile_image = db_object["profile_image"] if "profile_image" in db_object else None

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
            "receive_reports": self.receive_reports,
            "profile_image": self.profile_image,
        }