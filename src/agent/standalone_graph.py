"""Standalone LangGraph RAG pipeline for LangGraph Studio deployment.

This file contains all necessary imports and logic without relative imports
to work properly with LangGraph Studio's module loading system.
"""

import os
import sys
import sqlite3
import numpy as np
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TypedDict
from pathlib import Path
from contextlib import contextmanager

from langgraph.graph import StateGraph
from langgraph.runtime import Runtime

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Inline configuration
class Config:
    """Configuration settings for the RAG system."""
    
    # Base paths
    BASE_DIR = Path(__file__).parent.parent.parent
    DATA_DIR = BASE_DIR / "data"
    DB_PATH = DATA_DIR / "logistics.db"
    FAISS_INDEX_PATH = DATA_DIR / "faiss_index.index"
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    COHERE_API_KEY = os.getenv("COHERE_API_KEY", "")
    
    # Embedding Configuration
    EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "openai")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    EMBEDDING_DIMENSIONS = int(os.getenv("EMBEDDING_DIMENSIONS", "1536"))
    
    # Retrieval Configuration
    TOP_K = int(os.getenv("TOP_K", "20"))  # Increased to capture more results
    SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.3"))
    
    # Processing Configuration
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))


# Inline database class
class Database:
    """Minimal database operations."""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or Config.DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    async def get_chunk_metadata(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific chunk (async version)."""
        try:
            import asyncio
            
            def _get_metadata():
                with self.get_connection() as conn:
                    cursor = conn.execute("""
                        SELECT 
                            chunk_id,
                            chunk_text as text,
                            customer_name,
                            doc_type,
                            doc_date,
                            pdf_url,
                            pdf_url as document_name
                        FROM chunks
                        WHERE chunk_id = ?
                    """, (int(chunk_id),))
                    row = cursor.fetchone()
                    if row:
                        result = dict(row)
                        # Extract document name from PDF URL
                        if result.get('pdf_url'):
                            import os
                            result['document_name'] = os.path.basename(result['pdf_url']).replace('.pdf', '')
                        return result
                    return None
            
            return await asyncio.to_thread(_get_metadata)
        except Exception as e:
            print(f"Error getting chunk metadata for {chunk_id}: {e}")
            return None


# Inline vector store class
class VectorStore:
    """Minimal FAISS vector store operations."""
    
    def __init__(self):
        self.config = Config()
        self.index = None
        self.chunk_ids = []
        self._load_index()
    
    def _load_index(self):
        """Load FAISS index if it exists."""
        try:
            import faiss
            if self.config.FAISS_INDEX_PATH.exists():
                self.index = faiss.read_index(str(self.config.FAISS_INDEX_PATH))
                # Load the actual chunk ID mapping from database
                self._load_chunk_mapping()
                print(f"Loaded FAISS index with {self.index.ntotal} vectors")
        except Exception as e:
            print(f"Could not load FAISS index: {e}")
            self.index = None
    
    def _load_chunk_mapping(self):
        """Load the mapping from FAISS index to database chunk IDs."""
        try:
            db = Database()
            with db.get_connection() as conn:
                # Get mapping from chunk_embedding_id to chunk_id
                cursor = conn.execute('SELECT chunk_embedding_id, chunk_id FROM chunks ORDER BY chunk_embedding_id')
                embedding_to_chunk = dict(cursor.fetchall())
                
                # Create chunk_ids list where FAISS index i maps to the correct chunk_id
                self.chunk_ids = []
                for faiss_idx in range(self.index.ntotal if self.index else 0):
                    # The FAISS index corresponds to chunk_embedding_id
                    # But we need to account for the fact that embedding_ids might not start from 0
                    embedding_ids = sorted(embedding_to_chunk.keys())
                    
                    if faiss_idx < len(embedding_ids):
                        # Map FAISS index to the corresponding embedding_id
                        embedding_id = embedding_ids[faiss_idx]
                        chunk_id = embedding_to_chunk[embedding_id]
                        self.chunk_ids.append(str(chunk_id))
                    else:
                        # No corresponding chunk in database - this shouldn't happen but handle gracefully
                        self.chunk_ids.append(None)
                        
                print(f"Loaded chunk mapping: {len([x for x in self.chunk_ids if x is not None])} valid mappings out of {len(self.chunk_ids)}")
        except Exception as e:
            print(f"Error loading chunk mapping: {e}")
            # Fallback to simple numbering
            self.chunk_ids = [str(i + 1) for i in range(self.index.ntotal if self.index else 0)]
    
    def search(self, query_embedding: List[float], top_k: int = 5, 
               similarity_threshold: float = 0.3, filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Search for similar vectors."""
        if not self.index or not query_embedding:
            return []
        
        try:
            import faiss
            # Convert to numpy array
            query_vector = np.array([query_embedding], dtype=np.float32)
            
            # Normalize query vector (crucial for similarity search)
            faiss.normalize_L2(query_vector)
            
            # Search
            scores, indices = self.index.search(query_vector, min(top_k, self.index.ntotal))
            
            results = []
            for distance, idx in zip(scores[0], indices[0]):
                if idx >= 0:
                    # Get the correct chunk_id, skip if None (no database mapping)
                    chunk_id = self.chunk_ids[idx] if idx < len(self.chunk_ids) else None
                    if chunk_id is not None:
                        # Convert L2 distance to similarity score (lower distance = higher similarity)
                        # For normalized vectors, similarity = 1 - (distance^2 / 4)
                        similarity = max(0, 1 - (distance * distance / 4))
                        
                        if similarity >= similarity_threshold:
                            results.append({
                                "chunk_id": chunk_id,
                                "score": float(similarity),
                                "distance": float(distance),
                                "index": int(idx)
                            })
            
            return results
        except Exception as e:
            print(f"Error in vector search: {e}")
            return []


# Inline embedding generator
class EmbeddingGenerator:
    """Generate embeddings using OpenAI or Cohere."""
    
    def __init__(self):
        self.config = Config()
    
    async def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text (async version)."""
        try:
            if self.config.EMBEDDING_PROVIDER == "openai" and self.config.OPENAI_API_KEY:
                import openai
                import asyncio
                
                # Use async client for OpenAI to avoid blocking calls
                client = openai.AsyncOpenAI(api_key=self.config.OPENAI_API_KEY)
                response = await client.embeddings.create(
                    model=self.config.EMBEDDING_MODEL,
                    input=text
                )
                return response.data[0].embedding
            elif self.config.EMBEDDING_PROVIDER == "cohere" and self.config.COHERE_API_KEY:
                import cohere
                import asyncio
                
                # Run cohere in thread to avoid blocking
                def _cohere_embed():
                    client = cohere.Client(self.config.COHERE_API_KEY)
                    response = client.embed(texts=[text], model="embed-english-v3.0")
                    return response.embeddings[0]
                
                return await asyncio.to_thread(_cohere_embed)
            else:
                # Fallback: return dummy embedding for testing
                return [0.1] * self.config.EMBEDDING_DIMENSIONS
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None


class Context(TypedDict, total=False):
    """Runtime context for the RAG pipeline."""
    
    top_k: int
    filters: Optional[Dict[str, Any]]
    include_citations: bool


@dataclass
class State:
    """State for the RAG pipeline."""
    
    # Input
    user_query: str = ""
    
    # Processing
    query_embedding: Optional[List[float]] = None
    retrieved_chunks: List[Dict[str, Any]] = field(default_factory=list)
    combined_context: str = ""
    
    # Output
    answer: str = ""
    citations: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class RAGPipeline:
    """RAG pipeline implementation."""
    
    def __init__(self):
        """Initialize the RAG pipeline components."""
        self.config = Config()
        self.db = Database()
        self.vector_store = VectorStore()
        self.embedding_generator = EmbeddingGenerator()
    
    async def embed_query(self, state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
        """Generate embedding for the user query."""
        try:
            if not state.user_query.strip():
                return {"query_embedding": None}
            
            # Generate embedding
            embedding = await self.embedding_generator.generate_embedding(state.user_query)
            
            return {"query_embedding": embedding}
            
        except Exception as e:
            print(f"Error in embed_query: {e}")
            return {"query_embedding": None}
    
    async def retrieve_chunks(self, state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
        """Retrieve relevant document chunks."""
        try:
            if not state.query_embedding:
                return {"retrieved_chunks": []}
            
            # Get context parameters
            ctx = runtime.context or {}
            top_k = ctx.get("top_k", self.config.TOP_K)
            filters = ctx.get("filters", {})
            
            # Search vector store
            results = self.vector_store.search(
                query_embedding=state.query_embedding,
                top_k=top_k,
                similarity_threshold=self.config.SIMILARITY_THRESHOLD,
                filters=filters
            )
            
            # Enrich with metadata from database (async)
            enriched_chunks = []
            for result in results:
                chunk_id = result.get("chunk_id")
                if chunk_id:
                    metadata = await self.db.get_chunk_metadata(chunk_id)
                    if metadata:
                        result.update(metadata)
                enriched_chunks.append(result)
            
            return {"retrieved_chunks": enriched_chunks}
            
        except Exception as e:
            print(f"Error in retrieve_chunks: {e}")
            return {"retrieved_chunks": []}
    
    async def combine_context(self, state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
        """Combine retrieved chunks into context."""
        try:
            if not state.retrieved_chunks:
                return {"combined_context": "No relevant documents found."}
            
            # Sort by relevance score
            sorted_chunks = sorted(
                state.retrieved_chunks,
                key=lambda x: x.get("score", 0),
                reverse=True
            )
            
            # Combine text content
            context_parts = []
            for i, chunk in enumerate(sorted_chunks, 1):
                text = chunk.get("text", "").strip()
                if text:
                    source = chunk.get("document_name", "Unknown")
                    context_parts.append(f"[{i}] From {source}:\n{text}")
            
            combined_context = "\n\n".join(context_parts)
            
            return {"combined_context": combined_context}
            
        except Exception as e:
            print(f"Error in combine_context: {e}")
            return {"combined_context": "Error processing context."}
    
    async def generate_answer(self, state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
        """Generate answer based on context (lightweight version)."""
        try:
            if not state.combined_context or state.combined_context == "No relevant documents found.":
                return {
                    "answer": "I couldn't find relevant information to answer your question.",
                    "citations": []
                }
            
            # Simple answer generation (no LLM required for MVP)
            query_lower = state.user_query.lower()
            context_lower = state.combined_context.lower()
            
            # Extract key information
            answer_parts = []
            
            # Look for direct matches or relevant sections
            lines = state.combined_context.split('\n')
            relevant_lines = []
            priority_lines = []  # Lines that contain exact query terms
            
            query_words = [word for word in query_lower.split() if len(word) > 3]
            
            for line in lines:
                line_lower = line.lower()
                if any(word in line_lower for word in query_words):
                    relevant_lines.append(line.strip())
                    # Prioritize lines that contain the specific query terms (exact match priority)
                    query_match_count = sum(1 for word in query_words if word in line_lower)
                    if query_match_count >= 2:  # Lines with multiple query words get highest priority
                        priority_lines.insert(0, line.strip())  # Insert at beginning
                    elif any(word in line_lower for word in query_words[:1]):  # First query word (company name)
                        priority_lines.append(line.strip())
            
            if priority_lines:
                # Use priority lines first, then fill with other relevant lines
                selected_lines = priority_lines[:3] + [line for line in relevant_lines if line not in priority_lines][:7]
                answer = "Based on the documents, here's what I found:\n\n" + "\n".join(selected_lines[:10])
            elif relevant_lines:
                answer = "Based on the documents, here's what I found:\n\n" + "\n".join(relevant_lines[:10])
            else:
                answer = f"I found {len(state.retrieved_chunks)} relevant documents, but couldn't extract specific information matching your query. Please review the source documents for details."
            
            # Generate citations
            citations = []
            for chunk in state.retrieved_chunks:
                if chunk.get("document_name"):
                    citations.append({
                        "source": chunk["document_name"],
                        "score": chunk.get("score", 0),
                        "chunk_id": chunk.get("chunk_id")
                    })
            
            return {
                "answer": answer,
                "citations": citations
            }
            
        except Exception as e:
            print(f"Error in generate_answer: {e}")
            return {
                "answer": "Error generating answer.",
                "citations": []
            }
    
    async def format_output(self, state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
        """Format the final output."""
        try:
            # Include citations in context if requested
            ctx = runtime.context or {}
            include_citations = ctx.get("include_citations", True)
            
            metadata = {
                "query": state.user_query,
                "chunks_retrieved": len(state.retrieved_chunks),
                "has_context": bool(state.combined_context and state.combined_context != "No relevant documents found.")
            }
            
            if include_citations and state.citations:
                metadata["sources"] = [c["source"] for c in state.citations]
            
            return {"metadata": metadata}
            
        except Exception as e:
            print(f"Error in format_output: {e}")
            return {"metadata": {"error": str(e)}}


# Build the graph
def build_rag_graph() -> StateGraph:
    """Build and compile the RAG graph."""
    pipeline = RAGPipeline()
    
    graph = (
        StateGraph(State, context_schema=Context)
        .add_node("embed_query", pipeline.embed_query)
        .add_node("retrieve_chunks", pipeline.retrieve_chunks)
        .add_node("combine_context", pipeline.combine_context)
        .add_node("generate_answer", pipeline.generate_answer)
        .add_node("format_output", pipeline.format_output)
        .add_edge("__start__", "embed_query")
        .add_edge("embed_query", "retrieve_chunks")
        .add_edge("retrieve_chunks", "combine_context")
        .add_edge("combine_context", "generate_answer")
        .add_edge("generate_answer", "format_output")
        .compile(name="Logistics RAG Pipeline")
    )
    
    return graph


# Create the graph instance
graph = build_rag_graph()
