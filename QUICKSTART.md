# Logistics Document RAG Assistant - Quick Start Guide

## 🚀 Setup

### 1. Set Environment Variables

Create a `.env` file in the project root:

```bash
# OpenAI API Key (required)
OPENAI_API_KEY=your-openai-api-key-here

# Optional: Use Cohere instead
# EMBEDDING_PROVIDER=cohere
# COHERE_API_KEY=your-cohere-api-key

# Optional: Customize models
# EMBEDDING_MODEL=text-embedding-3-small
# LLM_MODEL=gpt-4o-mini

# Optional: Tune retrieval
# TOP_K=5
# CHUNK_SIZE=800
# CHUNK_OVERLAP=100
```

### 2. Install Dependencies

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -e .
```

## 📥 Ingest Documents

### Ingest from Directory

```bash
python -m agent.cli ingest ./docs
```

### Ingest Single PDF

```bash
python -m agent.cli ingest ./docs/sample-contract.txt
```

### Ingest Without LLM Metadata (faster, basic extraction)

```bash
python -m agent.cli ingest ./docs --no-llm
```

## 🔍 Query Documents

### Simple Query

```bash
python -m agent.cli query "What are the payment terms for UrbanWear?"
```

### Interactive Mode

```bash
python -m agent.cli interactive
```

Then type questions interactively:
```
❓ Your question: Find all invoices for UrbanWear from March 2024
❓ Your question: What is the termination notice period?
❓ Your question: quit
```

## 📊 View Statistics

```bash
# Show database stats
python -m agent.cli stats

# List all documents
python -m agent.cli list
```

## 🎯 Example Queries

Based on your PRD use cases:

```bash
# Find specific customer invoices
python -m agent.cli query "Retrieve UrbanWear invoices from March 2024"

# Search by location
python -m agent.cli query "Identify shipments to Rotterdam missing customs clearance"

# Find by container ID
python -m agent.cli query "Locate the bill of lading for container ID XYZ123"

# Check for delays
python -m agent.cli query "List all shipments delayed at the Port of Singapore"
```

## 🏗️ System Architecture

```
PDF Upload → Text Extraction → Chunking → Embedding Generation
     ↓            ↓               ↓              ↓
  Storage    Metadata DB      SQLite        FAISS Index
                                                 ↓
Query → Query Embedding → FAISS Search → Context Building → LLM → Answer + Citations
```

## 📁 Data Storage

All data is stored in `./data/`:
- `logistics.db` - SQLite database with metadata and chunks
- `faiss_index.index` - FAISS vector index
- `pdfs/` - Stored PDF files

## 🧪 Test the System

1. Ingest the sample contract:
```bash
python -m agent.cli ingest ./docs/sample-contract.txt
```

2. Query it:
```bash
python -m agent.cli query "What are the payment terms?"
```

3. Check stats:
```bash
python -m agent.cli stats
```

## 🔧 Troubleshooting

### No API Key Error
```bash
export OPENAI_API_KEY=your-key-here
```

### No Documents Found
Make sure you've ingested documents first:
```bash
python -m agent.cli ingest ./docs
```

### Empty Results
- Check if documents were ingested successfully: `python -m agent.cli list`
- Try broader search terms
- Check similarity threshold in config.py

## 📈 Performance Tips

- **Batch Ingestion**: Ingest multiple PDFs at once from a directory
- **LLM Metadata**: Use `--no-llm` flag for faster ingestion if you don't need detailed metadata
- **Chunk Size**: Adjust `CHUNK_SIZE` in environment for your documents
- **Top K**: Increase `TOP_K` for more comprehensive results

## 🎓 Next Steps

1. Ingest your logistics documents
2. Try the example queries from your PRD
3. Use interactive mode for exploration
4. Customize metadata extraction for your document types
5. Migrate to OCI 23ai when ready for production scale

## 📞 Common Commands Reference

```bash
# Ingestion
python -m agent.cli ingest <path>           # Ingest PDF(s)
python -m agent.cli ingest <path> --no-llm  # Fast ingestion

# Querying
python -m agent.cli query "<question>"      # Single query
python -m agent.cli interactive             # Interactive mode

# Management
python -m agent.cli stats                   # Show statistics
python -m agent.cli list                    # List documents
```

Happy querying! 🎉

