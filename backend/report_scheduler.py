import schedule
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import os

class ReportScheduler:
    """Fixed-schedule monthly reports: 1st of the month at 09:00."""
    
    def __init__(self, db, notification_manager, report_generator):
        self.db = db
        self.notification_manager = notification_manager
        self.report_generator = report_generator
        self.running = False
        self.thread = None

    def generate_and_send(self):
        """Logic to generate the previous month's report and email admins."""
        try:
            admins = self.db.get_administrators()
            admin_emails = [a.email for a in admins if hasattr(a, 'email') and a.email]
            
            if not admin_emails:
                print("Scheduler: No admin emails found.")
                return False

            # Calculate previous month range
            today = datetime.now()
            first_this_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            last_prev_month = first_this_month - timedelta(days=1)
            first_prev_month = last_prev_month.replace(day=1)
            
            temp_pdf = Path(tempfile.gettempdir()) / f"monthly_report_{first_prev_month.strftime('%Y_%m')}.pdf"
            
            self.report_generator.generate_report(first_prev_month, last_prev_month, str(temp_pdf))
            
            subject = f"Monthly Report - {first_prev_month.strftime('%B %Y')}"
            message = f"Please find the activity report for {first_prev_month.strftime('%B %Y')} attached."
            
            for email in admin_emails:
                self.notification_manager.send_email(
                    message=message, receiver=email, subject=subject, attachments=[str(temp_pdf)]
                )
            
            if temp_pdf.exists():
                os.remove(temp_pdf)
            
            self.report_generator.clear_old_logs(60) #
            return True
        except Exception as e:
            print(f"Scheduled Task Failed: {e}")
            return False

    def _run_loop(self):
        while self.running:
            schedule.run_pending()
            time.sleep(60)

    def start(self):
        # Start the scheduler, check every day at 09:00am
        if self.running: return
        schedule.clear()
        schedule.every().day.at("09:00").do(self._check_calendar_day)
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def _check_calendar_day(self):
        if datetime.now().day == 1:
            self.generate_and_send()

    def stop(self):
        self.running = False
        schedule.clear()

# Global instance management
_scheduler = None

def init_scheduler(db, notification_manager, report_generator):
    """Initialize and automatically start the scheduler."""
    global _scheduler
    _scheduler = ReportScheduler(db, notification_manager, report_generator)
    _scheduler.start() # Starts immediately without checking a config
    return _scheduler

def get_scheduler():
    """Get the active scheduler instance."""
    return _scheduler