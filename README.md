# Contract Management Agent

[![LangGraph](https://img.shields.io/badge/LangGraph-0.2.6+-blue.svg)](https://github.com/langchain-ai/langgraph)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://python.org)
[![OpenAI](https://img.shields.io/badge/OpenAI-API-orange.svg)](https://openai.com)
[![FAISS](https://img.shields.io/badge/FAISS-Vector%20Search-red.svg)](https://github.com/facebookresearch/faiss)

An intelligent **Contract Management Agent** built with [LangGraph](https://github.com/langchain-ai/langgraph) that provides semantic search and question-answering capabilities over logistics contracts and business documents. The system uses Retrieval-Augmented Generation (RAG) to deliver accurate, source-attributed answers about contract details, customer information, and business relationships.

<div align="center">
  <img src="./static/studio_ui.png" alt="Contract Management Agent in LangGraph Studio" width="75%" />
</div>

## 🎯 **Key Features**

- **🔍 Semantic Search**: Vector-based document retrieval using FAISS and OpenAI embeddings
- **📄 Contract Intelligence**: Specialized for logistics contracts, customer data, and business documents
- **🎯 Smart Retrieval**: Context-aware chunk retrieval with similarity scoring
- **📊 Source Attribution**: Full citation tracking with document references
- **🚀 Async Operations**: Non-blocking operations optimized for LangGraph Studio
- **🎨 Visual Debugging**: Complete LangGraph Studio integration for workflow visualization
- **💾 Persistent Storage**: SQLite database for metadata and FAISS for vector search

## 🏗️ **Architecture**

The agent implements a 5-step RAG pipeline:

```
User Query → Embed Query → Retrieve Chunks → Combine Context → Generate Answer → Format Output
```

### **Core Components**

- **Vector Store**: FAISS index with 23 document vectors (1536 dimensions)
- **Database**: SQLite with contract metadata, customer info, and document details
- **Embeddings**: OpenAI `text-embedding-3-small` model
- **Processing**: Async-first design with `asyncio.to_thread()` for blocking operations

### **Document Types Supported**

- Logistics services contracts
- Customer agreements
- Business partnerships
- Service provider contracts
- Multi-language documents (English, Italian, German)

## 🚀 **Quick Start**

### **1. Installation**

```bash
# Clone and navigate to project
cd /path/to/contract-management-agent

# Install dependencies
pip install -e .

# Install LangGraph CLI for Studio
pip install 'langgraph-cli[inmem]'
```

### **2. Environment Setup**

```bash
# Copy environment template
cp .env.example .env

# Add your OpenAI API key to .env
echo "OPENAI_API_KEY=your-api-key-here" >> .env

# Optional: Add LangSmith for tracing
echo "LANGSMITH_API_KEY=your-langsmith-key" >> .env
```

### **3. Start LangGraph Studio**

```bash
# Start the development server
python -m langgraph_cli dev --port 8123 --host 127.0.0.1

# Access Studio UI at:
# https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:8123
```

### **4. Test the Agent**

Try these example queries in Studio:

- `"UrbanWear Group Ltd."`
- `"HealthFirst Pharmaceuticals contract details"`
- `"logistics services for fashion industry"`
- `"TechGear Solutions LLC agreement"`

## 📊 **Sample Data**

The system comes pre-loaded with sample logistics contracts including:

| Customer | Industry | Contract Type | Location |
|----------|----------|---------------|----------|
| UrbanWear Group Ltd. | Fashion | Logistics Services | London, UK |
| HealthFirst Pharmaceuticals Inc. | Healthcare | Distribution | Boston, USA |
| TechGear Solutions LLC | Technology | Transportation | Austin, USA |
| GreenTech Appliances GmbH | Electronics | Logistics | Berlin, Germany |
| Bright Manufacturing Inc. | Manufacturing | Supply Chain | Los Angeles, USA |

## 🔧 **Configuration**

Key configuration options in `.env`:

```bash
# Embedding Configuration
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSIONS=1536

# Retrieval Configuration
TOP_K=20
SIMILARITY_THRESHOLD=0.3

# Processing Configuration
CHUNK_SIZE=800
CHUNK_OVERLAP=100

# Database Paths
SQLITE_DB_PATH=./data/contracts.db
FAISS_INDEX_PATH=./data/faiss_index.bin
```

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

## 🛠️ **Development**

### **Adding New Documents**

```bash
# Place PDF files in data/docs/
cp your-contract.pdf data/docs/

# Run ingestion pipeline
python -m src.agent.cli ingest --source data/docs/your-contract.pdf

# Restart Studio to see changes
python -m langgraph_cli dev --port 8123
```

### **Command Line Interface**

```bash
# Query the system
python -m src.agent.cli query "your question here"

# View statistics
python -m src.agent.cli stats

# List all documents
python -m src.agent.cli list
```

### **Studio Development**

- **Hot Reload**: Changes to `standalone_graph.py` automatically reload
- **State Inspection**: View intermediate results at each pipeline step
- **Thread Management**: Create new conversations with the `+` button
- **Debugging**: Trace execution flow and inspect state transitions

## 🎯 **Use Cases**

- **Contract Analysis**: "What are the terms for UrbanWear's logistics contract?"
- **Customer Lookup**: "Find all contracts for healthcare companies"
- **Service Details**: "What logistics services are provided to fashion clients?"
- **Compliance Checking**: "Show me all contracts expiring in 2026"
- **Relationship Mapping**: "Which service providers work with German companies?"

## 🔍 **Technical Details**

### **RAG Pipeline Steps**

1. **Embed Query**: Convert user question to 1536-dim vector using OpenAI
2. **Retrieve Chunks**: FAISS similarity search with L2 distance normalization
3. **Combine Context**: Format retrieved chunks with source attribution
4. **Generate Answer**: Smart text extraction with query-aware prioritization
5. **Format Output**: Structure response with citations and metadata

### **Performance Optimizations**

- **Async Operations**: All I/O operations use `async/await`
- **Vector Normalization**: L2 normalization for improved similarity search
- **Smart Chunking**: 800-character chunks with 100-character overlap
- **Metadata Caching**: Efficient SQLite queries with connection pooling
- **Priority Ranking**: Query-aware content prioritization

## 🚀 **Deployment Options**

### **Local Development**
```bash
./start-studio.sh
```

### **Production Deployment**
```bash
./deploy-local.sh
```

### **Docker Deployment**
```bash
docker-compose up -d
```

## 📚 **Documentation**

- [Quick Start Guide](./QUICKSTART.md) - Get up and running in 5 minutes
- [Studio Guide](./STUDIO_GUIDE.md) - Complete LangGraph Studio walkthrough
- [Architecture Overview](./ARCHITECTURE.md) - Technical deep dive
- [API Reference](./API.md) - Complete API documentation

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- [LangGraph](https://github.com/langchain-ai/langgraph) - Workflow orchestration framework
- [OpenAI](https://openai.com) - Embedding and language models
- [FAISS](https://github.com/facebookresearch/faiss) - Efficient vector search
- [LangSmith](https://smith.langchain.com) - Tracing and monitoring

---

**Built with ❤️ using LangGraph for intelligent contract management**