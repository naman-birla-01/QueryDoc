"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load .env before initializing app components
load_dotenv()

from app.dependencies import init_services
from app.routes import documents, query

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events for the FastAPI application."""
    # Startup
    logging.info("Starting QueryDoc Backend...")
    # Initialize singleton services (loads embedding model, chromadb, etc.)
    init_services()
    logging.info("Services initialized successfully.")
    
    yield
    
    # Shutdown
    logging.info("Shutting down QueryDoc Backend...")


app = FastAPI(
    title="QueryDoc RAG API",
    description="Retrieval-Augmented Generation (RAG) Document Q&A System",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(documents.router, prefix="/api/v1")
app.include_router(query.router, prefix="/api/v1")


@app.get("/health", tags=["system"])
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "service": "QueryDoc API"}
