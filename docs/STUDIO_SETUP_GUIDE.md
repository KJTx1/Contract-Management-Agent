# 🎨 LangGraph Studio Setup Guide

**Complete setup for LangGraph Studio across all deployment types**

## 🚀 **Quick Setup (All Deployments)**

### **Step 1: Get LangSmith API Key**
1. Go to https://smith.langchain.com/
2. Sign up/login
3. Get your API key from Settings

### **Step 2: Configure Environment**
```bash
# Add to your .env file
LANGSMITH_API_KEY=your-langsmith-key-here
LANGSMITH_PROJECT=logistics-rag
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
```

### **Step 3: Choose Your Deployment**

## 🏠 **Local Development (Recommended for Testing)**

### **Option A: Using our script**
```bash
./start-studio.sh
```

### **Option B: Manual startup**
```bash
source .venv/bin/activate
export $(cat .env | grep -v '^#' | xargs)
python -m langgraph_cli dev --port 8123 --no-browser
```

### **Access**: http://localhost:8123

## 🐳 **Docker Deployment (Production Ready)**

### **Option A: Studio + API**
```bash
./deploy-studio.sh
```

### **Option B: Full stack with Web UI**
```bash
./deploy.sh
```

### **Access**: 
- Studio: http://localhost:8123
- Web UI: http://localhost:8000 (if using full stack)

## ☁️ **Cloud Deployment (Enterprise)**

### **Using Docker Compose**
```bash
# Production deployment
docker-compose -f docker-compose.studio.yml up -d

# Or full stack
docker-compose up -d
```

### **Using Kubernetes**
```yaml
# Example k8s deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: langgraph-studio
spec:
  replicas: 1
  selector:
    matchLabels:
      app: langgraph-studio
  template:
    metadata:
      labels:
        app: langgraph-studio
    spec:
      containers:
      - name: studio
        image: your-registry/langgraph-studio:latest
        ports:
        - containerPort: 8123
        env:
        - name: LANGSMITH_API_KEY
          valueFrom:
            secretKeyRef:
              name: langgraph-secrets
              key: langsmith-api-key
```

## 🎯 **Studio Features Available**

### **Visual Pipeline**
- 🎨 Interactive graph showing your 5-node RAG pipeline
- 🔍 Node details and configuration
- 📊 Data flow visualization
- 🔧 Real-time parameter adjustment

### **Execution Tracing**
- 🔍 Step-by-step query execution
- ⏱️ Timing for each node
- 📝 Input/output for each step
- ❌ Error tracking and debugging

### **Interactive Testing**
- 🧪 Test queries directly in Studio
- 📊 See results in real-time
- 🔄 Compare different queries
- 📈 Performance analysis

### **Monitoring & Analytics**
- 📊 Response time metrics
- 📈 Success/failure rates
- 🔍 Query patterns
- 🎯 Performance bottlenecks

## 🔧 **Troubleshooting Studio Issues**

### **Studio Won't Start**

#### **Issue: Missing LangSmith API Key**
```bash
# Error: "requires env var LANGSMITH_API_KEY"
# Solution: Add to .env file
echo "LANGSMITH_API_KEY=your-key-here" >> .env
```

#### **Issue: Docker Problems**
```bash
# Error: Docker ServerVersion KeyError
# Solution: Use dev mode instead
python -m langgraph_cli dev --port 8123 --no-browser
```

#### **Issue: Port Already in Use**
```bash
# Find and kill process using port 8123
lsof -ti:8123 | xargs kill -9
```

### **Studio Loads But No Graph**

#### **Issue: Graph Not Found**
```bash
# Check langgraph.json configuration
cat config/langgraph.json

# Ensure graph path is correct
ls -la src/agent/graph.py
```

#### **Issue: Import Errors**
```bash
# Test graph import manually
python -c "from src.agent.graph import graph; print('Graph loaded successfully')"
```

### **Studio Loads But Queries Fail**

#### **Issue: No Documents Ingested**
```bash
# Check if documents are loaded
python -m agent.cli stats

# Ingest documents if needed
python -m agent.cli ingest ./docs
# Or ingest from OCI Object Storage (streaming)
python -m agent.cli ingest-oci
# For large batches (100+ PDFs), use concurrent processing
python -m agent.cli ingest-oci-concurrent --max-concurrent=10
```

