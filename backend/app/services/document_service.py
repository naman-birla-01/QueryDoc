"""Document orchestration service.

Coordinates the pipeline for document ingestion:
1. Save uploaded file to disk.
2. Extract text from PDF.
3. Chunk text.
4. Generate embeddings.
5. Store in vector database.
"""

import logging
import os
import uuid
import shutil
from pathlib import Path

from fastapi import UploadFile

from app.models.schemas import DocumentInfo
from app.services.pdf_service import PDFService
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStoreService

logger = logging.getLogger(__name__)


class DocumentService:
    """Orchestrate document ingestion and management."""

    def __init__(
        self,
        upload_dir: str,
        pdf_service: PDFService,
        chunking_service: ChunkingService,
        embedding_service: EmbeddingService,
        vector_store: VectorStoreService,
    ):
        self.upload_dir = Path(upload_dir)
        self.pdf_service = pdf_service
        self.chunking_service = chunking_service
        self.embedding_service = embedding_service
        self.vector_store = vector_store

        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def ingest_document(self, file: UploadFile) -> dict:
        """
        Full pipeline to ingest a PDF document.

        Args:
            file: FastAPI UploadFile object.

        Returns:
            Dict containing ingestion summary stats.
        """
        # 1. Generate unique ID and save file
        document_id = str(uuid.uuid4())
        filename = file.filename or "unknown.pdf"
        file_path = self.upload_dir / f"{document_id}_{filename}"

        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            logger.info("Saved upload to %s", file_path)

            # 2. Extract Text
            pages = self.pdf_service.extract_text(str(file_path))
            total_pages = len(pages)

            # 3. Chunk Text
            chunks = self.chunking_service.chunk_pages(
                pages=pages,
                document_id=document_id,
                filename=filename,
            )

            if not chunks:
                raise ValueError("No text chunks generated from document.")

            # 4. Generate Embeddings
            texts_to_embed = [c["text"] for c in chunks]
            embeddings = self.embedding_service.embed_texts(texts_to_embed)

            # 5. Store in Vector DB
            chunks_stored = self.vector_store.add_chunks(
                chunks=chunks,
                embeddings=embeddings,
            )

            return {
                "document_id": document_id,
                "filename": filename,
                "total_pages": total_pages,
                "total_chunks": chunks_stored,
            }

        except Exception as e:
            logger.error("Document ingestion failed: %s", e)
            # Cleanup saved file if processing fails
            if file_path.exists():
                file_path.unlink()
            raise

    def get_all_documents(self) -> list[DocumentInfo]:
        """List all ingested documents using vector store metadata."""
        # This is a basic implementation. For production, you'd want a SQL
        # database to track document metadata properly.
        doc_ids = self.vector_store.get_document_ids()
        
        docs = []
        for doc_id in doc_ids:
            # We reconstruct some info from the first chunk we find
            # This is slow and hacky, but works for a demo
            res = self.vector_store.collection.get(
                where={"document_id": doc_id},
                limit=1,
                include=["metadatas"]
            )
            
            if res and res["metadatas"]:
                meta = res["metadatas"][0]
                chunks = self.vector_store.get_chunk_count(doc_id)
                docs.append(
                    DocumentInfo(
                        document_id=doc_id,
                        filename=meta.get("filename", "unknown"),
                        total_pages=meta.get("page_number", 0), # Not completely accurate, but close enough for demo
                        total_chunks=chunks,
                        uploaded_at="N/A (Stored in DB)"
                    )
                )

        return docs

    def delete_document(self, document_id: str) -> bool:
        """Delete a document from vector store and disk."""
        # 1. Delete from Vector DB
        deleted_chunks = self.vector_store.delete_document(document_id)
        
        # 2. Delete from disk
        file_deleted = False
        for f in self.upload_dir.glob(f"{document_id}_*"):
            try:
                f.unlink()
                file_deleted = True
                logger.info("Deleted file %s", f.name)
            except OSError as e:
                logger.error("Failed to delete file %s: %s", f.name, e)
                
        return deleted_chunks > 0 or file_deleted
