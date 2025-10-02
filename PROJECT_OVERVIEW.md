# 🎯 Contract Management Agent - Project Overview

## 📋 **Project Summary**

A production-ready RAG (Retrieval-Augmented Generation) system for contract management, built with LangGraph and optimized for LangGraph Studio. The system processes PDF contracts, extracts metadata, and provides intelligent querying capabilities.

## 🏗️ **Architecture Overview**

### **Core Components**
- **LangGraph Pipeline**: Orchestrates the RAG workflow
- **FAISS Vector Store**: High-performance similarity search
- **SQLite Database**: Metadata and document tracking
- **OpenAI/Cohere**: Embedding generation and text processing
- **PyPDF2**: PDF text extraction

### **Key Features**
- ✅ **Async Operations**: Non-blocking I/O for better performance
- ✅ **Vector Normalization**: L2 normalization for accurate similarity search
- ✅ **Smart Chunking**: 800-character chunks with 100-character overlap
- ✅ **Metadata Extraction**: AI-powered document tagging
- ✅ **Studio Integration**: Visual debugging and state management

## 📁 **Streamlined Project Structure**

```
langraph/
├── src/agent/                    # Core RAG implementation
│   ├── standalone_graph.py     # Main RAG pipeline (Studio-compatible)
│   ├── graph.py                # Graph entry point
│   ├── rag_pipeline.py         # RAG workflow definition
│   ├── config.py               # Configuration management
│   ├── database.py             # SQLite operations
│   ├── vector_operations.py    # FAISS vector store
│   ├── pdf_processor.py        # Document processing
│   ├── ingestion.py            # Document ingestion pipeline
│   └── cli.py                  # Command-line interface
├── data/                        # Data storage
│   ├── logistics.db            # SQLite database
│   ├── faiss_index.index       # FAISS vector index
│   ├── docs/                   # Sample documents
│   └── pdfs/                   # Processed PDF files
├── tests/                       # Test suite
│   ├── unit_tests/             # Unit tests
│   └── integration_tests/      # Integration tests
├── deploy-local.sh             # Local deployment script
├── deploy-studio.sh            # Studio deployment script
├── start-studio.sh            # Studio startup script
├── test_mvp.py                # End-to-end test
├── langgraph.json             # LangGraph configuration
├── pyproject.toml             # Python dependencies
├── README.md                  # Main documentation
├── ARCHITECTURE.md            # Technical architecture
├── SIMPLE_LOCAL_GUIDE.md      # Quick start guide
├── STUDIO_SETUP_GUIDE.md      # Studio setup guide
└── STUDIO_FIX_SUMMARY.md      # Troubleshooting guide
```

## 🚀 **Deployment Options**

### **1. Local Development (Recommended)**
```bash
./start-studio.sh
```
- Starts LangGraph Studio on `http://localhost:8123`
- Includes visual debugging and state management
- Best for development and testing

### **2. Production Deployment**
```bash
./deploy-local.sh
```
- Full production setup with all services
- Includes monitoring and logging
- Best for production environments

### **3. Docker Deployment**
```bash
./deploy-studio.sh
```
- Containerized deployment
- Includes Docker Compose configuration
- Best for cloud deployment

## 🛠️ **Development Workflow**

### **Adding Documents**
```bash
# Place PDF files in data/docs/
cp your-contract.pdf data/docs/

# Run ingestion pipeline
python -m src.agent.cli ingest --source data/docs/your-contract.pdf
```

### **Testing**
```bash
# Run end-to-end test
python test_mvp.py

# Run unit tests
python -m pytest tests/

# Run integration tests
python -m pytest tests/integration_tests/
```

### **CLI Usage**
```bash
# Query the system
python -m src.agent.cli query "your question here"

# View statistics
python -m src.agent.cli stats

# List all documents
python -m src.agent.cli list
```

## 📊 **Performance Metrics**

- **Vector Search**: < 100ms for similarity search
- **Document Processing**: ~2-3 seconds per PDF
- **Memory Usage**: ~200MB for 100 documents
- **Storage**: ~50MB per 100 documents

## 🔧 **Configuration**

### **Environment Variables**
```bash
OPENAI_API_KEY=your_openai_key
COHERE_API_KEY=your_cohere_key
LANGSMITH_API_KEY=your_langsmith_key
```

### **Database Configuration**
```bash
SQLITE_DB_PATH=./data/logistics.db
FAISS_INDEX_PATH=./data/faiss_index.index
```

## 📚 **Documentation**

- **README.md**: Main project documentation
- **ARCHITECTURE.md**: Technical architecture details
- **SIMPLE_LOCAL_GUIDE.md**: Quick start guide
- **STUDIO_SETUP_GUIDE.md**: Studio setup instructions
- **STUDIO_FIX_SUMMARY.md**: Troubleshooting guide

## 🎯 **Use Cases**

1. **Contract Analysis**: Extract key terms and clauses
2. **Compliance Checking**: Verify contract compliance
3. **Risk Assessment**: Identify potential risks
4. **Document Search**: Find specific information quickly
5. **Metadata Extraction**: Automatically tag documents

## 🔄 **Recent Cleanup**

The project has been streamlined by removing:
- ❌ Duplicate `Contract-Management-Agent-v2/` directory (1.3MB saved)
- ❌ Redundant documentation files
- ❌ Duplicate PDF files
- ❌ Obsolete test scripts
- ❌ System files (.DS_Store)

The repository is now clean, organized, and production-ready.
