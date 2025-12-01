import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os


class Notification_Manager:
    def __init__(self):
        load_dotenv()
        self.server = "smtp.gmail.com"
        self.port = 587
        self.email_address = "bradancraig2004@gmail.com"  # We should make a email account so that email notifications can go through this
        self.email_password = os.environ.get("EMAIL_PASSWORD")

    def send_unique_email(self, message: str, receiver: str, subject: str):
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
