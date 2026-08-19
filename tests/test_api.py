import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"


def test_root():
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert "Daton" in data["name"]


def test_list_documents():
    resp = client.get("/api/documents")
    assert resp.status_code == 200
    assert "documents" in resp.json()


def test_list_datasets():
    resp = client.get("/api/datasets")
    assert resp.status_code == 200
    assert "datasets" in resp.json()


def test_database_tables():
    resp = client.get("/api/database/tables")
    assert resp.status_code == 200
    assert "tables" in resp.json()


def test_database_schema():
    resp = client.get("/api/database/schema")
    assert resp.status_code == 200
    assert "schema" in resp.json()


def test_chat_validation():
    resp = client.post("/api/chat", json={"message": ""})
    assert resp.status_code == 422


def test_chat_no_backend():
    resp = client.post("/api/chat", json={"message": "hello"})
    assert resp.status_code in (200, 500)
