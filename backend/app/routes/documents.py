"""Document management endpoints."""

from fastapi import APIRouter, UploadFile, File, HTTPException, status
from pydantic import ValidationError

from app.models.schemas import (
    DocumentUploadResponse,
    DocumentListResponse,
    DocumentDeleteResponse,
)
from app.dependencies import DocumentServiceDep

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    document_service: DocumentServiceDep,
    file: UploadFile = File(...),
):
    """
    Upload a PDF document, extract text, chunk it, generate embeddings,
    and store it in the vector database.
    """
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported.",
        )

    try:
        result = await document_service.ingest_document(file)
        return DocumentUploadResponse(
            document_id=result["document_id"],
            filename=result["filename"],
            total_pages=result["total_pages"],
            total_chunks=result["total_chunks"],
            message="Document successfully ingested.",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process document: {str(e)}",
        )


@router.get(
    "/",
    response_model=DocumentListResponse,
)
async def list_documents(document_service: DocumentServiceDep):
    """List all ingested documents."""
    docs = document_service.get_all_documents()
    return DocumentListResponse(documents=docs, total=len(docs))


@router.delete(
    "/{document_id}",
    response_model=DocumentDeleteResponse,
)
async def delete_document(
    document_id: str,
    document_service: DocumentServiceDep,
):
    """Delete a document and all its chunks from the vector database."""
    success = document_service.delete_document(document_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{document_id}' not found.",
        )

    return DocumentDeleteResponse(
        document_id=document_id,
        message="Document successfully deleted.",
    )
