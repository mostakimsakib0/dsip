from backend.database.db_manager import DatabaseManager
import numpy as np


def test_register_and_retrieve():
    db = DatabaseManager()
    emb = np.random.rand(512).astype(np.float32)
    db.register_student('999', 'Test User', 'CSE', emb)
    students = db.get_all_students()
    ids = [s[0] for s in students]
    assert '999' in ids
