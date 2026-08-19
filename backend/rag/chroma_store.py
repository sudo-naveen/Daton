import os
import uuid
import logging
from typing import List, Dict, Any
import chromadb
import backend.config as config

logger = logging.getLogger("daton.rag")

_client = None


def get_chroma_client():
    global _client
    if _client is None:
        os.makedirs(config.CHROMA_PERSIST_DIR, exist_ok=True)
        _client = chromadb.PersistentClient(path=config.CHROMA_PERSIST_DIR)
    return _client


def get_or_create_collection(name: str = "daton_documents"):
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"},
    )


def add_documents(
    chunks: List[Dict[str, Any]],
    filename: str,
    collection_name: str = "daton_documents",
):
    collection = get_or_create_collection(collection_name)

    existing = collection.get(where={"filename": filename})
    if existing and existing["ids"]:
        collection.delete(ids=existing["ids"])
        logger.info("Removed %d existing chunks for %s", len(existing["ids"]), filename)

    ids = []
    documents = []
    metadatas = []

    for chunk in chunks:
        page = chunk.get("page_number", 0)
        cid = chunk.get("chunk_id", 0)
        doc_id = f"{filename}_p{page}_c{cid}_{uuid.uuid4().hex[:8]}"
        ids.append(doc_id)
        documents.append(chunk["content"])
        metadatas.append({
            "filename": filename,
            "page_number": page,
            "chunk_id": cid,
        })

    batch_size = 100
    for i in range(0, len(ids), batch_size):
        collection.add(
            ids=ids[i:i + batch_size],
            documents=documents[i:i + batch_size],
            metadatas=metadatas[i:i + batch_size],
        )

    logger.info("Added %d chunks for %s", len(ids), filename)
    return {"status": "success", "chunks_added": len(ids)}


def query_documents(
    query: str,
    n_results: int = 5,
    collection_name: str = "daton_documents",
    max_distance: float = 0.8,
) -> List[Dict[str, Any]]:
    collection = get_or_create_collection(collection_name)

    try:
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
        )
    except Exception as e:
        logger.error("ChromaDB query failed: %s", e)
        return []

    docs = []
    if results and results.get("documents") and results["documents"][0]:
        for i, doc in enumerate(results["documents"][0]):
            meta = results["metadatas"][0][i] if results.get("metadatas") else {}
            dist = results["distances"][0][i] if results.get("distances") else None
            if dist is not None and dist > max_distance:
                continue
            docs.append({
                "content": doc,
                "metadata": meta,
                "distance": dist,
            })

    return docs


def delete_document(filename: str, collection_name: str = "daton_documents"):
    collection = get_or_create_collection(collection_name)
    results = collection.get(where={"filename": filename})
    if results and results["ids"]:
        collection.delete(ids=results["ids"])
        logger.info("Deleted %d chunks for %s", len(results["ids"]), filename)
        return {"status": "deleted", "count": len(results["ids"])}
    return {"status": "not_found", "count": 0}


def list_all_documents(collection_name: str = "daton_documents") -> List[Dict[str, Any]]:
    collection = get_or_create_collection(collection_name)
    all_docs = collection.get()
    file_map = {}
    if all_docs and all_docs.get("metadatas"):
        for i, meta in enumerate(all_docs["metadatas"]):
            fname = meta.get("filename", "unknown")
            if fname not in file_map:
                file_map[fname] = {
                    "filename": fname,
                    "chunk_count": 0,
                    "pages": set(),
                }
            file_map[fname]["chunk_count"] += 1
            file_map[fname]["pages"].add(meta.get("page_number", 0))

    result = []
    for info in file_map.values():
        info["pages"] = sorted(list(info["pages"]))
        result.append(info)
    return result
