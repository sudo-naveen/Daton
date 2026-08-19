import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from backend.database.connection import test_connection, get_tables, get_table_schema, get_full_schema, get_engine
import backend.config as config

logger = logging.getLogger("daton.api.database")

router = APIRouter(prefix="/api/database", tags=["database"])


class DatabaseTestRequest(BaseModel):
    database_url: Optional[str] = None


class DatabaseConnectRequest(BaseModel):
    database_url: str = Field(..., min_length=1)


@router.post("/test")
def test_db_connection(request: DatabaseTestRequest):
    url = request.database_url or config.DATABASE_URL
    result = test_connection(url)
    return result


@router.post("/connect")
def connect_database(request: DatabaseConnectRequest):
    try:
        get_engine(request.database_url)
        result = test_connection(request.database_url)
        return result
    except Exception as e:
        logger.error("Connection failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Connection error: {str(e)}")


@router.get("/tables")
def list_tables():
    try:
        tables = get_tables()
        return {"tables": tables}
    except Exception as e:
        logger.error("Failed to list tables: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schema")
def get_schema():
    try:
        schema = get_full_schema()
        return {"schema": schema}
    except Exception as e:
        logger.error("Failed to get schema: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schema/{table_name}")
def get_table_info(table_name: str):
    try:
        info = get_table_schema(table_name)
        return info
    except Exception as e:
        logger.error("Failed to get table schema: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
