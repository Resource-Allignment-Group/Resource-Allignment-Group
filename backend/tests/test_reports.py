import pytest
from pathlib import Path
from datetime import datetime, timedelta
from report_gen import ReportGenerator
from unittest.mock import patch
from report_scheduler import ReportScheduler

# Tests for report generation and logging functions

### Testing Fixtures

@pytest.fixture
def report_gen(client):
    return ReportGenerator(db=client.application.db)

@pytest.fixture
def log_file_with_entries(tmp_path):
    """Creates a temp log file with known entries for testing"""
    log = tmp_path / "test_logs.txt"
    log.write_text(
        "2026-03-01 10:00:00,000 - INFO - [User: Admin] [Action: CHECK_OUT] [Target: Tractor 1] [Details: John : john@example.com]\n"
        "2026-03-02 11:00:00,000 - INFO - [User: Admin] [Action: CHECK_IN] [Target: Tractor 1] [Details: Item returned in good condition]\n"
        "2026-03-03 12:00:00,000 - INFO - [User: Admin] [Action: ADD_USER] [Target: Jane : jane@example.com] [Details: New Account Approved by Admin]\n"
        "2025-01-01 08:00:00,000 - INFO - [User: Admin] [Action: DELETE_USER] [Target: Old User] [Details: Account Removed by Admin]\n"  # Outside date range
    )
    return log

### parse_logs -----------------------------------------

def test_parse_logs_returns_entries_in_range(log_file_with_entries):
    gen = ReportGenerator(db=None, log_file_path=log_file_with_entries)
    start = datetime(2026, 3, 1)
    end = datetime(2026, 3, 31)
    entries = gen.parse_logs(start, end)
    assert len(entries) == 3  # 4th entry is from 2025, outside range

def test_parse_logs_excludes_outside_range(log_file_with_entries):
    gen = ReportGenerator(db=None, log_file_path=log_file_with_entries)
    start = datetime(2026, 3, 1)
    end = datetime(2026, 3, 31)
    entries = gen.parse_logs(start, end)
    actions = [e["action"] for e in entries]
    assert "DELETE_USER" not in actions  # That entry is from 2025

def test_parse_logs_empty_when_no_file():
    gen = ReportGenerator(db=None, log_file_path=Path("/nonexistent/path.txt"))
    entries = gen.parse_logs(datetime(2026, 1, 1), datetime(2026, 12, 31))
    assert entries == []

def test_parse_logs_correct_fields(log_file_with_entries):
    gen = ReportGenerator(db=None, log_file_path=log_file_with_entries)
    entries = gen.parse_logs(datetime(2026, 3, 1), datetime(2026, 3, 31))
    entry = entries[0]
    assert entry["action"] == "CHECK_OUT"
    assert entry["user_id"] == "Admin"
    assert "Tractor 1" in entry["target_id"]

### generate_stats -----------------------------------------

def test_generate_stats_total(log_file_with_entries):
    gen = ReportGenerator(db=None, log_file_path=log_file_with_entries)
    entries = gen.parse_logs(datetime(2026, 3, 1), datetime(2026, 3, 31))
    stats = gen.generate_stats(entries)
    assert stats["total"] == 3

def test_generate_stats_by_action(log_file_with_entries):
    gen = ReportGenerator(db=None, log_file_path=log_file_with_entries)
    entries = gen.parse_logs(datetime(2026, 3, 1), datetime(2026, 3, 31))
    stats = gen.generate_stats(entries)
    assert stats["by_action"]["CHECK_OUT"] == 1
    assert stats["by_action"]["CHECK_IN"] == 1
    assert stats["by_action"]["ADD_USER"] == 1

def test_generate_stats_empty():
    gen = ReportGenerator(db=None)
    stats = gen.generate_stats([])
    assert stats["total"] == 0
    assert stats["unique_users"] == 0

### map_actions -----------------------------------------

def test_map_actions_known(report_gen):
    assert report_gen.map_actions("CHECK_OUT") == "Equipment Checkout"
    assert report_gen.map_actions("CHECK_IN") == "Equipment Return"
    assert report_gen.map_actions("ADD_USER") == "User Registered"
    assert report_gen.map_actions("DELETE_USER") == "User Deleted"
    assert report_gen.map_actions("UPDATE_ROLE") == "Role Updated"
    assert report_gen.map_actions("ADD_EQUIPMENT") == "Equipment Added"
    assert report_gen.map_actions("DELETE_EQUIPMENT") == "Equipment Deleted"

def test_map_actions_unknown_falls_back(report_gen):
    # Unknown actions should be title-cased with underscores replaced
    result = report_gen.map_actions("CUSTOM_ACTION")
    assert result == "Custom Action"

### get_detailed_info -----------------------------------------

def test_get_detailed_info_update_role(report_gen):
    entry = {"action": "UPDATE_ROLE", "details": "a"}
    assert report_gen.get_detailed_info(entry) == "Role changed to: Admin"

