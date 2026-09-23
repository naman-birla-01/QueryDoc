# QueryDoc — RAG-Based Document Q&A System

<div align="center">

![QueryDoc Banner](https://img.shields.io/badge/QueryDoc-RAG%20Document%20Q%26A-6C63FF?style=for-the-badge&logo=readthedocs&logoColor=white)

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python)](https://python.org)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20Store-FF6B6B?style=flat-square)](https://trychroma.com)
[![Groq](https://img.shields.io/badge/Groq-LLaMA3-F55036?style=flat-square)](https://groq.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

**Upload any PDF. Ask anything about it. Get cited, grounded answers — instantly.**

</div>

---

## ✨ What is QueryDoc?

QueryDoc is a **Retrieval-Augmented Generation (RAG)** system that lets you upload PDF documents and query them using natural language. Instead of hallucinating, the AI answers are grounded exclusively in your uploaded documents, with source citations including page numbers.

### How it works

```
Upload PDF → Extract Text → Chunk → Embed → Store in ChromaDB
                                                 ↓
Ask Question → Embed Question → Semantic Search → Groq LLM → Cited Answer
```

---

## 🏗️ Architecture

```
QueryDoc/
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI app + CORS + lifespan
│   │   ├── config.py             # Pydantic settings (env-driven)
│   │   ├── dependencies.py       # Service singletons + FastAPI DI
│   │   ├── models/
│   │   │   └── schemas.py        # Request/response Pydantic models
│   │   ├── routes/
│   │   │   ├── documents.py      # Upload / list / delete PDFs
│   │   │   └── query.py          # Ask questions (RAG pipeline)
│   │   └── services/
│   │       ├── pdf_service.py        # PyPDF2 text extraction
│   │       ├── chunking_service.py   # Sentence-aware text chunking
│   │       ├── embedding_service.py  # sentence-transformers
│   │       ├── vector_store.py       # ChromaDB operations
│   │       ├── document_service.py   # Ingestion pipeline orchestrator
│   │       └── llm_service.py        # Groq LLaMA3 answer generation
│   ├── .env.example
│   ├── requirements.txt
│   └── run.py
└── frontend/                     # Coming soon
```

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/QueryDoc.git
cd QueryDoc
```

### 2. Set up the Python environment

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in your values:

```env
GROQ_API_KEY=your-groq-api-key-here   # Get from https://console.groq.com
EMBEDDING_MODEL=all-MiniLM-L6-v2
CHROMA_PERSIST_DIR=./chroma_db
UPLOAD_DIR=./uploads
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K=5
```

> 🔑 Get a free Groq API key at [console.groq.com](https://console.groq.com)

### 4. Run the server

```bash
python run.py
```

The API will be live at `http://localhost:8080`

Interactive docs: `http://localhost:8080/docs`

---

## 📡 API Reference

### Documents

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/documents/upload` | Upload a PDF and ingest it |
| `GET` | `/api/v1/documents/` | List all ingested documents |
| `DELETE` | `/api/v1/documents/{document_id}` | Delete a document |

### Query

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/query/` | Ask a question about your documents |

### System

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |

---

### Example: Upload a Document

```bash
curl -X POST http://localhost:8080/api/v1/documents/upload \
  -F "file=@report.pdf"
```

```json
{
  "document_id": "3f8a1c2d-...",
  "filename": "report.pdf",
  "total_pages": 12,
  "total_chunks": 47,
  "message": "Document successfully ingested."
}
```

### Example: Ask a Question

```bash
curl -X POST http://localhost:8080/api/v1/query/ \
  -H "Content-Type: application/json" \
  -d '{"question": "What was the total revenue for Q1?", "top_k": 5}'
```

```json
{
  "answer": "According to [Source 1] (report.pdf, Page 3), the total revenue for Q1 was ₹4,643.55 crores...",
  "sources": [
    {
      "filename": "report.pdf",
      "page_number": 3,
      "relevance_score": 0.91,
      ...
    }
  ],
  "question": "What was the total revenue for Q1?",
  "documents_searched": 47
}
```

---

## ⚙️ Configuration

All settings are controlled via environment variables (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | — | Your Groq API key (**required**) |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | HuggingFace sentence-transformers model |
| `CHUNK_SIZE` | `500` | Characters per text chunk |
| `CHUNK_OVERLAP` | `50` | Overlapping characters between chunks |
| `TOP_K` | `5` | Number of chunks retrieved per query |
| `CHROMA_PERSIST_DIR` | `./chroma_db` | ChromaDB storage path |
| `UPLOAD_DIR` | `./uploads` | PDF upload storage path |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| API Framework | [FastAPI](https://fastapi.tiangolo.com/) |
| PDF Parsing | [PyPDF2](https://pypdf2.readthedocs.io/) |
| Embeddings | [sentence-transformers](https://www.sbert.net/) (`all-MiniLM-L6-v2`) |
| Vector Database | [ChromaDB](https://trychroma.com) (local, persistent) |
| LLM | [Groq](https://groq.com) (LLaMA3-8b) |
| Config | [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) |
| Server | [Uvicorn](https://www.uvicorn.org/) |

---

## 🔒 Security Notes

- ✅ `.env` is in `.gitignore` — your API key is never committed
- ✅ Use `.env.example` as a safe template to share with others
- ✅ The LLM answers **only** from document context — no hallucination
- ⚠️ CORS is set to `*` — restrict `allow_origins` in production

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'feat: add your feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
