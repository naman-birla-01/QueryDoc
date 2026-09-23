"""PDF text extraction service.

Handles reading PDF files and extracting text content page-by-page.
"""

import logging
from pathlib import Path
from PyPDF2 import PdfReader

logger = logging.getLogger(__name__)


class PDFService:
    """Extract text content from PDF documents."""

    @staticmethod
    def extract_text(file_path: str) -> list[dict]:
        """
        Extract text from each page of a PDF file.

        Args:
            file_path: Absolute path to the PDF file.

        Returns:
            List of dicts with 'page_number' (1-indexed) and 'text' keys.

        Raises:
            ValueError: If the file is not a valid PDF or has no extractable text.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        if path.suffix.lower() != ".pdf":
            raise ValueError(f"Expected a PDF file, got: {path.suffix}")

        try:
            reader = PdfReader(str(path))
        except Exception as e:
            raise ValueError(f"Failed to read PDF: {e}")

        pages = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text and text.strip():
                pages.append({
                    "page_number": i + 1,
                    "text": text.strip(),
                })

        if not pages:
            raise ValueError(
                "No extractable text found in the PDF. "
                "The document may be scanned/image-based."
            )

        logger.info(
            "Extracted text from %d pages of '%s'",
            len(pages), path.name,
        )
        return pages

    @staticmethod
    def get_page_count(file_path: str) -> int:
        """Return the total number of pages in a PDF."""
        reader = PdfReader(file_path)
        return len(reader.pages)
