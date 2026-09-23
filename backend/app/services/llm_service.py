"""LLM service for answer generation.

Uses Groq to generate grounded answers from retrieved
document chunks, with source citations.
"""

import logging
from groq import Groq

logger = logging.getLogger(__name__)


class LLMService:
    """Generate answers using Groq with retrieved context."""

    def __init__(self, api_key: str):
        """
        Args:
            api_key: Groq API key.
        """
        if not api_key or api_key == "your-groq-api-key-here":
            logger.warning(
                "No valid Groq API key provided. "
                "LLM-powered answers will use extractive fallback."
            )
            self.client = None
            return

        self.client = Groq(api_key=api_key)
        self.model = "llama3-8b-8192"  # Fast and capable model on Groq
        logger.info(f"Groq LLM initialized ({self.model})")

    def generate_answer(
        self,
        question: str,
        context_chunks: list[dict],
    ) -> str:
        """
        Generate a grounded answer from context chunks.

        If no LLM is configured, falls back to an extractive summary.

        Args:
            question: The user's question.
            context_chunks: List of retrieved chunk dicts with 'text' and 'metadata'.

        Returns:
            The generated answer string.
        """
        if not context_chunks:
            return (
                "I couldn't find any relevant information in the uploaded "
                "documents to answer your question."
            )

        # Build context string with source labels
        context_parts = []
        for i, chunk in enumerate(context_chunks, 1):
            meta = chunk["metadata"]
            context_parts.append(
                f"[Source {i} - {meta['filename']}, Page {meta['page_number']}]\n"
                f"{chunk['text']}"
            )
        context_str = "\n\n---\n\n".join(context_parts)

        if self.client is None:
            return self._extractive_fallback(question, context_chunks)

        system_prompt, user_prompt = self._build_prompt(question, context_str)

        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                model=self.model,
                temperature=0.0,
            )
            answer = response.choices[0].message.content.strip()
            logger.info("Generated LLM answer (%d chars)", len(answer))
            return answer
        except Exception as e:
            logger.error("LLM generation failed: %s", e)
            return self._extractive_fallback(question, context_chunks)

    @staticmethod
    def _build_prompt(question: str, context: str) -> tuple[str, str]:
        """Build the RAG system and user prompts for Groq."""
        system_prompt = """You are a helpful document Q&A assistant. Answer the user's question based ONLY on the provided document context. Follow these rules:

1. Answer ONLY using information from the provided context.
2. If the context doesn't contain enough information to fully answer the question, say so clearly.
3. Reference the source documents and page numbers in your answer (e.g., "According to [Source 1]...").
4. Be concise but thorough.
5. Use bullet points or numbered lists when presenting multiple pieces of information.
6. Do not make up or infer information not present in the context.

--- CONTEXT ---
{context}
--- END CONTEXT ---"""

        user_prompt = f"Question: {question}\n\nAnswer:"
        
        return system_prompt.format(context=context), user_prompt

    @staticmethod
    def _extractive_fallback(
        question: str,
        context_chunks: list[dict],
    ) -> str:
        """
        Fallback when no LLM is available.
        Returns the most relevant chunks as a formatted extractive answer.
        """
        parts = [
            "📄 **Relevant excerpts from your documents:**\n"
            "*(LLM not configured — showing retrieved passages directly)*\n"
        ]

        for i, chunk in enumerate(context_chunks[:3], 1):
            meta = chunk["metadata"]
            score = chunk.get("score", 0)
            parts.append(
                f"**[Source {i}]** {meta['filename']}, "
                f"Page {meta['page_number']} "
                f"(relevance: {score:.0%})\n"
                f"> {chunk['text'][:500]}{'...' if len(chunk['text']) > 500 else ''}\n"
            )

        return "\n".join(parts)
