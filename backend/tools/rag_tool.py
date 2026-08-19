import json
import logging
from langchain_core.tools import tool
from backend.rag.retriever import search_documents

logger = logging.getLogger("daton.tools.rag")


@tool
def rag_search(query: str) -> str:
    """Search uploaded documents for relevant information. Returns text chunks with source file and page number."""
    try:
        logger.info("RAG search: %s", query)
        results = search_documents(query, n_results=5)
        if not results:
            return "No relevant information found in uploaded documents."

        parts = []
        for i, doc in enumerate(results, 1):
            metadata = doc.get("metadata", {})
            source = metadata.get("filename", "unknown")
            page = metadata.get("page_number", "N/A")
            content = doc.get("content", "")

            parts.append(
                f"[Result {i}]\n"
                f"Source: {source}\n"
                f"Page: {page}\n"
                f"Content: {content}"
            )

        return "\n\n".join(parts)
    except Exception as e:
        return f"RAG error: {str(e)}"
