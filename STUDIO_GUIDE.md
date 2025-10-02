# 🎨 LangGraph Studio - Lightweight Self-Hosted RAG

**Operationally efficient, single-service deployment for visual RAG pipeline management.**

## 🚀 **Quick Deploy (2 Minutes)**

### **Prerequisites**
- Docker & Docker Compose
- OpenAI API key

### **1. Setup**
```bash
# Clone and configure
git clone <your-repo>
cd langraph

# Set your API key
echo "OPENAI_API_KEY=your-key-here" > .env
```

### **2. Deploy**
```bash
./deploy-studio.sh
```

### **3. Access**
**LangGraph Studio**: http://localhost:8123

## 🏗️ **Architecture (Lightweight)**

```
┌─────────────────────────────────────────────────────────────────┐
│                    LIGHTWEIGHT SOLUTION                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  User Browser                                                   │
│       │                                                         │
│       ├──> LangGraph Studio (Port 8123)                       │
│       │    ├─ Visual Pipeline Editor                           │
│       │    ├─ Real-time Execution Tracing                     │
│       │    ├─ Interactive Query Testing                       │
│       │    ├─ Performance Monitoring                          │
│       │    └─ Debug & Troubleshooting                         │
│       │                                                         │
│       └──> CLI (Document Management)                           │
│            ├─ python -m agent.cli ingest ./docs               │
│            ├─ python -m agent.cli query "question"            │
│            └─ python -m agent.cli stats                       │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                RAG Pipeline                             │   │
│  │  Embed → Retrieve → Combine → Generate → Format        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Data Storage                               │   │
│  │  SQLite + FAISS + PDF Files (./data/)                  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 🎯 **What You Get**

### **LangGraph Studio Features**
- 🎨 **Visual Pipeline**: See your RAG flow as an interactive graph
- 🔍 **Execution Tracing**: Step-by-step debugging of each query
- 📊 **Performance Metrics**: Response times, success rates, bottlenecks
- 🧪 **Interactive Testing**: Test queries directly in the interface
- 📝 **State Inspection**: View data flowing between nodes
- 🔧 **Live Configuration**: Adjust parameters without redeployment
- 📈 **Monitoring Dashboard**: System health and usage analytics

### **CLI Integration**
- 📤 **Document Ingestion**: `python -m agent.cli ingest ./docs`
- 🔍 **Query Testing**: `python -m agent.cli query "your question"`
- 📊 **System Stats**: `python -m agent.cli stats`
- 📋 **Document Listing**: `python -m agent.cli list`

## 🔧 **Operational Efficiency**

### **Single Service Deployment**
- ✅ **Minimal Resources**: One container, lightweight footprint
- ✅ **Simple Management**: Single service to monitor
- ✅ **Fast Startup**: < 30 seconds to full operation
- ✅ **Easy Updates**: Single container rebuild
- ✅ **Clear Logs**: Focused logging from one service

### **Resource Requirements**
```yaml
Minimum:
  CPU: 1 core
  RAM: 2GB
  Disk: 5GB

Recommended:
  CPU: 2 cores
  RAM: 4GB
  Disk: 20GB
```

### **Management Commands**
```bash
# Deploy
./deploy-studio.sh

# Monitor
docker-compose -f docker-compose.studio.yml logs -f

# Stop
docker-compose -f docker-compose.studio.yml down

# Restart
docker-compose -f docker-compose.studio.yml restart

# Update
docker-compose -f docker-compose.studio.yml build --no-cache
docker-compose -f docker-compose.studio.yml up -d
```

## 📊 **Using LangGraph Studio**

### **1. Access the Interface**
Open http://localhost:8123 in your browser

### **2. View Your RAG Pipeline**
- See the 5-node graph: Embed → Retrieve → Combine → Generate → Format
- Understand data flow between components
- Identify bottlenecks visually

### **3. Test Queries Interactively**
- Enter test queries in the Studio interface
- Watch real-time execution traces
- See exactly what happens at each step
- Debug issues immediately

### **4. Monitor Performance**
- View response times for each node
- Track success/failure rates
- Identify slow components
- Monitor system health

### **5. Debug Issues**
- Step through failed executions
- Inspect intermediate states
- View error messages in context
- Test fixes immediately

## 🔍 **Typical Workflow**

### **Initial Setup**
```bash
# 1. Deploy Studio
./deploy-studio.sh

# 2. Ingest documents
python -m agent.cli ingest ./docs