#### **Issue: API Keys Not Working**
```bash
# Test OpenAI connection
python -c "
import openai
client = openai.OpenAI()
print('OpenAI connection successful')
"
```

## 🎨 **Studio Usage Examples**

### **1. Visual Pipeline Exploration**
1. Open http://localhost:8123
2. Click on your graph
3. Explore each node:
   - `embed_query`: See query embedding generation
   - `retrieve_chunks`: View FAISS search results
   - `combine_context`: See prompt construction
   - `generate_answer`: View LLM response
   - `format_output`: See final formatting

### **2. Interactive Query Testing**
1. Go to the "Playground" tab
2. Enter test queries:
   ```
   "Find contracts for UrbanWear"
   "What are the payment terms?"
   "Show me HealthFirst documents"
   ```
3. Watch real-time execution
4. Analyze results and performance

### **3. Debugging Failed Queries**
1. Run a query that fails
2. Click on the failed execution
3. Step through each node
4. Identify where the failure occurred
5. Check inputs/outputs at each step
6. Fix the issue and test again

### **4. Performance Optimization**
1. Run multiple queries
2. Check the "Analytics" tab
3. Identify slow nodes
4. Adjust configuration:
   - Lower similarity threshold
   - Increase TOP_K
   - Optimize chunk size
5. Test improvements

## 📊 **Studio Integration with CLI**

### **Best Workflow**
```bash
# Terminal 1: Start Studio
./start-studio.sh

# Terminal 2: Use CLI for document management
python -m agent.cli ingest ./docs
# Or for OCI Object Storage (streaming):
python -m agent.cli ingest-oci
# For large batches, use concurrent processing:
python -m agent.cli ingest-oci-concurrent --max-concurrent=5
python -m agent.cli stats

# Browser: Use Studio for query testing and debugging
# Open http://localhost:8123
```

### **Development Cycle**
1. **Ingest documents** via CLI
2. **Test queries** in Studio
3. **Debug issues** visually
4. **Optimize parameters** in Studio
5. **Validate with CLI** for automation

## 🔐 **Security Considerations**

### **API Key Management**
```bash
# Never commit API keys to git
echo ".env" >> .gitignore

# Use environment variables in production
export LANGSMITH_API_KEY=your-key
export OPENAI_API_KEY=your-key
```

### **Network Security**
```bash
# Local development (secure)
python -m langgraph_cli dev --host 127.0.0.1

# Network access (use with caution)
python -m langgraph_cli dev --host 0.0.0.0
```

### **Production Deployment**
- Use secrets management (Kubernetes secrets, Docker secrets)
- Enable HTTPS/TLS
- Set up authentication
- Configure firewall rules

## 🎯 **Studio Deployment Matrix**

| Deployment Type | Command | Studio URL | Best For |
|----------------|---------|------------|----------|
| **Local Dev** | `./start-studio.sh` | http://localhost:8123 | Development, Testing |
| **Docker Local** | `./deploy-studio.sh` | http://localhost:8123 | Production Testing |
| **Docker Compose** | `docker-compose up` | http://localhost:8123 | Multi-service |
| **Cloud/K8s** | Custom deployment | https://your-domain:8123 | Production |

## 🎉 **Success Checklist**

Your Studio setup is successful when:
- ✅ Studio loads at http://localhost:8123
- ✅ You can see the RAG pipeline graph
- ✅ Interactive queries work
- ✅ Execution traces are visible
- ✅ Performance metrics are shown
- ✅ No errors in browser console
- ✅ CLI integration works

## 📞 **Quick Commands Reference**

```bash
# Start Studio (all methods)
./start-studio.sh                    # Recommended
python -m langgraph_cli dev --port 8123           # Manual
./deploy-studio.sh                  # Docker

# Test Studio
curl http://localhost:8123/health   # Health check
open http://localhost:8123          # Open in browser

# Debug Studio
pkill -f langgraph                  # Kill processes
lsof -i :8123                       # Check port usage
docker-compose logs -f              # Docker logs

# CLI Integration
python -m agent.cli stats           # System status
python -m agent.cli query "test"    # Test query
python -m agent.cli ingest ./docs   # Add documents
```

**Now you have LangGraph Studio working across all deployment types!** 🎨✨
