# System Architecture

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     INGESTION PIPELINE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  OCI Object Storage PDF                                         │
│       │                                                         │
│       ├──> Stream PDF bytes to memory                          │
│       │         │                                               │
│       │         ├──> Text Extraction (PyPDF2 from bytes)       │
│       │         │         │                                     │
│       │         │         ├──> Chunking (800 tokens, 100 overlap) │
│       │         │         │         │                           │
│       │         │         │         ├──> Embedding Generation  │
│       │         │         │         │    (OpenAI/Cohere)         │
│       │         │         │         │         │                 │
│       │         │         │         │         └──> FAISS Index  │
│       │         │         │         │                           │
│       │         │         │         └──> SQLite (chunks table)  │
│       │         │         │                                     │
│       │         │         └──> AI Metadata Extraction (LLM)   │
│       │         │                  │                           │
│       │         │                  └──> SQLite (documents table) │
│       │         │                                               │
│       │         └──> Store OCI URL (no local storage)          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    QUERY PIPELINE (LangGraph)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  User Query                                                     │
│       │                                                         │
│       ├──> [Node 1] Embed Query                                │
│       │         │                                               │
│       │         └──> Query Embedding                            │
│       │                                                         │
│       ├──> [Node 2] Retrieve Chunks                            │
│       │         │                                               │
│       │         ├──> FAISS Similarity Search                    │
│       │         │         │                                     │
│       │         └──> Apply Metadata Filters (SQLite)            │
│       │                   │                                     │
│       │                   └──> Top-K Relevant Chunks            │
│       │                                                         │
│       ├──> [Node 3] Combine Context                            │
│       │         │                                               │
│       │         └──> Build Prompt with Chunks                   │
│       │                                                         │
│       ├──> [Node 4] Generate Answer                            │
│       │         │                                               │
│       │         └──> LLM (GPT-4o-mini)                         │
│       │                   │                                     │
│       │                   └──> Generated Answer                 │
│       │                                                         │
│       └──> [Node 5] Format Output                              │
│                 │                                               │
│                 └──> Answer + Citations + Sources               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 📦 Component Details

### Storage Layer

```
data/
├── logistics.db              # SQLite Database
│   ├── documents table       # Document metadata
│   │   ├── doc_id (PK)
│   │   ├── filename
│   │   ├── customer_name
│   │   ├── doc_type
│   │   ├── doc_date
│   │   ├── shipment_id
│   │   └── ... (15+ fields)
│   │
│   └── chunks table          # Text chunks
│       ├── chunk_id (PK)
│       ├── doc_id (FK)
│       ├── chunk_text
│       ├── chunk_embedding_id
│       └── ... (metadata)
│
├── faiss_index.index         # FAISS Vector Index
│   └── 1536-dimensional embeddings
│
└── pdfs/                     # Original PDFs
    └── {uuid}_{filename}.pdf
```

### Code Structure

```
src/agent/
├── config.py                 # Configuration management
│   └── Config class
│
├── database.py               # SQLite operations
│   └── Database class
│       ├── insert_document()
│       ├── insert_chunk()
│       ├── search_chunks()
│       └── get_stats()
│
├── pdf_processor.py          # PDF processing
│   └── PDFProcessor class
│       ├── extract_text_from_pdf()
│       ├── chunk_text()
│       └── extract_metadata_with_llm()
│
├── vector_operations.py      # FAISS & embeddings
│   ├── VectorStore class
│   │   ├── add_vectors()
│   │   └── search()
│   └── EmbeddingGenerator class
│       └── generate_embeddings()
│
├── ingestion.py              # Ingestion pipeline
│   └── DocumentIngestionPipeline class
│       ├── ingest_document()
│       └── ingest_directory()
│
├── rag_pipeline.py           # LangGraph RAG
│   ├── RAGPipeline class
│   │   ├── embed_query()
│   │   ├── retrieve_chunks()
│   │   ├── combine_context()
│   │   ├── generate_answer()
│   │   └── format_output()
│   └── graph (compiled LangGraph)
│
├── cli.py                    # Command-line interface
│   └── CLI class
│       ├── ingest_command()
│       ├── query_command()
│       └── interactive_mode()
│
└── graph.py                  # Main export
    └── graph
```

## 🔄 Data Flow

### Ingestion Flow

```
1. OCI Object Storage PDF
   ↓
2. Stream PDF bytes to memory
   ↓
3. Extract Text (PyPDF2 from bytes)
   ↓
4. Split into Chunks
   ├─> Store in SQLite (chunks table)
   └─> Generate Embeddings
       ↓
5. Add to FAISS Index
   ↓
6. Extract Metadata (LLM)
   ↓
7. Store in SQLite (documents table)
   ↓
8. Store OCI URL (no local copy)
```

### Query Flow

