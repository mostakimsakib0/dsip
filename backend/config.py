import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '..', 'data')
EMBEDDINGS_DIR = os.path.join(DATA_DIR, 'embeddings')
REPORTS_DIR = os.path.join(DATA_DIR, 'reports')
DATABASE_PATH = os.path.join(BASE_DIR, '..', 'attendance.db')

DETECTION_MODEL = 'buffalo_l'
SIMILARITY_THRESHOLD = 0.35
EMBEDDING_SIZE = 512
CONFIDENCE_THRESHOLD = 0.30

FRAME_WIDTH = 640
FRAME_HEIGHT = 480

ATTENDANCE_COOLDOWN_MINUTES = 60
