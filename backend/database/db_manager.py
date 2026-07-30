import sqlite3
import numpy as np
import pickle
from datetime import datetime
from backend.config import DATABASE_PATH, ATTENDANCE_COOLDOWN_MINUTES, CONFIDENCE_THRESHOLD
from backend.database.schema import STUDENT_TABLE, ATTENDANCE_TABLE


class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.execute(STUDENT_TABLE)
        self.cursor.execute(ATTENDANCE_TABLE)
        self.conn.commit()

    def register_student(self, student_id, name, department, embedding):
        blob = pickle.dumps(embedding)
        self.cursor.execute(
            "INSERT OR REPLACE INTO students (student_id, name, department, face_embedding) VALUES (?, ?, ?, ?)",
            (student_id, name, department, blob)
        )
        self.conn.commit()

    def get_all_students(self):
        self.cursor.execute("SELECT student_id, name, department FROM students")
        return self.cursor.fetchall()

    def get_all_embeddings(self):
        self.cursor.execute("SELECT student_id, name, face_embedding FROM students")
        rows = self.cursor.fetchall()
        result = []
        for sid, name, blob in rows:
            emb = pickle.loads(blob)
            result.append((sid, name, emb))
        return result

    def mark_attendance(self, student_id, name, confidence):
        today = datetime.now().strftime("%Y-%m-%d")
        now = datetime.now().strftime("%H:%M:%S")

        if self._is_duplicate(student_id, today):
            return False

        self.cursor.execute(
            "INSERT INTO attendance (student_id, name, date, time, confidence) VALUES (?, ?, ?, ?, ?)",
            (student_id, name, today, now, confidence)
        )
        self.conn.commit()
        return True

    def _is_duplicate(self, student_id, date):
        self.cursor.execute(
            "SELECT time FROM attendance WHERE student_id = ? AND date = ? ORDER BY time DESC LIMIT 1",
            (student_id, date)
        )
        row = self.cursor.fetchone()
        if row is None:
            return False
        last_time = datetime.strptime(row[0], "%H:%M:%S")
        now = datetime.now()
        diff = (now - now.replace(hour=last_time.hour, minute=last_time.minute, second=last_time.second)).total_seconds()
        return diff < ATTENDANCE_COOLDOWN_MINUTES * 60

    def get_attendance_by_date(self, date):
        self.cursor.execute(
            "SELECT student_id, name, time, confidence FROM attendance WHERE date = ? ORDER BY time",
            (date,)
        )
        return self.cursor.fetchall()

    def get_attendance_report(self, start_date, end_date):
        self.cursor.execute(
            """SELECT student_id, name, date, time, confidence
               FROM attendance WHERE date BETWEEN ? AND ?
               ORDER BY date, time""",
            (start_date, end_date)
        )
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()
