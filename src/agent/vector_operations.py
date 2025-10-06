"""FAISS vector store operations."""

import numpy as np
import faiss
from pathlib import Path
from typing import List, Tuple, Optional

from .config import Config


class VectorStore:
    """FAISS vector store for embeddings."""
    
    def __init__(self, index_path: Optional[Path] = None):
        self.index_path = index_path or Config.FAISS_INDEX_PATH
        self.dimension = Config.EMBEDDING_DIMENSION
        self.index = self._load_or_create_index()
    
    def _load_or_create_index(self) -> faiss.Index:
        """Load existing index or create new one."""
        if self.index_path.exists():
            try:
                index = faiss.read_index(str(self.index_path))
                print(f"Loaded FAISS index with {index.ntotal} vectors")
                return index
            except Exception as e:
                print(f"Warning: Could not load index: {e}. Creating new index.")
        
        # Start with simple index for small datasets
        # Will automatically upgrade to IVF when we have enough vectors
        index = faiss.IndexFlatL2(self.dimension)
        print(f"Created new FAISS index with dimension {self.dimension}")
        return index
    
    def add_vectors(self, embeddings: np.ndarray) -> List[int]:
        """Add vectors to the index.
        
        Args:
            embeddings: numpy array of shape (n, dimension)
        
        Returns:
            List of IDs for the added vectors
        """
        if embeddings.ndim == 1:
            embeddings = embeddings.reshape(1, -1)
        
        # Normalize vectors for better similarity search
        faiss.normalize_L2(embeddings)
        
        # Check if we need to upgrade to IVF index for better performance
        if (isinstance(self.index, faiss.IndexFlatL2) and 
            self.index.ntotal + len(embeddings) >= 100):
            self._upgrade_to_ivf_index()
        
        # For IVF index, need to train if not already trained
        if hasattr(self.index, 'is_trained') and not self.index.is_trained:
            if self.index.ntotal == 0:
                # Train on a subset of data if available
                self.index.train(embeddings)
        
        start_id = self.index.ntotal
        self.index.add(embeddings)
        
        # Save index
        self.save()
        
        return list(range(start_id, self.index.ntotal))
    
    def _upgrade_to_ivf_index(self):
        """Upgrade from FlatL2 to IVF index for better performance with large datasets."""
        if isinstance(self.index, faiss.IndexFlatL2) and self.index.ntotal >= 50:
            print("🔄 Upgrading to IVF index for better performance...")
            
            # Get all existing vectors
            all_vectors = self.index.reconstruct_n(0, self.index.ntotal)
            
            # Create new IVF index
            nlist = min(100, max(10, self.index.ntotal // 10))  # Adaptive cluster count
            quantizer = faiss.IndexFlatL2(self.dimension)
            new_index = faiss.IndexIVFFlat(quantizer, self.dimension, nlist)
            
            # Train the new index
            new_index.train(all_vectors)
            
            # Add all vectors to the new index
            new_index.add(all_vectors)
            
            # Replace the old index
            self.index = new_index
            print(f"✅ Upgraded to IVF index with {nlist} clusters")
    
    def search(self, query_embedding: np.ndarray, k: int = 5) -> Tuple[np.ndarray, np.ndarray]:
        """Search for similar vectors.
        
        Args:
            query_embedding: Query vector of shape (dimension,)
            k: Number of results to return
        
        Returns:
            Tuple of (distances, indices)
        """
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)
        
        # Normalize query vector
        faiss.normalize_L2(query_embedding)
        
        # Search
        distances, indices = self.index.search(query_embedding, k)
        
        return distances[0], indices[0]
    
    def save(self):
        """Save index to disk."""
        faiss.write_index(self.index, str(self.index_path))
    
    def get_vector_count(self) -> int:
        """Get number of vectors in index."""
        return self.index.ntotal
    
    def reset(self):
        """Reset the index (delete all vectors)."""
        self.index = faiss.IndexFlatL2(self.dimension)
        if self.index_path.exists():
            self.index_path.unlink()
        print("FAISS index reset")


class EmbeddingGenerator:
    """Generate embeddings using OpenAI or Cohere."""
    
    def __init__(self):
        self.provider = Config.EMBEDDING_PROVIDER
        self.model = Config.EMBEDDING_MODEL
        self._init_client()
    
    def _init_client(self):
        """Initialize embedding client."""
        if self.provider == "openai":
            from openai import OpenAI
            self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        elif self.provider == "cohere":
            import cohere
            self.client = cohere.Client(api_key=Config.COHERE_API_KEY)
        else:
            raise ValueError(f"Unsupported embedding provider: {self.provider}")
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for a single text."""
        return self.generate_embeddings([text])[0]
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for multiple texts.
        
        Returns:
            numpy array of shape (len(texts), dimension)
        """
        if self.provider == "openai":
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            embeddings = [item.embedding for item in response.data]
            return np.array(embeddings, dtype=np.float32)
        
        elif self.provider == "cohere":
            response = self.client.embed(
                texts=texts,
                model=self.model,
                input_type="search_document"
            )
            return np.array(response.embeddings, dtype=np.float32)
        
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def generate_query_embedding(self, query: str) -> np.ndarray:
        """Generate embedding for a search query."""
        if self.provider == "cohere":
            # Cohere has special input_type for queries
            response = self.client.embed(
                texts=[query],
                model=self.model,
                input_type="search_query"
            )
            return np.array(response.embeddings[0], dtype=np.float32)
        else:
            return self.generate_embedding(query)

