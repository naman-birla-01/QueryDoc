"""FastAPI dependencies for injecting services into routes."""

from fastapi import Depends
from typing import Annotated

from app.config import get_settings, Settings
from app.services.pdf_service import PDFService
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStoreService
from app.services.document_service import DocumentService
from app.services.llm_service import LLMService

# Global service instances (acting as singletons)
_pdf_service = PDFService()
_chunking_service = None
_embedding_service = None
_vector_store = None
_document_service = None
_llm_service = None


def init_services():
    """Initialize all services on application startup."""
    global _chunking_service, _embedding_service, _vector_store, _document_service, _llm_service
    
    settings = get_settings()
    
    _chunking_service = ChunkingService(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    _embedding_service = EmbeddingService(
        model_name=settings.embedding_model,
    )
    _vector_store = VectorStoreService(
        persist_dir=settings.chroma_persist_dir,
    )
    _document_service = DocumentService(
        upload_dir=settings.upload_dir,
        pdf_service=_pdf_service,
        chunking_service=_chunking_service,
        embedding_service=_embedding_service,
        vector_store=_vector_store,
    )
    _llm_service = LLMService(
        api_key=settings.groq_api_key,
    )

def get_document_service() -> DocumentService:
    if not _document_service:
        raise RuntimeError("Services not initialized")
    return _document_service

def get_vector_store() -> VectorStoreService:
    if not _vector_store:
        raise RuntimeError("Services not initialized")
    return _vector_store

def get_embedding_service() -> EmbeddingService:
    if not _embedding_service:
        raise RuntimeError("Services not initialized")
    return _embedding_service

def get_llm_service() -> LLMService:
    if not _llm_service:
        raise RuntimeError("Services not initialized")
    return _llm_service

DocumentServiceDep = Annotated[DocumentService, Depends(get_document_service)]
VectorStoreDep = Annotated[VectorStoreService, Depends(get_vector_store)]
EmbeddingServiceDep = Annotated[EmbeddingService, Depends(get_embedding_service)]
LLMServiceDep = Annotated[LLMService, Depends(get_llm_service)]