```
1. User Question
   ↓
2. Generate Query Embedding
   ↓
3. Search FAISS (semantic similarity)
   ↓
4. Get Chunk IDs
   ↓
5. Fetch from SQLite (with metadata)
   ↓
6. Apply Filters (customer, date, type)
   ↓
7. Build Context Prompt
   ↓
8. Send to LLM
   ↓
9. Generate Answer
   ↓
10. Format with Citations
    ↓
11. Return to User
```

## 🎯 Key Design Decisions

### 1. SQLite for Metadata
- **Why**: Fast, embedded, SQL queries for filtering
- **Alternative**: NoSQL (MongoDB) - overkill for MVP
- **Migration Path**: PostgreSQL or OCI 23ai

### 2. FAISS for Vectors
- **Why**: Fast, mature, easy to use
- **Alternative**: Pinecone, Weaviate - require external services
- **Migration Path**: OCI 23ai vector capabilities

### 3. LangGraph for Orchestration
- **Why**: Modular, testable, cloud-ready
- **Alternative**: Simple functions - harder to maintain
- **Benefits**: Easy to add nodes, visualize, debug

### 4. PyPDF2 for Extraction
- **Why**: Lightweight, no dependencies
- **Alternative**: pdfplumber, Unstructured.io
- **Limitation**: Text-based PDFs only (no OCR)

### 5. OpenAI for Embeddings & LLM
- **Why**: Best quality, widely available
- **Alternative**: Cohere (supported), local models
- **Cost**: ~$0.01-0.05 per document

## 🔌 Integration Points

### Current (MVP)
```
┌─────────┐     ┌─────────┐     ┌──────┐
│ OpenAI  │────▶│  Agent  │────▶│ CLI  │
└─────────┘     └─────────┘     └──────┘
                     │
                     ├───▶ SQLite
                     ├───▶ FAISS
                     └───▶ OCI Object Storage
```

### Future (Production)
```
┌─────────┐     ┌─────────┐     ┌──────────┐
│ OpenAI  │────▶│  Agent  │────▶│ FastAPI  │
└─────────┘     └─────────┘     └──────────┘
                     │                │
                     ├───▶ OCI 23ai   │
                     ├───▶ OCI Object │
                     └───▶ Storage    │
                                      │
                                ┌─────▼─────┐
                                │  Web UI   │
                                └───────────┘
```

## 📊 Scalability Considerations

### Current Limits
- **Documents**: 100-500 PDFs (FAISS L2 index)
- **Concurrent Users**: 1-10 (single process)
- **Query Latency**: 1-3 seconds
- **Storage**: OCI Object Storage (unlimited)

### Scaling Up
- **More Documents**: FAISS IVF index or migrate to OCI 23ai
- **More Users**: Deploy as FastAPI service with workers
- **Faster Queries**: Batch embedding generation, caching
- **More Storage**: OCI Object Storage

## 🛡️ Security & Privacy

### Current
- **Data**: OCI Object Storage (cloud)
- **API Keys**: Environment variables
- **Access**: OCI IAM permissions
- **Network**: HTTPS/TLS encrypted

### Production Recommendations
- **Authentication**: JWT tokens
- **Authorization**: Role-based access
- **Encryption**: TLS for API, encrypted storage
- **Audit**: Log all queries and access

## 🔧 Configuration Options

```python
# Embedding
EMBEDDING_PROVIDER = "openai" | "cohere"
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSION = 1536

# Chunking
CHUNK_SIZE = 800          # tokens
CHUNK_OVERLAP = 100       # tokens

# Retrieval
TOP_K = 5                 # results
SIMILARITY_THRESHOLD = 0.7

# LLM
LLM_MODEL = "gpt-4o-mini"
```

## 📈 Performance Metrics

### Ingestion
- **Text Extraction**: ~1-2s per PDF
- **Chunking**: <0.1s per document
- **Embedding**: ~0.5-1s per document
- **LLM Metadata**: ~2-3s per document
- **Total**: ~3-6s per document

### Query
- **Embedding**: ~0.2-0.5s
- **FAISS Search**: <0.1s
- **DB Lookup**: <0.1s
- **LLM Generation**: ~1-2s
- **Total**: ~1.5-3s per query

## 🎓 Extension Points

### Add New Document Types
1. Extend `PDFProcessor` for new formats
2. Update metadata schema in `database.py`
3. Add type-specific extraction logic

### Add New Retrieval Methods
1. Implement in `RAGPipeline`
2. Add as new LangGraph node
3. Combine with existing retrieval

### Add New Interfaces
1. FastAPI: Create REST endpoints
2. Streamlit: Build web UI
3. Slack Bot: Integrate messaging

This architecture provides a solid foundation for the MVP while maintaining clear paths for production scaling! 🚀

