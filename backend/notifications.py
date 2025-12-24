import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
from user import User
from datetime import datetime
from bson.objectid import ObjectId


class Notification:
    def __init__(
        self,
        id: ObjectId = None,
        sender: str = None,
        receiver: str = None,
        date: datetime = None,
        body: str = None,
        _type: str = None,
        equipment_id: ObjectId = None,
        read: bool = False,
    ):
        self.id = id
        self.sender = sender
        self.receiver = receiver
        self.date = date
        self.body = body
        self.type = _type
        self.equipment_id = equipment_id
        self.read = read

    def populate_from_json(self, json_info):
        self.id = ObjectId(json_info["_id"])
        self.sender = ObjectId(json_info["sender"])
        self.receiver = ObjectId(json_info["receiver"])
        self.date = json_info["date"]
        self.body = json_info["body"]
        self.type = json_info["type"]
        self.equipment_id = ObjectId(json_info["equipment_id"])
        self.read = json_info["read"]

    def to_dict(self, sender_username):
        return {  # need to convert to strings in order to make the json serializable
            "sender_username": sender_username,
            "sender": str(self.sender),
            "receiver": str(self.receiver),
            "date": str(self.date),
            "body": self.body,
            "type": self.type,
            "_id": str(self.id),
            "equipment_id": str(self.equipment_id),
            "read": self.read,
        }


class Notification_Manager:
    def __init__(self, db):
        load_dotenv()
        self.db = db
        self.server = "smtp.gmail.com"
        self.port = 587  # port can not change
        self.email_address = "bradancraig2004@gmail.com"  # We should make a email account so that email notifications can go through this
        self.email_password = os.environ.get("EMAIL_PASSWORD")

    def send_email(self, message: str, receiver: str, subject: str):
        msg = MIMEMultipart()
        msg["From"] = self.email_address
        msg["To"] = receiver
        msg["Subject"] = subject
        msg.attach(MIMEText(message, "plain"))
        try:
            server = smtplib.SMTP(self.server, self.port)
            server.starttls()
            server.login(self.email_address, self.email_password)
            server.sendmail(self.email_address, receiver, msg.as_string())
            server.quit()
            return "Email sent successfully!"

        except Exception as e:
            return f"Error sending email: {e}"

    def send_account_approval_message(self, new_user: User):
        message = f"The user {new_user.username} is attempting to make a new account"
        for admin in self.db.get_administrators():
            new_note = Notification(
                id=ObjectId(),
                sender=new_user,
                receiver=admin,
                date=datetime.now(),
                body=message,
                _type="a",
                equipment_id=None,
                read=False,
            )
            self.db.send_notification(notification=new_note)

    def send_equipment_request(
        self, id: ObjectId, sender: User, equip_name: str, equipment_id: ObjectId
    ):
        message = f"{sender.username} wants to sign out {equip_name}"
        try:
            for admin in self.db.get_administrators():
                new_note = Notification(
                    id=id,
                    sender=sender,
                    receiver=admin,
                    date=datetime.now(),
                    body=message,
                    _type="r",
                    equipment_id=ObjectId(equipment_id),
                    read=False,
                )
                self.db.send_notification(notification=new_note)

            return 1
        except:
            return 0

    def send_inform_notification(
        self, sender: User, receiver: User, message: str, id: ObjectId = None
    ):
        if id is None:
            id = ObjectId()

        notification = Notification(
            id=id,
            sender=sender,
            receiver=receiver,
            date=datetime.now(),
            body=message,
            _type="i",  # inform
            equipment_id=None,
            read=False,
        )
        self.db.send_notification(notification=notification)