def test_get_detailed_info_update_role_user(report_gen):
    entry = {"action": "UPDATE_ROLE", "details": "u"}
    assert report_gen.get_detailed_info(entry) == "Role changed to: User"

def test_get_detailed_info_check_in(report_gen):
    entry = {"action": "CHECK_IN", "details": "Item returned DAMAGED: crack"}
    assert "DAMAGED" in report_gen.get_detailed_info(entry)

def test_get_detailed_info_check_in_no_details(report_gen):
    entry = {"action": "CHECK_IN", "details": ""}
    assert report_gen.get_detailed_info(entry) == "No condition noted"

### generate_report -----------------------------------------

def test_generate_report_creates_pdf(report_gen, tmp_path):
    output = tmp_path / "test_report.pdf"
    start = datetime(2026, 3, 1)
    end = datetime(2026, 3, 31)
    report_gen.generate_report(start, end, str(output))
    assert output.exists()
    assert output.stat().st_size > 0

### clear_old_logs -----------------------------------------

def test_clear_old_logs_removes_old_entries(tmp_path):
    log = tmp_path / "logs.txt"
    old_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d %H:%M:%S")
    recent_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log.write_text(
        f"{old_date},000 - INFO - [User: A] [Action: CHECK_OUT] [Target: X]\n"
        f"{recent_date},000 - INFO - [User: B] [Action: CHECK_IN] [Target: Y]\n"
    )
    gen = ReportGenerator(db=None, log_file_path=log)
    gen.clear_old_logs(days_to_keep=60)
    content = log.read_text()
    assert "CHECK_IN" in content     # Recent entry kept
    assert "CHECK_OUT" not in content  # Old entry removed

def test_clear_old_logs_no_file():
    # Should not raise if the log file doesn't exist
    gen = ReportGenerator(db=None, log_file_path=Path("/nonexistent/logs.txt"))
    gen.clear_old_logs()  # Should return silently

### ReportScheduler -----------------------------------------

def test_generate_and_send_no_admins(client):
    # If there are no admins, should return False without crashing
    db = client.application.db
    nm = client.application.nm
    rg = ReportGenerator(db=db)
    scheduler = ReportScheduler(db=db, notification_manager=nm, report_generator=rg)
    # DB is empty (no admins seeded), so should bail out early
    result = scheduler.generate_and_send()
    assert result is False

def test_generate_and_send_with_admin(login_admin, tmp_path):
    # With an admin present who has receive_reports=True, should generate and "send"
    db = login_admin.application.db
    nm = login_admin.application.nm
    rg = ReportGenerator(db=db)
    scheduler = ReportScheduler(db=db, notification_manager=nm, report_generator=rg)
    # Set the admin to receive reports
    admin = db.get_user_by_email("admin@gmail.com")
    db.users_db.update_one({"_id": admin.id}, {"$set": {"receive_reports": True}})
    with patch.object(nm, "send_email") as mock_email:
        result = scheduler.generate_and_send()
    assert result is True
    assert mock_email.called

def test_generate_and_send_admin_opted_out(login_admin):
    # Admin with receive_reports=False should be skipped, causing an early return
    db = login_admin.application.db
    nm = login_admin.application.nm
    rg = ReportGenerator(db=db)
    scheduler = ReportScheduler(db=db, notification_manager=nm, report_generator=rg)
    admin = db.get_user_by_email("admin@gmail.com")
    db.users_db.update_one({"_id": admin.id}, {"$set": {"receive_reports": False}})
    result = scheduler.generate_and_send()
    assert result is False

def test_check_calendar_day_not_first(login_admin):
    # _check_calendar_day should only call generate_and_send on day 1 of the month
    db = login_admin.application.db
    nm = login_admin.application.nm
    rg = ReportGenerator(db=db)
    scheduler = ReportScheduler(db=db, notification_manager=nm, report_generator=rg)
    with patch.object(scheduler, "generate_and_send") as mock_gen:
        with patch("report_scheduler.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 3, 15)  # Not the 1st
            scheduler._check_calendar_day()
    mock_gen.assert_not_called()

def test_check_calendar_day_on_first(login_admin):
    db = login_admin.application.db
    nm = login_admin.application.nm
    rg = ReportGenerator(db=db)
    scheduler = ReportScheduler(db=db, notification_manager=nm, report_generator=rg)
    with patch.object(scheduler, "generate_and_send") as mock_gen:
        with patch("report_scheduler.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 4, 1)  # Is the 1st
            scheduler._check_calendar_day()
    mock_gen.assert_called_once()

### /download_monthly_report route -----------------------------------------

def test_download_monthly_report_admin(login_admin):
    res = login_admin.get("/download_monthly_report")
    assert res.status_code == 200
    assert res.content_type == "application/pdf"

def test_download_monthly_report_not_admin(login_user):
    res = login_user.get("/download_monthly_report")
    assert res.status_code == 403

def test_download_monthly_report_not_logged_in(client):
    res = client.get("/download_monthly_report")
    assert res.status_code == 401