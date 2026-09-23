"""ChromaDB vector store service.

Manages storing, querying, and deleting document chunk embeddings
in a persistent ChromaDB collection.
"""

import logging
import chromadb
from chromadb.config import Settings as ChromaSettings

logger = logging.getLogger(__name__)

COLLECTION_NAME = "querydoc_chunks"


class VectorStoreService:
    """Persistent vector store backed by ChromaDB."""

    def __init__(self, persist_dir: str = "./chroma_db"):
        """
        Args:
            persist_dir: Directory for ChromaDB persistent storage.
        """
        logger.info("Initializing ChromaDB at: %s", persist_dir)
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(
            "ChromaDB collection '%s' ready (%d vectors)",
            COLLECTION_NAME, self.collection.count(),
        )

    def add_chunks(
        self,
        chunks: list[dict],
        embeddings: list[list[float]],
    ) -> int:
        """
        Store document chunks with their embeddings.

        Args:
            chunks: List of chunk dicts (must have 'chunk_id', 'text', and metadata fields).
            embeddings: Corresponding embedding vectors.

        Returns:
            Number of chunks added.
        """
        if not chunks:
            return 0

        ids = [c["chunk_id"] for c in chunks]
        documents = [c["text"] for c in chunks]
        metadatas = [
            {
                "page_number": c["page_number"],
                "chunk_index": c["chunk_index"],
                "document_id": c["document_id"],
                "filename": c["filename"],
            }
            for c in chunks
        ]

        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        logger.info("Added %d chunks to vector store", len(ids))
        return len(ids)

    def query(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        document_id: str | None = None,
    ) -> list[dict]:
        """
        Retrieve the most relevant chunks for a query embedding.

        Args:
            query_embedding: The query vector.
            top_k: Number of results to return.
            document_id: Optional filter to a specific document.

        Returns:
            List of result dicts with 'text', 'metadata', and 'score'.
        """
        where_filter = None
        if document_id:
            where_filter = {"document_id": document_id}

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter,
            include=["documents", "metadatas", "distances"],
        )

        parsed: list[dict] = []
        if results and results["ids"] and results["ids"][0]:
            for i, chunk_id in enumerate(results["ids"][0]):
                # ChromaDB cosine distance: lower = more similar
                # Convert to similarity score (1 - distance)
                distance = results["distances"][0][i]
                similarity = 1.0 - distance

                parsed.append({
                    "chunk_id": chunk_id,
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "score": round(similarity, 4),
                })

        return parsed

    def delete_document(self, document_id: str) -> int:
        """
        Remove all chunks belonging to a document.

        Args:
            document_id: The document ID whose chunks should be deleted.

        Returns:
            Number of chunks deleted.
        """
        # Get all chunk IDs for this document
        existing = self.collection.get(
            where={"document_id": document_id},
            include=[],
        )

        if existing and existing["ids"]:
            self.collection.delete(ids=existing["ids"])
            count = len(existing["ids"])
            logger.info(
                "Deleted %d chunks for document '%s'", count, document_id,
            )
            return count

        return 0

    def get_document_ids(self) -> list[str]:
        """Return a list of unique document IDs in the store."""
        all_data = self.collection.get(include=["metadatas"])
        if not all_data or not all_data["metadatas"]:
            return []

        doc_ids = set()
        for meta in all_data["metadatas"]:
            if meta and "document_id" in meta:
                doc_ids.add(meta["document_id"])

        return sorted(doc_ids)

    def get_chunk_count(self, document_id: str) -> int:
        """Return the number of chunks stored for a specific document."""
        result = self.collection.get(
            where={"document_id": document_id},
            include=[],
        )
        return len(result["ids"]) if result and result["ids"] else 0

    @property
    def total_chunks(self) -> int:
        """Total number of chunks across all documents."""
        return self.collection.count()
