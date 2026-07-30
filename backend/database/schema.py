STUDENT_TABLE = """
CREATE TABLE IF NOT EXISTS students (
    student_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    department TEXT NOT NULL,
    face_embedding BLOB NOT NULL
);
"""

ATTENDANCE_TABLE = """
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    name TEXT NOT NULL,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    confidence REAL NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);
"""
