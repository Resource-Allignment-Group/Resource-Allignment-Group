class User:
    def __init__(self):
        self.username = None
        self.password = None
        self.id = None
        self.role = None
        self.email = None
        self.inbox = []
        self.checked_out_equipment = []

    def fill_inbox(self, db):
        notifications = db.get_notifications_by_user(self.id)

        for n in notifications.sort("date", -1):
            self.inbox.append(n)

    def fill_user_information(self, db_object):
        self.username = db_object["username"]
        self.password = db_object["password"]
        self.id = db_object["_id"]
        self.role = db_object["role"]
        self.inbox = db_object["inbox"]
        self.checked_out_equipment = db_object["checked_out_equipment"]
