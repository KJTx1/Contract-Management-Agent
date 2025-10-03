# 🚀 Scalability Fix Guide for 250+ Documents

## 🚨 **Problem Identified**

When customers ingest 250+ PDFs, only certain documents show up in query results due to several configuration bottlenecks in the current system design.

## ✅ **Root Causes & Fixes Applied**

### **1. TOP_K Limitation (CRITICAL)**
**Problem:** System only retrieves 5-20 chunks maximum per query
**Fix Applied:** 
- Increased `TOP_K` from 5/20 to **50**
- This allows retrieval of more diverse document chunks

### **2. Similarity Threshold Too High (CRITICAL)**
**Problem:** 30% similarity threshold filters out many relevant documents
**Fix Applied:**
- Lowered `SIMILARITY_THRESHOLD` from 0.3 to **0.1**
- This captures more relevant documents with lower similarity scores

### **3. FAISS Index Type Limitation (CRITICAL)**
**Problem:** `IndexFlatL2` is not scalable for 250+ documents
**Fix Applied:**
- Upgraded to `IndexIVFFlat` with 100 clusters
- Provides better performance and scalability

## 🔧 **Configuration Changes Made**

### **Files Updated:**

1. **`src/agent/config.py`**
   ```python
   TOP_K = int(os.getenv("TOP_K", "50"))  # Increased for 250+ documents
   SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.1"))  # Lowered for better recall
   ```

2. **`src/agent/standalone_graph.py`**
   ```python
   TOP_K = int(os.getenv("TOP_K", "50"))  # Increased for 250+ documents
   SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.1"))  # Lowered for better recall
   ```

3. **`config/env.example`**
   ```bash
   TOP_K=50
   SIMILARITY_THRESHOLD=0.1
   ```

4. **`src/agent/vector_operations.py`**
   - Upgraded to `IndexIVFFlat` for better scalability
   - Added proper training for IVF index

## 📊 **Expected Performance Improvements**

### **Before Fix:**
- ❌ Only 5-20 documents retrieved per query
- ❌ 30% similarity threshold too restrictive
- ❌ Slow performance with 250+ documents
- ❌ Many relevant documents filtered out

### **After Fix:**
- ✅ Up to 50 chunks retrieved per query
- ✅ 10% similarity threshold captures more documents
- ✅ Scalable FAISS index for large document sets
- ✅ Better document diversity in results

## 🚀 **Deployment Instructions**

### **For Existing Systems:**
1. **Update Configuration in .env file:**
   ```bash
   # Add to your .env file
   TOP_K=50
   SIMILARITY_THRESHOLD=0.1
   ```

2. **Rebuild FAISS Index (if needed):**
   ```bash
   # Remove old index to force recreation with new type
   rm data/faiss_index.index
   
   # Re-ingest documents to create new scalable index
   python -m agent.cli ingest --source /path/to/your/250/documents
   ```

3. **Test the System:**
   ```bash
   # Check system stats
   python -m agent.cli stats
   
   # Test with a query that should return diverse results
   python -m agent.cli query "Show me all contract types"
   ```

### **For New Deployments:**
1. Copy the updated configuration files
2. Create `.env` file with the new values:
   ```bash
   TOP_K=50
   SIMILARITY_THRESHOLD=0.1
   ```
3. Ingest your 250 documents
4. The system will automatically use the new scalable configuration

## 📈 **Monitoring & Validation**

### **Check System Health:**
```bash
# Verify document count
python -m agent.cli stats

# Test query diversity
python -m agent.cli query "List all customers"
python -m agent.cli query "Show me contracts from different countries"
python -m agent.cli query "Find all document types"
```

### **Expected Results:**
- Should see 50+ chunks retrieved per query
- More diverse document sources in results
- Better coverage of your 250 document corpus
- Improved relevance and recall

## ⚠️ **Important Notes**

1. **Performance Trade-off:** Lower similarity threshold may return more results but with lower precision
2. **Memory Usage:** Higher TOP_K increases memory usage during query processing
3. **Index Training:** IVF index requires training, which happens automatically on first use
4. **Backup:** Always backup your existing index before making changes

## 🔄 **Rollback Instructions**

If issues occur, you can rollback by:
```bash
# Restore original settings in .env file
TOP_K=5
SIMILARITY_THRESHOLD=0.3

# Restart the system
python -m agent.cli stats
```

## 📞 **Support**

If you encounter issues with the new configuration:
1. Check the system logs for errors
2. Verify all 250 documents are properly ingested
3. Test with simple queries first
4. Contact support with specific error messages

---

**This fix should resolve the issue where only certain documents show up when querying 250+ PDFs!** 🎯
