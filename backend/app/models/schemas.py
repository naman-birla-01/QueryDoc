from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ── Document Schemas ──────────────────────────────────────────────────────────

class DocumentUploadResponse(BaseModel):
    """Response returned after a document is uploaded and ingested."""
    document_id: str
    filename: str
    total_pages: int
    total_chunks: int
    message: str


class DocumentInfo(BaseModel):
    """Summary info about an ingested document."""
    document_id: str
    filename: str
    total_pages: int
    total_chunks: int
    uploaded_at: str


class DocumentListResponse(BaseModel):
    """Response containing all ingested documents."""
    documents: list[DocumentInfo]
    total: int


class DocumentDeleteResponse(BaseModel):
    """Response after deleting a document."""
    document_id: str
    message: str


# ── Query Schemas ─────────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    """Request body for querying documents."""
    question: str = Field(..., min_length=1, max_length=2000)
    document_id: Optional[str] = Field(
        None,
        description="Optional: restrict search to a specific document"
    )
    top_k: Optional[int] = Field(
        None,
        ge=1,
        le=20,
        description="Number of chunks to retrieve (default from config)"
    )


class SourceChunk(BaseModel):
    """A retrieved chunk with metadata for source citation."""
    text: str
    page_number: int
    chunk_index: int
    document_id: str
    filename: str
    relevance_score: float


class QueryResponse(BaseModel):
    """Response containing the generated answer and source citations."""
    answer: str
    sources: list[SourceChunk]
    question: str
    documents_searched: int
