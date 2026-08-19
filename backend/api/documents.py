import os
import uuid
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List
import backend.config as config
from backend.rag.retriever import ingest_document, remove_document, list_uploaded_documents

logger = logging.getLogger("daton.api.documents")

router = APIRouter(prefix="/api/documents", tags=["documents"])


class UploadResponse(BaseModel):
    status: str
    filename: str
    chunks_indexed: int


def _safe_filename(filename: str) -> str:
    return os.path.basename(filename)


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    safe_name = _safe_filename(file.filename)
    ext = os.path.splitext(safe_name)[1].lower()
    if ext not in config.ALLOWED_DOC_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Allowed: {', '.join(sorted(config.ALLOWED_DOC_EXTENSIONS))}"
        )

    content = await file.read()
    if len(content) > config.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File too large. Max size: {config.MAX_FILE_SIZE_MB}MB")

    os.makedirs(config.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(config.UPLOAD_DIR, safe_name)

    with open(file_path, "wb") as f:
        f.write(content)

    try:
        result = ingest_document(file_path, safe_name)
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        logger.info("Document uploaded: %s (%d chunks)", safe_name, result["chunks_indexed"])
        return UploadResponse(
            status="success",
            filename=result["filename"],
            chunks_indexed=result["chunks_indexed"],
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Ingestion failed for %s: %s", safe_name, e)
        raise HTTPException(status_code=500, detail=f"Ingestion error: {str(e)}")


@router.get("")
def get_documents():
    docs = list_uploaded_documents()
    return {"documents": docs}


@router.delete("/{filename}")
def delete_document(filename: str):
    safe_name = _safe_filename(filename)
    result = remove_document(safe_name)
    upload_path = os.path.join(config.UPLOAD_DIR, safe_name)
    if os.path.exists(upload_path):
        os.remove(upload_path)
    logger.info("Document deleted: %s", safe_name)
    return result
