from backend.face_recognition.detector import FaceDetector
from backend.face_recognition.embedder import FaceEmbedder
from backend.face_recognition.matcher import FaceMatcher
from backend.face_recognition.preprocess import Preprocessor
from backend.database.db_manager import DatabaseManager


class FaceRecognizer:
    def __init__(self):
        self.detector = FaceDetector()
        self.embedder = FaceEmbedder()
        self.matcher = FaceMatcher()
        self.preprocessor = Preprocessor()
        self.db = DatabaseManager()

    def preprocess(self, frame):
        if self.preprocessor.should_apply():
            return self.preprocessor.process(frame)
        return frame

    def recognize(self, frame):
        frame = self.preprocess(frame)
        faces = self.detector.detect(frame)
        results = []

        known_embeddings = self.db.get_all_embeddings()

        for face in faces:
            bbox = face.bbox.astype(int).tolist()
            embedding = self.embedder.extract_embedding(face)
            match = self.matcher.find_best_match(embedding, known_embeddings)

            if match and self.matcher.is_recognized(match[2]):
                sid, name, confidence = match
                attended = self.db.mark_attendance(sid, name, confidence)
                results.append({
                    'student_id': sid,
                    'name': name,
                    'confidence': round(float(confidence), 4),
                    'bbox': bbox,
                    'attended': attended
                })
            else:
                results.append({
                    'student_id': None,
                    'name': 'Unknown',
                    'confidence': 0.0,
                    'bbox': bbox,
                    'attended': False
                })

        return results
