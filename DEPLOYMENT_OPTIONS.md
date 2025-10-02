# 🚀 Complete Deployment Options with LangGraph Studio

**All deployment types now include LangGraph Studio for visual RAG pipeline management**

## 🎯 **Quick Reference**

| Deployment Type | Command | Studio URL | Best For |
|----------------|---------|------------|----------|
| **Local Development** | `./start-studio.sh` | http://localhost:8123 | Development, Testing |
| **Local with CLI** | `./deploy-local.sh` | http://localhost:8123 | Quick Testing |
| **Docker Studio Only** | `./deploy-studio.sh` | http://localhost:8123 | Production Studio |
| **Full Docker Stack** | `./deploy.sh` | http://localhost:8123 | Complete Solution |
| **Test All Types** | `./test-studio-all.sh` | - | Validation |

## 🏠 **Local Development (Recommended)**

### **Quick Start**
```bash
# 1. Ensure LangSmith API key is in .env
echo "LANGSMITH_API_KEY=your-key-here" >> .env

# 2. Start Studio
./start-studio.sh

# 3. Access Studio
open http://localhost:8123
```

### **Features**
- ✅ **Fastest startup** (no Docker)
- ✅ **Hot reloading** for development
- ✅ **Native debugging** capabilities
- ✅ **Direct file access** for editing
- ✅ **CLI integration** for document management

### **Perfect For**
- 🧪 Testing new features
- 🐛 Debugging issues
- 🔧 Configuration tuning
- 📚 Learning the system

## 🐳 **Docker Deployments**

### **Studio-Only Docker**
```bash
# Lightweight Docker deployment with just Studio
./deploy-studio.sh
```

**Features:**
- ✅ **Containerized** environment
- ✅ **Production-ready** setup
- ✅ **Easy scaling** and management
- ✅ **Isolated** dependencies

### **Full Docker Stack**
```bash
# Complete solution with Studio + Web UI
./deploy.sh
```

**Features:**
- ✅ **LangGraph Studio** on port 8123
- ✅ **Web UI** on port 8000 (document management)
- ✅ **Multi-service** architecture
- ✅ **Production deployment** ready

## 🎨 **LangGraph Studio Features (All Deployments)**

### **Visual Pipeline**
- 🎨 **Interactive Graph**: See your 5-node RAG pipeline
- 🔍 **Node Details**: Inspect each component
- 📊 **Data Flow**: Understand information flow
- 🔧 **Live Configuration**: Adjust parameters in real-time

### **Execution Tracing**
- 🔍 **Step-by-step Debugging**: Watch queries execute
- ⏱️ **Performance Timing**: See bottlenecks
- 📝 **Input/Output Inspection**: Debug data transformations
- ❌ **Error Tracking**: Identify and fix issues

### **Interactive Testing**
- 🧪 **Query Playground**: Test queries directly
- 📊 **Real-time Results**: See immediate responses
- 🔄 **Query Comparison**: Test different approaches
- 📈 **Performance Analysis**: Optimize your system

### **Monitoring & Analytics**
- 📊 **Response Metrics**: Track performance over time
- 📈 **Success Rates**: Monitor system health
- 🔍 **Query Patterns**: Understand usage
- 🎯 **Bottleneck Identification**: Find optimization opportunities

## 🔧 **Configuration Requirements**

### **Required Environment Variables**
```bash
# In .env file
OPENAI_API_KEY=your-openai-key-here
LANGSMITH_API_KEY=your-langsmith-key-here
LANGSMITH_PROJECT=logistics-rag
LANGCHAIN_TRACING_V2=true
```

### **Optional Configuration**
```bash
# RAG tuning
SIMILARITY_THRESHOLD=0.3
TOP_K=5
CHUNK_SIZE=800
CHUNK_OVERLAP=100

# Studio customization
LANGSMITH_PROJECT=your-project-name
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
```

## 🎯 **Deployment Decision Matrix**

### **Choose Local Development When:**
- 🧪 You're developing or testing
- 🐛 You need to debug issues
- 🔧 You want to modify code
- 📚 You're learning the system
- ⚡ You want fastest startup

