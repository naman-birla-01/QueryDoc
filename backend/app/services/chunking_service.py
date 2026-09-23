"""Text chunking service.

Splits extracted page text into smaller, overlapping chunks suitable
for embedding and retrieval.
"""

import logging

logger = logging.getLogger(__name__)


class ChunkingService:
    """Split document text into overlapping chunks."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Args:
            chunk_size: Target number of characters per chunk.
            chunk_overlap: Number of overlapping characters between consecutive chunks.
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_pages(
        self,
        pages: list[dict],
        document_id: str,
        filename: str,
    ) -> list[dict]:
        """
        Chunk extracted page data into smaller segments.

        Args:
            pages: List of dicts with 'page_number' and 'text'.
            document_id: Unique ID of the parent document.
            filename: Original filename.

        Returns:
            List of chunk dicts, each containing:
                - chunk_id, text, page_number, chunk_index,
                  document_id, filename
        """
        all_chunks: list[dict] = []
        global_index = 0

        for page in pages:
            page_text = page["text"]
            page_num = page["page_number"]
            page_chunks = self._split_text(page_text)

            for chunk_text in page_chunks:
                all_chunks.append({
                    "chunk_id": f"{document_id}_chunk_{global_index}",
                    "text": chunk_text,
                    "page_number": page_num,
                    "chunk_index": global_index,
                    "document_id": document_id,
                    "filename": filename,
                })
                global_index += 1

        logger.info(
            "Created %d chunks from %d pages (doc=%s)",
            len(all_chunks), len(pages), document_id,
        )
        return all_chunks

    def _split_text(self, text: str) -> list[str]:
        """
        Split a single text blob into overlapping chunks.

        Uses sentence-boundary-aware splitting: tries to break at
        sentence endings ('. ', '? ', '! ', newlines) to keep chunks
        semantically coherent.
        """
        if len(text) <= self.chunk_size:
            return [text]

        chunks: list[str] = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size

            if end >= len(text):
                chunks.append(text[start:].strip())
                break

            # Try to find a sentence boundary near the end of the chunk
            boundary = self._find_boundary(text, start, end)
            chunk = text[start:boundary].strip()

            if chunk:
                chunks.append(chunk)

            # Move forward, keeping overlap
            start = boundary - self.chunk_overlap
            if start < 0:
                start = 0
            # Prevent infinite loop
            if start >= boundary:
                start = boundary

        return chunks

    @staticmethod
    def _find_boundary(text: str, start: int, end: int) -> int:
        """
        Find the best sentence boundary between start and end.

        Looks backwards from `end` for sentence-ending punctuation
        followed by whitespace. Falls back to `end` if none found.
        """
        search_start = max(start + (end - start) // 2, start)
        best = end

        for sep in [". ", "? ", "! ", "\n\n", "\n"]:
            pos = text.rfind(sep, search_start, end)
            if pos != -1:
                best = pos + len(sep)
                break

        return best
