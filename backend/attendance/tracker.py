from backend.database.db_manager import DatabaseManager
from datetime import datetime


class AttendanceTracker:
    def __init__(self):
        self.db = DatabaseManager()

    def get_today_attendance(self):
        today = datetime.now().strftime("%Y-%m-%d")
        return self.db.get_attendance_by_date(today)

    def get_report(self, start_date, end_date):
        return self.db.get_attendance_report(start_date, end_date)

    def get_summary(self, date=None):
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        records = self.db.get_attendance_by_date(date)
        return {
            'date': date,
            'total': len(records),
            'records': records
        }
