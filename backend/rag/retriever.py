from typing import List, Dict, Any
from backend.rag.ingestion import extract_and_chunk
from backend.rag.chroma_store import add_documents, query_documents, delete_document, list_all_documents


def ingest_document(file_path: str, filename: str) -> Dict[str, Any]:
    chunks = extract_and_chunk(file_path)
    if not chunks:
        return {"status": "error", "message": "No content could be extracted from the file"}

    result = add_documents(chunks, filename)
    return {
        "status": "success",
        "filename": filename,
        "chunks_indexed": result["chunks_added"],
    }


def search_documents(query: str, n_results: int = 5) -> List[Dict[str, Any]]:
    return query_documents(query, n_results)


def remove_document(filename: str) -> Dict[str, Any]:
    return delete_document(filename)


def list_uploaded_documents() -> List[Dict[str, Any]]:
    return list_all_documents()
