import logging
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Optional, Dict, Any, List
import backend.config as config

logger = logging.getLogger("daton.database")

engine = None
SessionLocal = None


def get_engine(database_url: Optional[str] = None):
    global engine, SessionLocal
    url = database_url or config.DATABASE_URL
    if url.startswith("sqlite"):
        engine = create_engine(
            url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    else:
        engine = create_engine(url, pool_pre_ping=True)
    SessionLocal = None
    logger.info("Database engine created for: %s", url.split("@")[-1] if "@" in url else url)
    return engine


def get_session() -> Session:
    global SessionLocal
    if SessionLocal is None:
        e = get_engine()
        SessionLocal = sessionmaker(bind=e)
    return SessionLocal()


def _get_inspector():
    global engine
    if engine is None:
        get_engine()
    return inspect(engine)


def get_tables() -> List[str]:
    insp = _get_inspector()
    tables = insp.get_table_names()
    return [t for t in tables if not t.startswith("sqlite_")]


def get_table_schema(table_name: str) -> Dict[str, Any]:
    insp = _get_inspector()
    columns = insp.get_columns(table_name)
    return {
        "table": table_name,
        "columns": [
            {
                "name": col["name"],
                "type": str(col["type"]),
                "nullable": col.get("nullable", True),
            }
            for col in columns
        ],
    }


def get_full_schema() -> Dict[str, Any]:
    tables = get_tables()
    schema = {}
    for t in tables:
        schema[t] = get_table_schema(t)
    return schema


def execute_sql(query: str) -> List[Dict[str, Any]]:
    session = get_session()
    try:
        logger.info("Executing SQL: %s", query[:200])
        result = session.execute(text(query))
        if result.returns_rows:
            columns = result.keys()
            rows = result.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        session.commit()
        return []
    except Exception as e:
        session.rollback()
        logger.error("SQL execution error: %s", e)
        raise
    finally:
        session.close()


def test_connection(database_url: Optional[str] = None) -> Dict[str, Any]:
    try:
        eng = get_engine(database_url)
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection successful")
        return {"status": "connected", "message": "Database connection successful"}
    except Exception as e:
        logger.error("Database connection failed: %s", e)
        return {"status": "error", "message": str(e)}
