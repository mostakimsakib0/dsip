import numpy as np
from backend.face_recognition.matcher import FaceMatcher


def test_cosine_similarity_identical():
    matcher = FaceMatcher()
    emb = np.random.rand(512).astype(np.float32)
    emb = emb / np.linalg.norm(emb)
    score = matcher.cosine_similarity(emb, emb)
    assert abs(score - 1.0) < 1e-6


def test_cosine_similarity_orthogonal():
    matcher = FaceMatcher()
    a = np.array([1.0, 0.0], dtype=np.float32)
    b = np.array([0.0, 1.0], dtype=np.float32)
    score = matcher.cosine_similarity(a, b)
    assert abs(score) < 1e-6


def test_find_best_match():
    matcher = FaceMatcher()
    emb = np.random.rand(512).astype(np.float32)
    emb = emb / np.linalg.norm(emb)
    known = [('001', 'Alice', emb), ('002', 'Bob', -emb)]
    match = matcher.find_best_match(emb, known)
    assert match[0] == '001'


def test_recognition_threshold():
    matcher = FaceMatcher()
    assert matcher.is_recognized(0.5) is True
    assert matcher.is_recognized(0.2) is False


# vim: ts=4:et
