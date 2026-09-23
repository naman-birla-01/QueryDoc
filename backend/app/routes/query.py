"""Query execution endpoints."""

from fastapi import APIRouter, HTTPException, status, Depends

from app.models.schemas import QueryRequest, QueryResponse, SourceChunk
from app.config import get_settings, Settings
from app.dependencies import (
    EmbeddingServiceDep,
    VectorStoreDep,
    LLMServiceDep,
)

router = APIRouter(prefix="/query", tags=["query"])


@router.post(
    "/",
    response_model=QueryResponse,
)
async def query_documents(
    request: QueryRequest,
    embedding_service: EmbeddingServiceDep,
    vector_store: VectorStoreDep,
    llm_service: LLMServiceDep,
    settings: Settings = Depends(get_settings),
):
    """
    Query the document knowledge base.
    
    1. Embeds the question.
    2. Retrieves top K relevant chunks from ChromaDB.
    3. Generates an answer using Groq LLaMA3 based on the chunks.
    """
    try:
        # 1. Embed Question
        query_vector = embedding_service.embed_query(request.question)
        
        # 2. Retrieve context chunks
        top_k = request.top_k or settings.top_k
        results = vector_store.query(
            query_embedding=query_vector,
            top_k=top_k,
            document_id=request.document_id,
        )
        
        if not results:
            return QueryResponse(
                answer="No relevant documents found to answer your question.",
                sources=[],
                question=request.question,
                documents_searched=vector_store.total_chunks, # using total_chunks as proxy for DB size
            )

        # 3. Generate answer
        answer = llm_service.generate_answer(
            question=request.question,
            context_chunks=results,
        )
        
        # 4. Format sources
        sources = [
            SourceChunk(
                text=r["text"],
                page_number=r["metadata"]["page_number"],
                chunk_index=r["metadata"]["chunk_index"],
                document_id=r["metadata"]["document_id"],
                filename=r["metadata"]["filename"],
                relevance_score=r["score"],
            )
            for r in results
        ]
        
        return QueryResponse(
            answer=answer,
            sources=sources,
            question=request.question,
            documents_searched=vector_store.total_chunks,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query failed: {str(e)}",
        )