### **Choose Docker Studio When:**
- 🏭 You need production environment
- 🔒 You want isolated deployment
- 📈 You plan to scale
- 👥 Multiple users will access
- 🌐 You need network deployment

### **Choose Full Docker Stack When:**
- 🎨 You want both Studio and Web UI
- 👥 You have non-technical users
- 📤 You need document upload interface
- 📊 You want comprehensive monitoring
- 🏢 You're deploying for a team

## 🚀 **Getting Started Workflow**

### **Step 1: Setup**
```bash
# Get your API keys
# OpenAI: https://platform.openai.com/api-keys
# LangSmith: https://smith.langchain.com/

# Add to .env file
echo "OPENAI_API_KEY=your-openai-key" >> .env
echo "LANGSMITH_API_KEY=your-langsmith-key" >> .env
```

### **Step 2: Choose Deployment**
```bash
# For development
./start-studio.sh

# For production testing
./deploy-studio.sh

# For full solution
./deploy.sh
```

### **Step 3: Validate**
```bash
# Test all deployment types
./test-studio-all.sh

# Or test specific deployment
curl http://localhost:8123/health
```

### **Step 4: Use Studio**
1. Open http://localhost:8123
2. Explore the RAG pipeline graph
3. Test queries in the playground
4. Monitor execution traces
5. Optimize performance

## 📊 **Studio Usage Examples**

### **Development Workflow**
```bash
# Terminal 1: Start Studio
./start-studio.sh

# Terminal 2: Manage documents
python -m agent.cli ingest ./docs
python -m agent.cli stats

# Browser: Test and debug in Studio
# http://localhost:8123
```

### **Production Workflow**
```bash
# Deploy with Docker
./deploy-studio.sh

# Monitor via Studio
open http://localhost:8123

# Manage via CLI or API
python -m agent.cli query "production query"
```

## 🔍 **Troubleshooting**

### **Studio Won't Start**
```bash
# Check API keys
grep LANGSMITH_API_KEY .env
grep OPENAI_API_KEY .env

# Check port availability
lsof -i :8123

# Kill existing processes
pkill -f langgraph
```

### **Studio Loads But No Graph**
```bash
# Verify graph configuration
cat langgraph.json

# Test graph import
python -c "from src.agent.graph import graph; print('OK')"
```

### **Queries Fail in Studio**
```bash
# Check documents are ingested
python -m agent.cli stats

# Test CLI query
python -m agent.cli query "test"

# Check API connectivity
python -c "import openai; print('OpenAI OK')"
```

## 🎉 **Success Indicators**

Your Studio deployment is successful when:
- ✅ Studio loads at http://localhost:8123
- ✅ RAG pipeline graph is visible
- ✅ Interactive queries work
- ✅ Execution traces appear
- ✅ Performance metrics are shown
- ✅ CLI integration works
- ✅ No errors in browser console

## 📞 **Quick Commands**

```bash
# Start Studio (choose one)
./start-studio.sh          # Local development
./deploy-studio.sh         # Docker studio-only
./deploy.sh                # Full Docker stack

# Test Studio
curl http://localhost:8123/health
open http://localhost:8123

# Manage System
python -m agent.cli stats
python -m agent.cli query "test"
python -m agent.cli ingest ./docs

# Debug Issues
pkill -f langgraph         # Kill processes
docker-compose logs -f     # View Docker logs
./test-studio-all.sh       # Test all deployments
```

## 🎯 **Summary**

**You now have LangGraph Studio available across ALL deployment types:**

1. **✅ Local Development**: `./start-studio.sh` - Fast, flexible, perfect for development
2. **✅ Docker Studio**: `./deploy-studio.sh` - Production-ready, containerized
3. **✅ Full Stack**: `./deploy.sh` - Complete solution with Web UI
4. **✅ Testing**: `./test-studio-all.sh` - Validate all deployments

**Every deployment includes:**
- 🎨 **Visual RAG Pipeline** editor
- 🔍 **Real-time Execution** tracing
- 🧪 **Interactive Query** testing
- 📊 **Performance Monitoring**
- 🔧 **Debug Capabilities**

**Your RAG system is now complete with visual management across all deployment scenarios!** 🎉✨
