# 🤖 Contract Management Agent

> **AI-Powered Document Intelligence for Logistics Contracts**

A sophisticated RAG (Retrieval-Augmented Generation) system built with LangGraph that transforms contract management through intelligent document processing, semantic search, and AI-powered insights.

## ✨ **Key Features**

- 🔍 **Semantic Search**: Find relevant information using meaning, not just keywords
- 📄 **Document Intelligence**: Extract metadata, customer info, and key terms automatically  
- 🧠 **AI-Powered Answers**: Get intelligent responses with proper citations
- 🎨 **LangGraph Studio**: Visual workflow design and debugging interface
- ⚡ **High Performance**: Async operations optimized for production
- 🌊 **Streaming Processing**: Process PDFs directly from OCI Object Storage (no local storage)
- 🔧 **Self-Hosted**: Complete control over your data and infrastructure

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.11+
- OpenAI API key
- Git

### **Installation**
```bash
# Clone the repository
git clone <repository-url>
cd langraph

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .

# Set up environment
cp .env.example .env
# Edit .env with your API keys
```

### **Start LangGraph Studio**
```bash
# Quick start
./scripts/start-studio.sh

# Or manually
source .venv/bin/activate
python -m langgraph_cli dev --port 8123
```

Visit `http://localhost:8123` to access the Studio interface.

## 📁 **Project Structure**

```
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
├── data/                        # Local metadata storage (SQLite + FAISS)
│   ├── logistics.db            # SQLite database
│   ├── faiss_index.index       # FAISS vector index
│   └── pdfs/                   # Sample PDF files (dev only - production uses OCI streaming)
├── scripts/                     # Deployment and utility scripts
│   ├── start-studio.sh        # Studio startup script
│   ├── deploy-local.sh        # Local deployment
│   └── deploy-studio.sh       # Studio deployment
├── docs/                        # Documentation
│   ├── README.md              # This file
│   ├── ARCHITECTURE.md        # Technical architecture
│   └── STUDIO_SETUP_GUIDE.md  # Studio setup guide
├── docker/                      # Docker configurations
│   ├── Dockerfile             # Main application
│   ├── Dockerfile.studio      # Studio-specific
│   └── docker-compose.yml     # Multi-container setup
├── config/                      # Configuration files
│   └── langgraph.json         # LangGraph configuration
├── tests/                       # Test suite
│   ├── unit_tests/             # Unit tests
│   ├── integration_tests/      # Integration tests
│   └── test_system_integration.py # End-to-end system test
└── pyproject.toml              # Python dependencies
```

## 🔧 **Configuration**

### **Environment Variables**
Create a `.env` file with:
```bash
# API Keys
OPENAI_API_KEY=your_openai_api_key_here
COHERE_API_KEY=your_cohere_api_key_here  # Optional

# LangSmith (Optional)
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_PROJECT=contract-management-agent

# OCI Configuration (Required for Object Storage)
OCI_CONFIG_FILE=~/.oci/config
OCI_PROFILE=DEFAULT
OCI_BUCKET_NAME=contract-documents

# Embedding Configuration
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSIONS=1536

# LLM Configuration
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini

# Retrieval Configuration
TOP_K=20
SIMILARITY_THRESHOLD=0.3
```

**Copy the example configuration:**
```bash
cp config/env.example .env
# Edit .env with your actual API keys and OCI configuration
```

### **OCI Setup**
1. **Install OCI CLI**: `pip install oci`
2. **Configure OCI**: Set up `~/.oci/config` file or environment variables
3. **Create Bucket**: Create an OCI Object Storage bucket
4. **Set Environment**: Configure `OCI_BUCKET_NAME` in your `.env` file

**OCI Configuration Options:**
- **Config File**: `~/.oci/config` (recommended)
- **Environment Variables**: Set OCI_* variables directly
- **Instance Principal**: For OCI compute instances

## 📊 **Sample Data**

The system comes with 5 sample logistics contracts:
- **UrbanWear Group Ltd.** - Fashion logistics contract
- **HealthFirst Pharmaceuticals Inc.** - Pharmaceutical logistics
- **Bright Manufacturing Inc.** - Manufacturing logistics
- **TechFlow Solutions** - Technology logistics
- **Global Logistics Solutions** - General logistics services

## 🎯 **Usage**

### **Adding New Documents**
```bash
# Place PDF files anywhere and ingest them
cp your-contract.pdf ./your-contract.pdf

# Run ingestion pipeline
python -m src.agent.cli ingest --source your-contract.pdf

# Restart Studio to see changes
./scripts/start-studio.sh
```

### **Querying Documents**
```bash
# Command line interface
python -m src.agent.cli query "Tell me about UrbanWear Group Ltd."

# Or use Studio interface at http://localhost:8123
```

### **System Statistics**
```bash
# Check system status
python -m src.agent.cli stats
```

## 🏗️ **Production Architecture (OCI)**

### **Cloud Storage**
- **OCI Object Storage**: Primary document storage (✅ Implemented)
- **OCI Vector Database**: Production vector store (Future enhancement)
- **OCI Database**: Metadata and document tracking (Future enhancement)

### **Current Implementation**
- **Document Storage**: OCI Object Storage with local fallback
- **Vector Store**: FAISS (local) with OCI streaming for documents
- **Database**: SQLite (local) with OCI URLs for document references

### **OCI Setup Requirements**
1. **OCI Account**: Oracle Cloud Infrastructure account
2. **Object Storage Bucket**: Create a bucket for document storage
3. **API Keys**: Generate OCI API keys and configure authentication
4. **Configuration**: Set up OCI config file or environment variables

### **Development vs Production**
- **Development**: Local `data/` directory with SQLite + FAISS + OCI streaming
- **Production**: OCI object storage + FAISS + SQLite (hybrid approach)

## 🧪 **Testing**

```bash
# Run all unit and integration tests
python -m pytest tests/ -v

# Run specific test suite
python -m pytest tests/unit_tests/
python -m pytest tests/integration_tests/

# Run system integration test (end-to-end validation)
python tests/test_system_integration.py

# Or use quick-start script
./quick-start.sh test        # Unit/integration tests
./quick-start.sh system      # System integration test
```

## 🚀 **Deployment Options**

### **Local Development**
```bash
./scripts/start-studio.sh
```

### **Docker Deployment**
```bash
# Build and run with Docker Compose
cd docker/
docker-compose up -d
```

### **Production Deployment**
```bash
# Deploy to production environment
./scripts/deploy.sh
```

## 🔍 **Technical Deep Dive**

### **RAG Pipeline**
1. **Document Ingestion**: PDF → Text → Chunks → Embeddings
2. **Vector Storage**: FAISS index for fast similarity search
3. **Metadata Storage**: SQLite for document relationships
4. **Query Processing**: Embedding → Search → Context → LLM
5. **Response Generation**: AI-powered answers with citations

### **Key Technologies**
- **LangGraph**: Workflow orchestration
- **OpenAI**: Embeddings and LLM generation
- **FAISS**: Vector similarity search
- **SQLite**: Metadata and document tracking
- **PyPDF2**: PDF text extraction

## 📈 **Performance**

- **Embedding Generation**: ~2-3 seconds per document
- **Vector Search**: <100ms for similarity queries
- **LLM Response**: ~3-5 seconds for complex queries
- **Studio Interface**: Real-time workflow visualization

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 **Support**

- **Documentation**: Check the `docs/` directory
- **Issues**: Create a GitHub issue
- **Discussions**: Use GitHub Discussions for questions

---

**Built with ❤️ using LangGraph, OpenAI, and modern AI technologies**