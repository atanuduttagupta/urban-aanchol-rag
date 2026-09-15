from sentence_transformers import SentenceTransformer

from backend.app.database.embedding_config import (
    EMBEDDING_DIMENSIONS,
    MODEL_NAME,
)


class EmbeddingGenerator:
    def __init__(self) -> None:
        self.model = SentenceTransformer(MODEL_NAME)

    def generate(self, text: str) -> list[float]:
        embedding = self.model.encode(
            text,
            normalize_embeddings=True,
        )
        return embedding.tolist()

    @property
    def dimensions(self) -> int:
        return EMBEDDING_DIMENSIONS