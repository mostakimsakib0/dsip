import pandas as pd
from datetime import datetime
from backend.config import REPORTS_DIR
from backend.database.db_manager import DatabaseManager
import os


class ReportGenerator:
    def __init__(self):
        self.db = DatabaseManager()

    def generate_csv(self, start_date, end_date):
        records = self.db.get_attendance_report(start_date, end_date)
        df = pd.DataFrame(records, columns=['Student ID', 'Name', 'Date', 'Time', 'Confidence'])
        filename = f"attendance_{start_date}_to_{end_date}.csv"
        filepath = os.path.join(REPORTS_DIR, filename)
        df.to_csv(filepath, index=False)
        return filepath

    def generate_excel(self, start_date, end_date):
        records = self.db.get_attendance_report(start_date, end_date)
        df = pd.DataFrame(records, columns=['Student ID', 'Name', 'Date', 'Time', 'Confidence'])
        filename = f"attendance_{start_date}_to_{end_date}.xlsx"
        filepath = os.path.join(REPORTS_DIR, filename)
        df.to_excel(filepath, index=False)
        return filepath
