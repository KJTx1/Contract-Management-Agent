"""LangGraph RAG pipeline for document retrieval and question answering."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TypedDict
from langgraph.graph import StateGraph
from langgraph.runtime import Runtime

from .config import Config
from .database import Database
from .vector_operations import VectorStore, EmbeddingGenerator


class Context(TypedDict, total=False):
    """Runtime context for the RAG pipeline."""
    
    top_k: int
    filters: Optional[Dict[str, Any]]
    include_citations: bool


@dataclass
class State:
    """State for the RAG pipeline."""
    
    user_query: str = ""
    query_embedding: List[float] = field(default_factory=list)
    retrieved_chunks: List[Dict[str, Any]] = field(default_factory=list)
    context_prompt: str = ""
    response: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class RAGPipeline:
    """RAG pipeline using LangGraph."""
    
    def __init__(self):
        self.db = Database()
        self.vector_store = VectorStore()
        self.embedding_gen = EmbeddingGenerator()
    
    # Node 1: Generate Query Embedding
    async def embed_query(self, state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
        """Generate embedding for user query."""
        print(f"🔍 Query: {state.user_query}")
        
        query_embedding = self.embedding_gen.generate_query_embedding(state.user_query)
        
        return {"query_embedding": query_embedding.tolist()}
    
    # Node 2: Retrieve Relevant Chunks
    async def retrieve_chunks(self, state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
        """Retrieve relevant chunks using FAISS and apply metadata filters."""
        ctx = runtime.context or {}
        top_k = ctx.get("top_k", Config.TOP_K)
        filters = ctx.get("filters", {})
        
        # Search FAISS for similar vectors
        import numpy as np
        query_embedding = np.array(state.query_embedding, dtype=np.float32)
        
        distances, indices = self.vector_store.search(query_embedding, k=top_k * 2)  # Get more for filtering
        
        # Get chunk data from database
        # Note: FAISS indices correspond to chunk_embedding_id in database
        retrieved_chunks = []
        
        for distance, idx in zip(distances, indices):
            if idx == -1:  # FAISS returns -1 for invalid results
                continue
            
            # Find chunk by embedding_id
            chunks = self.db.search_chunks({"chunk_embedding_id": int(idx)}, limit=1)
            
            if not chunks:
                continue
            
            chunk = chunks[0]
            
            # Apply metadata filters
            if filters:
                match = True
                for key, value in filters.items():
                    if chunk.get(key) != value:
                        match = False
                        break
                
                if not match:
                    continue
            
            # Calculate similarity score (convert L2 distance to similarity)
            similarity = 1 / (1 + float(distance))
            
            if similarity < Config.SIMILARITY_THRESHOLD:
                continue
            
            chunk["similarity_score"] = similarity
            retrieved_chunks.append(chunk)
            
            if len(retrieved_chunks) >= top_k:
                break
        
        print(f"  └─ Retrieved {len(retrieved_chunks)} relevant chunks")
        
        return {"retrieved_chunks": retrieved_chunks}
    
    # Node 3: Combine Context
    async def combine_context(self, state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
        """Build prompt with query + retrieved context."""
        if not state.retrieved_chunks:
            context_prompt = f"""Question: {state.user_query}

No relevant documents found in the database. Please try rephrasing your query or check if documents have been ingested."""
            return {"context_prompt": context_prompt}
        
        # Build context from chunks
        context_parts = []
        seen_docs = set()
        
        for i, chunk in enumerate(state.retrieved_chunks, 1):
            doc_id = chunk.get("doc_id", "unknown")
            doc_type = chunk.get("doc_type", "document")
            customer = chunk.get("customer_name", "N/A")
            date = chunk.get("doc_date", "N/A")
            pdf_url = chunk.get("pdf_url", "")
            chunk_text = chunk.get("chunk_text", "")
            similarity = chunk.get("similarity_score", 0)
            
            # Track unique documents
            seen_docs.add(doc_id)
            
            context_parts.append(
                f"[Source {i}] (Relevance: {similarity:.2%})\n"
                f"Document Type: {doc_type}\n"
                f"Customer: {customer}\n"
                f"Date: {date}\n"
                f"Content: {chunk_text}\n"
                f"PDF: {pdf_url}"
            )
        
        context = "\n\n".join(context_parts)
        
        context_prompt = f"""You are a logistics document assistant. Answer the question using ONLY the provided document excerpts. Always cite your sources.

Question: {state.user_query}

Relevant Document Excerpts:
{context}

Instructions:
1. Answer the question clearly and concisely
2. Cite specific sources (e.g., "According to Source 1...")
3. If the documents don't contain enough information, say so
4. Include relevant details like customer names, dates, and document types
5. Provide the PDF links for reference

Answer:"""
        
        metadata = {
            "num_sources": len(state.retrieved_chunks),
            "unique_documents": len(seen_docs)
        }
        
        return {
            "context_prompt": context_prompt,
            "metadata": metadata
        }
    
    # Node 4: Generate Answer
    async def generate_answer(self, state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
        """Generate answer using LLM."""
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=Config.OPENAI_API_KEY)
            
            response = client.chat.completions.create(
                model=Config.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful logistics document assistant. Always cite your sources and provide accurate information based on the documents provided."},
                    {"role": "user", "content": state.context_prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            answer = response.choices[0].message.content
            
            return {"response": answer}
            
        except Exception as e:
            return {"response": f"Error generating answer: {str(e)}"}
    
    # Node 5: Format Output
    async def format_output(self, state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
        """Format the final output with citations."""
        ctx = runtime.context or {}
        include_citations = ctx.get("include_citations", True)
        
        output_parts = [
            "=" * 80,
            "ANSWER",
            "=" * 80,
            "",
            state.response,
            ""
        ]
        
        if include_citations and state.retrieved_chunks:
            output_parts.extend([
                "=" * 80,
                "SOURCES",
                "=" * 80,
                ""
            ])
            
            for i, chunk in enumerate(state.retrieved_chunks, 1):
                customer = chunk.get("customer_name", "N/A")
                doc_type = chunk.get("doc_type", "document")
                date = chunk.get("doc_date", "N/A")
                pdf_url = chunk.get("pdf_url", "")
                similarity = chunk.get("similarity_score", 0)
                
                output_parts.extend([
                    f"[Source {i}] (Relevance: {similarity:.2%})",
                    f"  Customer: {customer}",
                    f"  Type: {doc_type}",
                    f"  Date: {date}",
                    f"  PDF: {pdf_url}",
                    ""
                ])
        
        # Add metadata
        if state.metadata:
            output_parts.extend([
                "=" * 80,
                "METADATA",
                "=" * 80,
                f"Sources used: {state.metadata.get('num_sources', 0)}",
                f"Unique documents: {state.metadata.get('unique_documents', 0)}",
                ""
            ])
        
        formatted_output = "\n".join(output_parts)
        
        return {"response": formatted_output}


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


# Export the compiled graph
graph = build_rag_graph()

