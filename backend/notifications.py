import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
from user import User
from datetime import datetime
from bson.objectid import ObjectId
from typing import Literal


class Notification:
    def __init__(
        self,
        id: ObjectId = None,
        sender: ObjectId = None,
        receiver: ObjectId = None,
        date: datetime = None,
        body: str = None,
        _type: str = None,
        equipment_id: ObjectId = None,
        read: bool = False,
        status: Literal["a", "r", "p"] = None,
    ):
        self.id = ObjectId(id)
        self.sender = ObjectId(sender)
        self.receiver = ObjectId(receiver)
        self.date = date
        self.body = body
        self.type = _type
        self.equipment_id = ObjectId(equipment_id) if equipment_id else None
        self.read = read
        self.status = status

    def populate_from_json(self, json_info):
        self.id = ObjectId(json_info.get("_id"))
        self.sender = ObjectId(json_info.get("sender"))
        self.receiver = ObjectId(json_info.get("receiver"))
        self.date = json_info.get("date", "")
        self.body = json_info.get("body", "")
        self.type = json_info.get("type", "i")
        eq_id = json_info.get("equipment_id")
        self.equipment_id = ObjectId(eq_id) if eq_id else None
        self.read = json_info.get("read", False)
        self.status = json_info.get("status", "p")

    def to_dict(self, sender_name):
        d = {
            "sender_name": sender_name,
            "sender": str(self.sender),
            "receiver": str(self.receiver),
            "date": str(self.date),
            "body": self.body,
            "type": self.type,
            "_id": str(self.id),
            "read": self.read,
            "status": self.status,
        }
        d["equipment_id"] = str(self.equipment_id) if self.equipment_id else None
        return d


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

    def send_forgot_password_email(self, email: str, link: str):
        msg = MIMEMultipart()
        msg["From"] = self.email_address
        msg["To"] = email
        msg["Subject"] = "Forgot Password"
        msg.attach(
            MIMEText(
                f"Please use the following link to reset your password \n\n{link}",
                "plain",
            )
        )
        try:
            server = smtplib.SMTP(self.server, self.port)
            server.starttls()
            server.login(self.email_address, self.email_password)
            server.sendmail(self.email_address, email, msg.as_string())
            server.quit()
            print("email sent")
            return "Email sent successfully!"

        except Exception as e:
            print(e)
            return f"Error sending email: {e}"

    def send_account_approval_message(self, new_user: User):
        message = f"{new_user.name} is attempting to make a new account"
        for admin in self.db.get_administrators():
            new_note = Notification(
                id=ObjectId(),
                sender=new_user.id,
                receiver=admin.id,
                date=datetime.now(),
                body=message,
                _type="a",
                equipment_id=None,
                read=False,
                status=None,
            )
            self.db.send_notification(notification=new_note)

    def send_equipment_request(
        self, id: ObjectId, sender: User, equip_name: str, equipment_id: ObjectId
    ):
        message = f"{sender.name} wants to sign out {equip_name}"
        try:
            for admin in self.db.get_administrators():
                new_note = Notification(
                    id=id,
                    sender=sender.id,
                    receiver=admin.id,
                    date=datetime.now(),
                    body=message,
                    _type="r",
                    equipment_id=equipment_id,
                    read=False,
                    status="p",
                )
                self.db.send_notification(notification=new_note)
            return 1
        except Exception as e:
            return 0

    def send_inform_notification(self, sender, receiver, message="", equipment_id=None, id=None):
        if id is None:
            id = ObjectId()

        notification = Notification(
            id=id,
            sender=sender.id,
            receiver=receiver.id,
            date=datetime.now(),
            body=message,
            _type="i",  # inform
            equipment_id=equipment_id,
            read=False,
            status=None,
        )
        self.db.send_notification(notification=notification)