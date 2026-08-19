import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import backend.config as config

logger = logging.getLogger("daton")

os.makedirs(config.DATA_DIR, exist_ok=True)
os.makedirs(config.UPLOAD_DIR, exist_ok=True)
os.makedirs(config.DATASETS_DIR, exist_ok=True)
os.makedirs(os.path.join(config.DATA_DIR, "charts"), exist_ok=True)

app = FastAPI(
    title="Daton - AI Data Analyst",
    description="AI-powered data analyst agent with RAG, SQL, and visualization",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from backend.api.chat import router as chat_router
from backend.api.documents import router as documents_router
from backend.api.datasets import router as datasets_router
from backend.api.database import router as database_router

app.include_router(chat_router)
app.include_router(documents_router)
app.include_router(datasets_router)
app.include_router(database_router)

chart_dir = os.path.join(config.DATA_DIR, "charts")
app.mount("/charts", StaticFiles(directory=chart_dir), name="charts")


@app.get("/health")
def health():
    return {"status": "healthy", "service": "Daton AI Analyst"}


@app.get("/")
def root():
    return {
        "name": "Daton - AI Data Analyst",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "chat": "/api/chat",
            "documents": "/api/documents",
            "datasets": "/api/datasets",
            "database": "/api/database",
        },
    }
