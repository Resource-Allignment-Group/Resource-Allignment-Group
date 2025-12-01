import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
from user import User
from database import Database


class Notification_Manager:
    def __init__(self):
        load_dotenv()
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

    def send_notification(self, sender: User, receiver: User, message):
        pass

    def send_account_approval_message(self, new_user: User, db: Database):
        message = """
            The user %s is attempting to make a new account 
                """

        for user in db.get_administrators():
            self.send_notification(sender=new_user, receiver=user, message=message)
