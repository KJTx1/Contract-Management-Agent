# 🚀 Get Started in 5 Minutes

## Step 1: Set Your API Key

```bash
export OPENAI_API_KEY=your-openai-api-key-here
```

Or create a `.env` file:
```bash
echo "OPENAI_API_KEY=your-key-here" > .env
```

## Step 2: Test the System

```bash
source .venv/bin/activate
python test_mvp.py
```

You should see:
```
🎉 All systems operational! Ready to ingest documents.
```

## Step 3: Ingest Documents

```bash
# Ingest all PDFs from the docs folder
python -m agent.cli ingest ./docs
```

## Step 4: Query Your Documents

```bash
# Ask a question
python -m agent.cli query "What are the payment terms?"
```

Or use interactive mode:
```bash
python -m agent.cli interactive
```

## 🎯 Example Workflow

```bash
# 1. Check system status
python -m agent.cli stats

# 2. Ingest documents
python -m agent.cli ingest ./docs

# 3. List ingested documents
python -m agent.cli list

# 4. Query with natural language
python -m agent.cli query "Find invoices for UrbanWear from March 2024"

# 5. Interactive exploration
python -m agent.cli interactive
```

## 📖 Full Documentation

- `QUICKSTART.md` - Detailed setup and usage guide
- `MVP_SUMMARY.md` - Complete implementation overview
- `prd.txt` - Original product requirements

## ⚡ Quick Commands

```bash
# Ingestion
python -m agent.cli ingest <path>                    # Ingest PDFs
python -m agent.cli ingest <path> --no-llm           # Fast mode

# Querying  
python -m agent.cli query "<question>"               # Single query
python -m agent.cli interactive                      # Interactive mode

# Management
python -m agent.cli stats                            # Show statistics
python -m agent.cli list                             # List documents
```

## 🎨 Example Queries

Try these with your logistics documents:

```bash
# Customer-specific
python -m agent.cli query "Find all documents for UrbanWear Group Ltd"

# Date-based
python -m agent.cli query "Show invoices from March 2024"

# Location-based
python -m agent.cli query "List shipments to Rotterdam"

# Document type
python -m agent.cli query "Find bills of lading"

# Specific details
python -m agent.cli query "What is the termination notice period?"
python -m agent.cli query "What are the payment terms?"
python -m agent.cli query "When does the contract expire?"
```

## 🔧 Troubleshooting

### Issue: "No API key found"
**Solution**: Set `OPENAI_API_KEY` environment variable

### Issue: "No documents found"
**Solution**: Ingest documents first with `python -m agent.cli ingest ./docs`

### Issue: "No results for query"
**Solution**: 
- Check if documents were ingested: `python -m agent.cli list`
- Try broader search terms
- Check your documents contain the information you're looking for

## 💡 Tips

1. **Start Small**: Ingest 5-10 documents first to test
2. **Use Interactive Mode**: Best for exploring your document corpus
3. **Check Stats**: Use `stats` and `list` commands to verify ingestion
4. **LLM Metadata**: First ingestion uses LLM for metadata (slower but better)
5. **Fast Mode**: Use `--no-llm` for quick testing

## 🎓 What Happens Behind the Scenes

1. **Ingestion**:
   - PDF → Text extraction
   - Text → Chunks (800 tokens with overlap)
   - Chunks → Embeddings (OpenAI)
   - Store in FAISS + SQLite

2. **Query**:
   - Question → Query embedding
   - Search FAISS for similar chunks
   - Filter by metadata (if specified)
   - Combine context + LLM generation
   - Return answer with citations

## 📊 System Components

- **Database**: `data/logistics.db` (SQLite)
- **Vectors**: `data/faiss_index.index` (FAISS)
- **PDFs**: `data/pdfs/` (Original files)

## 🎯 Success!

If you can run these commands successfully, you're ready to go:

```bash
✅ python test_mvp.py              # All tests pass
✅ python -m agent.cli ingest ./docs  # Documents ingested
✅ python -m agent.cli query "test"   # Query works
```

Happy querying! 🎉

---

**Need help?** Check:
- `QUICKSTART.md` for detailed instructions
- `MVP_SUMMARY.md` for architecture details
- Source code has extensive docstrings

