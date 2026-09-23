"""Embedding generation service.

Wraps sentence-transformers to generate dense vector embeddings
for text chunks and queries.
"""

import logging
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Generate text embeddings using sentence-transformers."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Args:
            model_name: HuggingFace model identifier for sentence-transformers.
        """
        logger.info("Loading embedding model: %s", model_name)
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        self._dimension = self.model.get_sentence_embedding_dimension()
        logger.info(
            "Embedding model loaded (dim=%d)", self._dimension,
        )

    @property
    def dimension(self) -> int:
        """Embedding vector dimensionality."""
        return self._dimension

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for a batch of texts.

        Args:
            texts: List of text strings to embed.

        Returns:
            List of embedding vectors (each a list of floats).
        """
        if not texts:
            return []

        embeddings = self.model.encode(
            texts,
            show_progress_bar=False,
            convert_to_numpy=True,
        )
        return embeddings.tolist()

    def embed_query(self, query: str) -> list[float]:
        """
        Generate an embedding for a single query string.

        Args:
            query: The query text.

        Returns:
            Embedding vector as a list of floats.
        """
        embedding = self.model.encode(
            [query],
            show_progress_bar=False,
            convert_to_numpy=True,
        )
        return embedding[0].tolist()