# 3. Verify in Studio
# Open http://localhost:8123
# Check that documents are processed
```

### **Daily Operations**
```bash
# Monitor system
docker-compose -f docker-compose.studio.yml ps

# Check logs
docker-compose -f docker-compose.studio.yml logs --tail=100

# Add new documents
python -m agent.cli ingest /path/to/new/docs

# Test queries in Studio UI
```

### **Troubleshooting**
```bash
# View detailed logs
docker-compose -f docker-compose.studio.yml logs -f

# Check system stats
python -m agent.cli stats

# Test CLI queries
python -m agent.cli query "test question"

# Restart if needed
docker-compose -f docker-compose.studio.yml restart
```

## 📈 **Performance Optimization**

### **Configuration Tuning**
```bash
# In .env file
SIMILARITY_THRESHOLD=0.3    # Lower = more results
TOP_K=5                     # Number of results
CHUNK_SIZE=800             # Larger = more context
CHUNK_OVERLAP=100          # Overlap between chunks
```

### **Scaling Considerations**
- **Documents**: Up to 1000 PDFs efficiently
- **Concurrent Users**: 5-10 simultaneous users
- **Query Volume**: 100+ queries per hour
- **Storage**: Linear growth with document count

### **When to Scale Up**
- Response times > 10 seconds
- Memory usage > 80%
- Frequent timeouts
- User complaints about slowness

## 🔒 **Security & Production**

### **Basic Security**
```bash
# Change default port
# In docker-compose.studio.yml:
ports:
  - "9000:8123"  # Use port 9000 instead

# Add firewall rules
sudo ufw allow 9000/tcp
sudo ufw deny 8123/tcp
```

### **Production Checklist**
- [ ] Change default ports
- [ ] Set up SSL/TLS
- [ ] Configure firewall rules
- [ ] Set up log rotation
- [ ] Configure backup strategy
- [ ] Monitor disk usage
- [ ] Set up alerting

## 📊 **Monitoring & Alerts**

### **Health Checks**
```bash
# Service health
curl http://localhost:8123/ok

# System stats via CLI
python -m agent.cli stats

# Docker health
docker-compose -f docker-compose.studio.yml ps
```

### **Log Monitoring**
```bash
# Error monitoring
docker-compose -f docker-compose.studio.yml logs | grep ERROR

# Performance monitoring
docker-compose -f docker-compose.studio.yml logs | grep "Query:"

# System monitoring
docker stats langgraph_langgraph-studio_1
```

## 🛠️ **Maintenance**

### **Regular Tasks**
- **Daily**: Check logs for errors
- **Weekly**: Monitor disk usage
- **Monthly**: Update Docker images
- **Quarterly**: Review performance metrics

### **Backup Strategy**
```bash
# Backup data directory
tar -czf backup-$(date +%Y%m%d).tar.gz ./data/

# Restore from backup
tar -xzf backup-20241201.tar.gz
```

### **Updates**
```bash
# Update system
git pull
docker-compose -f docker-compose.studio.yml build --no-cache
docker-compose -f docker-compose.studio.yml up -d
```

## 🎯 **Success Metrics**

Your deployment is successful when:
- ✅ Studio loads in < 3 seconds
- ✅ Queries complete in < 5 seconds
- ✅ No errors in logs
- ✅ Visual graph displays correctly
- ✅ Execution traces are clear
- ✅ System handles expected load

## 🎉 **Benefits of This Approach**

### **Operational Efficiency**
- **Single Service**: Easy to manage and monitor
- **Lightweight**: Minimal resource requirements
- **Fast Deployment**: 2-minute setup
- **Clear Debugging**: Visual troubleshooting
- **Production Ready**: Docker-based, scalable

### **Developer Experience**
- **Visual Debugging**: See exactly what's happening
- **Interactive Testing**: Test queries in real-time
- **Performance Insights**: Identify bottlenecks quickly
- **Easy Configuration**: Adjust parameters visually
- **Comprehensive Monitoring**: Full system visibility

### **User Experience**
- **Reliable**: Single point of failure, easy to fix
- **Fast**: Optimized for performance
- **Transparent**: Clear execution traces
- **Debuggable**: Issues are easy to identify and fix

## 🚀 **Get Started Now**

```bash
# 1. Set API key
echo "OPENAI_API_KEY=your-key" > .env

# 2. Deploy
./deploy-studio.sh

# 3. Access Studio
open http://localhost:8123

# 4. Ingest documents
python -m agent.cli ingest ./docs

# 5. Start querying!
```

**Your lightweight, operationally efficient RAG system is ready!** 🎨✨
