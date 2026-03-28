import schedule
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import os

# The scheduling class for monthly report generation


# Runs in the background to keep track of when monthly reports should be generated
class ReportScheduler:
    def __init__(self, db, notification_manager, report_generator):
        self.db = db
        self.notification_manager = notification_manager
        self.report_generator = report_generator
        self.running = False
        self.thread = None

    def generate_and_send(self):
        """Calculates dates, builds the pdf using the report generator, emails the admins
        and then cleans up temporary files the were created"""
        try:
            # Get all admins, then make a list of their emails
            admins = self.db.get_administrators()
            # We check for a 'receive_reports' attribute. If it's missing, default to True.
            # This allows admins to receive the monthly reports only if they have it turned on
            admin_emails = [
                a.email
                for a in admins
                if hasattr(a, "email")
                and a.email
                and getattr(a, "receive_reports", True)
            ]
            # Don't generate a report if no admins were found
            if not admin_emails:
                return False

            # Calculate previous month range
            # e.g. it is April 1st and we want all info from March
            today = datetime.now()
            first_this_month = today.replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )
            last_prev_month = first_this_month - timedelta(days=1)
            first_prev_month = last_prev_month.replace(day=1)
            # Gives the PDF a title
            temp_pdf = (
                Path(tempfile.gettempdir())
                / f"monthly_report_{first_prev_month.strftime('%Y_%m')}.pdf"
            )
            # Use the report generated to parse the log file and populate the PDF
            self.report_generator.generate_report(
                first_prev_month, last_prev_month, str(temp_pdf)
            )

            # Setup the subject and message lines for the email
            subject = f"Monthly Report - {first_prev_month.strftime('%B %Y')}"
            message = f"Please find the activity report for {first_prev_month.strftime('%B %Y')} attached."
            # Send the same email to each admin
            for email in admin_emails:
                self.notification_manager.send_email(
                    message=message,
                    receiver=email,
                    subject=subject,
                    attachments=[str(temp_pdf)],
                )

            # Delete the monthly report PDF
            if temp_pdf.exists():
                os.remove(temp_pdf)
            # Use the report generator to clear the old logs entries
            # This clears logs older than 60 days
            self.report_generator.clear_old_logs(60)
            return True
        except Exception:
            return False

    def _run_loop(self):
        """Checks to see if it is time to generate the report every minute"""
        while self.running:
            schedule.run_pending()
            time.sleep(60)

    def start(self):
        """Creates the background thread that will be used to check date/time"""
        # Start the scheduler, check every day at 09:00am
        if self.running:
            return
        schedule.clear()
        schedule.every().day.at("09:00").do(self._check_calendar_day)
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def _check_calendar_day(self):
        """Checks to see if today is the first of the month"""
        # If it is, generate the monthly report
        if datetime.now().day == 1:
            self.generate_and_send()

# Global instance management
_scheduler = None

def init_scheduler(db, notification_manager, report_generator):
    """Start the scheduler instance"""
    global _scheduler
    _scheduler = ReportScheduler(db, notification_manager, report_generator)
    _scheduler.start()
    return _scheduler
