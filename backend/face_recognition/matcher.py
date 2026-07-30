import numpy as np
from backend.config import SIMILARITY_THRESHOLD


class FaceMatcher:
    def cosine_similarity(self, emb_a, emb_b):
        dot = np.dot(emb_a, emb_b)
        norm_a = np.linalg.norm(emb_a)
        norm_b = np.linalg.norm(emb_b)
        return dot / (norm_a * norm_b)

    def find_best_match(self, query_embedding, known_embeddings):
        best_score = -1
        best_match = None

        for sid, name, emb in known_embeddings:
            score = self.cosine_similarity(query_embedding, emb)
            if score > best_score:
                best_score = score
                best_match = (sid, name, score)

        return best_match

    def is_recognized(self, score):
        return score >= SIMILARITY_THRESHOLD
