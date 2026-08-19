from typing import List, Dict, Any
import backend.config as config


def get_embeddings():
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    return GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
        google_api_key=config.GEMINI_API_KEY,
    )
