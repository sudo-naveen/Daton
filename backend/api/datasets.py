import os
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import backend.config as config

logger = logging.getLogger("daton.api.datasets")

router = APIRouter(prefix="/api/datasets", tags=["datasets"])


class DatasetInfo(BaseModel):
    filename: str
    path: str
    rows: Optional[int] = None
    columns: Optional[List[str]] = None


datasets_store: dict = {}


def _safe_filename(filename: str) -> str:
    return os.path.basename(filename)


@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    safe_name = _safe_filename(file.filename)
    ext = os.path.splitext(safe_name)[1].lower()
    if ext not in config.ALLOWED_DATASET_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Allowed: {', '.join(sorted(config.ALLOWED_DATASET_EXTENSIONS))}"
        )

    content = await file.read()
    if len(content) > config.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File too large. Max size: {config.MAX_FILE_SIZE_MB}MB")

    os.makedirs(config.DATASETS_DIR, exist_ok=True)
    file_path = os.path.join(config.DATASETS_DIR, safe_name)

    with open(file_path, "wb") as f:
        f.write(content)

    try:
        import pandas as pd
        if ext == ".csv":
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        info = DatasetInfo(
            filename=safe_name,
            path=file_path,
            rows=len(df),
            columns=list(df.columns),
        )
        datasets_store[safe_name] = info
        logger.info("Dataset uploaded: %s (%d rows, %d cols)", safe_name, len(df), len(df.columns))

        return {
            "status": "success",
            "filename": safe_name,
            "rows": len(df),
            "columns": list(df.columns),
        }
    except Exception as e:
        logger.error("Dataset processing failed for %s: %s", safe_name, e)
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@router.get("")
def list_datasets():
    return {"datasets": [d.model_dump() for d in datasets_store.values()]}


@router.delete("/{filename}")
def delete_dataset(filename: str):
    safe_name = _safe_filename(filename)
    if safe_name in datasets_store:
        path = datasets_store[safe_name].path
        if os.path.exists(path):
            os.remove(path)
        del datasets_store[safe_name]
        logger.info("Dataset deleted: %s", safe_name)
        return {"status": "deleted"}
    raise HTTPException(status_code=404, detail="Dataset not found")
