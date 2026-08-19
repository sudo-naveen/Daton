import os
import uuid
from typing import List, Dict, Any
from pathlib import Path
import backend.config as config


def extract_text_from_pdf(file_path: str) -> List[Dict[str, Any]]:
    try:
        import PyPDF2
        pages = []
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text and text.strip():
                    pages.append({"content": text.strip(), "page_number": i + 1})
        return pages
    except Exception as e:
        return [{"content": f"Error reading PDF: {str(e)}", "page_number": 0}]


def extract_text_from_docx(file_path: str) -> List[Dict[str, Any]]:
    try:
        import docx
        doc = docx.Document(file_path)
        full_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        return [{"content": full_text, "page_number": 1}]
    except Exception as e:
        return [{"content": f"Error reading DOCX: {str(e)}", "page_number": 1}]


def extract_text_from_txt(file_path: str) -> List[Dict[str, Any]]:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        return [{"content": text, "page_number": 1}]
    except Exception as e:
        return [{"content": f"Error reading TXT: {str(e)}", "page_number": 1}]


def extract_text_from_csv(file_path: str) -> List[Dict[str, Any]]:
    try:
        import pandas as pd
        df = pd.read_csv(file_path)
        content = df.to_string(index=False)
        return [{"content": content, "page_number": 1}]
    except Exception as e:
        return [{"content": f"Error reading CSV: {str(e)}", "page_number": 1}]


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
        if start + overlap >= len(text):
            break
    return chunks


def extract_and_chunk(file_path: str) -> List[Dict[str, Any]]:
    ext = Path(file_path).suffix.lower()

    if ext == ".pdf":
        pages = extract_text_from_pdf(file_path)
    elif ext == ".docx":
        pages = extract_text_from_docx(file_path)
    elif ext == ".txt":
        pages = extract_text_from_txt(file_path)
    elif ext == ".csv":
        pages = extract_text_from_csv(file_path)
    else:
        return []

    all_chunks = []
    for page in pages:
        page_chunks = chunk_text(page["content"])
        for i, chunk in enumerate(page_chunks):
            all_chunks.append({
                "content": chunk,
                "page_number": page["page_number"],
                "chunk_id": i,
            })

    return all_chunks
