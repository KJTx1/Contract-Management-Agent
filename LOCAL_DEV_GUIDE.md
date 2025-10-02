# 🏠 Local Development Guide - No Docker Required

**Quick local testing of LangGraph Studio without containers.**

## 🚀 **Quick Start (1 Minute)**

```bash
# 1. Ensure your API key is set in .env
echo "OPENAI_API_KEY=your-key-here" > .env

# 2. Deploy locally
./deploy-local.sh

# 3. Access Studio
open http://localhost:8123
```

## 🎯 **What This Gives You**

### **LangGraph Studio (Development Mode)**
- 🎨 **Visual Pipeline Editor**: Interactive graph interface
- 🔍 **Real-time Debugging**: Step-by-step execution traces
- 🧪 **Interactive Testing**: Test queries directly in Studio
- 📊 **Performance Monitoring**: Response times and metrics
- 🔧 **Hot Reloading**: Automatic updates when code changes

### **CLI Integration**
- 📤 **Document Management**: `python -m agent.cli ingest ./docs`
- 🔍 **Query Testing**: `python -m agent.cli query "question"`
- 📊 **System Stats**: `python -m agent.cli stats`
- 📋 **Document Listing**: `python -m agent.cli list`

## 🔧 **Local Development Benefits**

### **No Docker Required**
- ✅ **Faster Startup**: No container building
- ✅ **Direct Debugging**: Native Python debugging
- ✅ **Hot Reloading**: Instant code changes
- ✅ **Resource Efficient**: No container overhead
- ✅ **Simple Setup**: Just Python virtual environment

### **Development Features**
- 🔄 **Auto-reload**: Changes reflected immediately
- 🐛 **Native Debugging**: Use your favorite Python debugger
- 📝 **Live Logs**: Direct console output
- 🔧 **Easy Configuration**: Edit files directly

## 📁 **Project Structure**

```
langraph/
├── deploy-local.sh          # Local deployment script
├── test-local.sh           # Test script
├── .env                    # Environment variables
├── data/                   # Local data storage
│   ├── logistics.db        # SQLite database
│   ├── faiss_index.index   # Vector index
│   └── pdfs/              # Stored documents
├── docs/                   # Sample documents
└── src/agent/             # RAG pipeline code
```

## 🎮 **Usage Examples**

### **Start Development Server**
```bash
./deploy-local.sh
```

### **Test Everything**
```bash
./test-local.sh
```

### **Manual CLI Testing**
```bash
# Activate environment
source .venv/bin/activate

# Ingest documents
python -m agent.cli ingest ./docs

# Query documents
python -m agent.cli query "Find contracts for UrbanWear"

# Check system stats
python -m agent.cli stats

# List documents
python -m agent.cli list
```

### **Access Studio**
- Open http://localhost:8123
- View the RAG pipeline graph
- Test queries interactively
- Debug execution traces
- Monitor performance

## 🔍 **Development Workflow**

### **1. Start Development**
```bash
./deploy-local.sh
```

### **2. Make Code Changes**
- Edit files in `src/agent/`
- Changes are automatically reloaded
- No need to restart server

### **3. Test Changes**
- Use LangGraph Studio for visual testing
- Use CLI for automated testing
- Check logs in terminal

### **4. Debug Issues**
- View execution traces in Studio
- Check terminal logs
- Use Python debugger if needed

## 🛠️ **Troubleshooting**

### **Server Won't Start**
```bash
# Check if port is in use
lsof -i :8123

# Kill existing process
pkill -f "langgraph"

# Restart
./deploy-local.sh
```

### **No Documents Found**
```bash
# Check if documents exist
ls -la docs/

# Ingest manually
python -m agent.cli ingest ./docs

# Verify ingestion
python -m agent.cli stats
```

### **Query Returns No Results**
```bash
# Check similarity threshold
grep SIMILARITY_THRESHOLD .env

# Lower threshold for more results
echo "SIMILARITY_THRESHOLD=0.2" >> .env

# Restart server
pkill -f "langgraph"
./deploy-local.sh
```

### **Studio Not Loading**
```bash
# Check if server is running
curl http://localhost:8123/health

# Check logs in terminal
# Look for any error messages

# Try different browser or incognito mode
```

## 📊 **Performance Tips**

### **Faster Development**
- Use `--no-browser` flag to skip auto-opening browser
- Use `--no-reload` flag to disable hot reloading if not needed
- Keep document set small during development

### **Memory Optimization**
- Limit document ingestion during testing
- Use smaller chunk sizes for faster processing
- Monitor memory usage with `htop` or Activity Monitor

## 🔧 **Configuration Options**

### **Environment Variables**
```bash
# In .env file
OPENAI_API_KEY=your-key-here
SIMILARITY_THRESHOLD=0.3
TOP_K=5
CHUNK_SIZE=800
CHUNK_OVERLAP=100

# Development specific
DEBUG=true
LOG_LEVEL=DEBUG
```

### **LangGraph Dev Options**
```bash
# Custom port
python -m langgraph_cli dev --port 9000

# Enable debugging
python -m langgraph_cli dev --debug-port 5678

# Disable auto-reload
python -m langgraph_cli dev --no-reload

# Custom host (for network access)
python -m langgraph_cli dev --host 0.0.0.0
```

## 🎯 **When to Use Local Development**

### **Perfect For:**
- 🧪 **Testing new features**
- 🐛 **Debugging issues**
- 🔧 **Configuration tuning**
- 📚 **Learning the system**
- 🚀 **Rapid prototyping**

### **Not Ideal For:**
- 🏭 **Production deployment**
- 👥 **Multi-user testing**
- 📈 **Performance benchmarking**
- 🔒 **Security testing**
- 🌐 **Network deployment**

## 🚀 **Next Steps**

### **After Local Testing**
1. **Validate functionality** with your documents
2. **Tune configuration** for your use case
3. **Test different queries** and scenarios
4. **Move to Docker deployment** for production
5. **Deploy to cloud** for team access

### **Production Deployment**
```bash
# When ready for production
./deploy-studio.sh  # Docker-based deployment
```

## 📝 **Development Notes**

- **Hot Reloading**: Code changes are automatically detected
- **Debug Mode**: Full Python debugging available
- **Live Logs**: See all output in terminal
- **Fast Iteration**: No container rebuilding needed
- **Native Performance**: No virtualization overhead

## 🎉 **You're Ready!**

Your local development environment is now set up for:
- ✅ **Visual RAG pipeline development**
- ✅ **Interactive query testing**
- ✅ **Real-time debugging**
- ✅ **Performance monitoring**
- ✅ **Rapid iteration**

**Happy developing!** 🎨🚀
