import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from backend.rag.ingestion import extract_and_chunk, chunk_text
import tempfile


def test_chunk_text():
    text = "A" * 3000
    chunks = chunk_text(text, chunk_size=1000, overlap=200)
    assert len(chunks) > 1
    assert all(len(c) <= 1000 for c in chunks)


def test_extract_txt():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("This is a test document with some content about data analysis and AI.")
        f.flush()
        chunks = extract_and_chunk(f.name)
        assert len(chunks) > 0
        assert "test document" in chunks[0]["content"]
        os.unlink(f.name)


def test_extract_csv():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("name,age\nAlice,30\nBob,25\n")
        f.flush()
        chunks = extract_and_chunk(f.name)
        assert len(chunks) > 0
        assert "Alice" in chunks[0]["content"]
        os.unlink(f.name)
