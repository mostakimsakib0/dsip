import cv2
import insightface
from backend.config import DETECTION_MODEL


class FaceDetector:
    def __init__(self):
        self.model = insightface.app.FaceAnalysis(name=DETECTION_MODEL)
        self.model.prepare(ctx_id=0, det_size=(640, 640))

    def detect(self, frame):
        faces = self.model.get(frame)
        return faces

    def detect_single(self, frame):
        faces = self.detect(frame)
        if len(faces) == 0:
            return None
        return faces[0]
