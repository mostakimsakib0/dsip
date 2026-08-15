import sqlite3
import numpy as np
import pickle
from datetime import datetime
from backend.config import DATABASE_PATH, ATTENDANCE_COOLDOWN_MINUTES, CONFIDENCE_THRESHOLD
from backend.database.schema import INSTRUCTOR_TABLE, STUDENT_TABLE, ATTENDANCE_TABLE

DEFAULT_INSTRUCTOR = {
    'username': 'instructor',
    'password': 'cse434',
    'full_name': 'Course Instructor'
}


class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.execute(INSTRUCTOR_TABLE)
        self.cursor.execute(STUDENT_TABLE)
        self.cursor.execute(ATTENDANCE_TABLE)
        self._seed_instructor()
        self.conn.commit()

    def _seed_instructor(self):
        self.cursor.execute("SELECT COUNT(*) FROM instructors")
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute(
                "INSERT INTO instructors (username, password, full_name) VALUES (?, ?, ?)",
                (DEFAULT_INSTRUCTOR['username'], DEFAULT_INSTRUCTOR['password'],
                 DEFAULT_INSTRUCTOR['full_name'])
            )

    def verify_instructor(self, username, password):
        self.cursor.execute(
            "SELECT username, full_name FROM instructors WHERE username = ? AND password = ?",
            (username, password)
        )
        return self.cursor.fetchone()

    def delete_student(self, student_id):
        self.cursor.execute(
            "DELETE FROM attendance WHERE student_id = ?", (student_id,))
        self.cursor.execute(
            "DELETE FROM students WHERE student_id = ?", (student_id,))
        self.conn.commit()
        return self.cursor.rowcount

    def student_exists(self, student_id):
        self.cursor.execute(
            "SELECT name FROM students WHERE student_id = ?", (student_id,))
        row = self.cursor.fetchone()
        return row[0] if row else None

    def register_student(self, student_id, name, department, embedding):
        blob = pickle.dumps(embedding)
        self.cursor.execute(
            "INSERT OR REPLACE INTO students (student_id, name, department, face_embedding) VALUES (?, ?, ?, ?)",
            (student_id, name, department, blob)
        )
        self.conn.commit()

    def get_all_students(self):
        self.cursor.execute(
            "SELECT student_id, name, department FROM students")
        return self.cursor.fetchall()

    def get_all_embeddings(self):
        self.cursor.execute(
            "SELECT student_id, name, face_embedding FROM students")
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
            (student_id, name, today, now, float(confidence))
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
        diff = (now - now.replace(hour=last_time.hour,
                minute=last_time.minute, second=last_time.second)).total_seconds()
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


# vim: ts=4:et
