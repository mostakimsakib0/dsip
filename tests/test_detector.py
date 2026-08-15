import cv2
import numpy as np
from backend.face_recognition.detector import FaceDetector


def test_detector_initialization():
    detector = FaceDetector()
    assert detector.model is not None


def test_detector_no_face():
    detector = FaceDetector()
    blank = np.zeros((480, 640, 3), dtype=np.uint8)
    faces = detector.detect(blank)
    assert len(faces) == 0


# vim: ts=4:et
