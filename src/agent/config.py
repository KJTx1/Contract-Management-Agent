"""Configuration for Logistics Document RAG Assistant."""

import os
from pathlib import Path
from typing import Optional

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed


class Config:
    """Configuration settings for the RAG system."""
    
    # Base paths
    BASE_DIR = Path(__file__).parent.parent.parent
    DATA_DIR = BASE_DIR / "data"
    DB_PATH = DATA_DIR / "logistics.db"
    FAISS_INDEX_PATH = DATA_DIR / "faiss_index.index"
    PDF_STORAGE_DIR = DATA_DIR / "pdfs"
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    COHERE_API_KEY = os.getenv("COHERE_API_KEY", "")
    
    # Embedding Configuration
    EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "openai")  # openai or cohere
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSIONS", "1536"))  # text-embedding-3-small dimension
    
    # LLM Configuration
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
    
    # Chunking Configuration
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))  # tokens
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))  # tokens
    
    # Retrieval Configuration
    TOP_K = int(os.getenv("TOP_K", "50"))  # Increased for 250+ documents
    SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.1"))  # Lowered for better recall with large datasets
    
    
    @classmethod
    def setup_directories(cls):
        """Create necessary directories if they don't exist."""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.PDF_STORAGE_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def validate(cls):
        """Validate required configuration."""
        errors = []
        
        if not cls.OPENAI_API_KEY and cls.EMBEDDING_PROVIDER == "openai":
            errors.append("OPENAI_API_KEY is required when using OpenAI embeddings")
        
        if not cls.COHERE_API_KEY and cls.EMBEDDING_PROVIDER == "cohere":
            errors.append("COHERE_API_KEY is required when using Cohere embeddings")
        
        if errors:
            raise ValueError("Configuration errors:\n" + "\n".join(errors))


# Initialize directories on import
Config.setup_directories()

