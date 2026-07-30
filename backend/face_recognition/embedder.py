import numpy as np
from backend.config import EMBEDDING_SIZE


class FaceEmbedder:
    def extract_embedding(self, face):
        return face.normed_embedding

    def embedding_to_array(self, embedding):
        return np.array(embedding, dtype=np.float32)
