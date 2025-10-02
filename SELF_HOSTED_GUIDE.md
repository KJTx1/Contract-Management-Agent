# 🏠 Self-Hosted Logistics RAG Assistant

Complete self-hosted solution with both **Control Plane** (LangGraph Studio) and **Data Plane** (RAG API + Web UI).

## 🚀 **Quick Start (5 Minutes)**

### **Prerequisites**
- Docker & Docker Compose installed
- OpenAI API key

### **1. Clone & Setup**
```bash
git clone <your-repo>
cd langraph
```

### **2. Configure Environment**
```bash
# Copy and edit environment file
cp .env.example .env
nano .env  # Add your OPENAI_API_KEY
```

### **3. Deploy Everything**
```bash
./deploy.sh
```

### **4. Access Your System**
- **Web UI**: http://localhost:8000 (Document management & querying)
- **LangGraph Studio**: http://localhost:8123 (Visual debugging & monitoring)

## 🏗️ **Architecture Overview**

```
┌─────────────────────────────────────────────────────────────────┐
│                    SELF-HOSTED SOLUTION                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌──────────────────┐    ┌─────────────┐ │
│  │   Web UI        │    │  LangGraph       │    │   Data      │ │
│  │   (Port 8000)   │───▶│  Studio          │───▶│   Storage   │ │
│  │                 │    │  (Port 8123)     │    │             │ │
│  │ • Upload PDFs   │    │                  │    │ • SQLite    │ │
│  │ • Query Docs    │    │ • Visual Graph   │    │ • FAISS     │ │
│  │ • View Results  │    │ • Debug Traces   │    │ • PDF Files │ │
│  │ • Manage System │    │ • Monitor Perf   │    │             │ │
│  └─────────────────┘    └──────────────────┘    └─────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 🎛️ **Control Plane: LangGraph Studio**

### **Features**
- 🎨 **Visual Graph Editor**: See your RAG pipeline as a flowchart
- 🔍 **Execution Tracing**: Step-by-step debugging of queries
- 📊 **Performance Monitoring**: Response times, success rates
- 🧪 **Interactive Testing**: Test queries directly in the UI
- 📝 **State Inspection**: View data flow between nodes
- 🔧 **Configuration Management**: Adjust parameters visually

### **Access**: http://localhost:8123

### **Usage**
1. Open LangGraph Studio in your browser
2. View the RAG pipeline graph
3. Run test queries and see execution traces
4. Monitor performance metrics
5. Debug issues with detailed logs

## 📊 **Data Plane: Web UI + API**

### **Web Interface Features**
- 📤 **Document Upload**: Drag & drop PDF files
- 🔍 **Smart Search**: Natural language queries
- 📋 **Document Management**: View uploaded documents
- 📈 **System Statistics**: Monitor system health
- 🎯 **Real-time Results**: Instant search results with citations

### **Access**: http://localhost:8000

### **API Endpoints**
- `GET /api/stats` - System statistics
- `GET /api/documents` - List documents
- `POST /api/upload` - Upload PDFs
- `POST /api/query` - Query documents
- `GET /health` - Health check

## 🔧 **Management Commands**

### **Start Services**
```bash
docker-compose up -d
```

### **Stop Services**
```bash
docker-compose down
```

### **View Logs**
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f langgraph-studio
docker-compose logs -f web-ui
```

### **Restart Services**
```bash
docker-compose restart
```

### **Update System**
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 📁 **Data Persistence**

All data is stored in the `./data/` directory:
- `logistics.db` - SQLite database with metadata
- `faiss_index.index` - Vector embeddings
- `pdfs/` - Uploaded PDF files

**Backup**: Simply copy the `./data/` directory

## 🔒 **Security Considerations**

### **Production Deployment**
1. **Change Default Ports**: Modify `docker-compose.yml`
2. **Add Authentication**: Implement user login
3. **Use HTTPS**: Add SSL certificates
4. **Firewall Rules**: Restrict access to necessary IPs
5. **API Rate Limiting**: Prevent abuse

### **Environment Variables**
```bash
# Security
API_KEY_REQUIRED=true
ALLOWED_ORIGINS=https://yourdomain.com

# Performance
MAX_UPLOAD_SIZE=100MB
QUERY_RATE_LIMIT=60/minute
```

## 📈 **Scaling Options**

### **Horizontal Scaling**
```yaml
# docker-compose.yml
services:
  web-ui:
    deploy:
      replicas: 3
  
  nginx:
    image: nginx
    # Load balancer configuration
```

### **Performance Tuning**
```bash
# Environment variables
CHUNK_SIZE=1000          # Larger chunks for better context
TOP_K=10                 # More results
SIMILARITY_THRESHOLD=0.2  # Lower threshold for more results
```

## 🔍 **Monitoring & Observability**

### **Health Checks**
```bash
# Check service health
curl http://localhost:8000/health
curl http://localhost:8123/health
```

### **Metrics Collection**
- Response times
- Query success rates
- Document processing status
- System resource usage

### **Log Analysis**
```bash
# Search logs
docker-compose logs | grep ERROR
docker-compose logs | grep "Query:"
```

## 🛠️ **Troubleshooting**

### **Common Issues**

#### **Services Won't Start**
```bash
# Check Docker status
docker ps
docker-compose ps

# View detailed logs
docker-compose logs
```

#### **Can't Access Web UI**
```bash
# Check if port is available
netstat -tulpn | grep 8000

# Restart services
docker-compose restart web-ui
```

#### **No Search Results**
1. Check if documents are uploaded: http://localhost:8000
2. Verify API key is set correctly
3. Lower similarity threshold in `.env`
4. Check LangGraph Studio for execution traces

#### **Upload Fails**
1. Ensure PDFs are text-based (not scanned images)
2. Check file size limits
3. Verify disk space available
4. Check upload logs in Web UI

### **Debug Mode**
```bash
# Enable debug logging
echo "DEBUG=true" >> .env
docker-compose restart
```

## 🚀 **Advanced Configuration**

### **Custom Models**
```bash
# Use different embedding model
EMBEDDING_MODEL=text-embedding-3-large
EMBEDDING_PROVIDER=cohere

# Use different LLM
LLM_MODEL=gpt-4
```

### **Performance Optimization**
```bash
# Increase processing power
CHUNK_SIZE=1200
MAX_CONCURRENT_UPLOADS=10
FAISS_INDEX_TYPE=IVF  # For large document sets
```

### **Integration**
```bash
# Connect to external databases
DATABASE_URL=postgresql://user:pass@host:5432/db

# Use cloud storage
STORAGE_TYPE=s3
S3_BUCKET=my-documents
```

## 📞 **Support & Maintenance**

### **Regular Maintenance**
1. **Weekly**: Check logs for errors
2. **Monthly**: Backup data directory
3. **Quarterly**: Update Docker images
4. **Annually**: Review security settings

### **Backup Strategy**
```bash
# Backup data
tar -czf backup-$(date +%Y%m%d).tar.gz ./data/

# Restore data
tar -xzf backup-20241201.tar.gz
```

### **Updates**
```bash
# Update to latest version
git pull
docker-compose build --no-cache
docker-compose up -d
```

## 🎯 **Success Metrics**

Your self-hosted system is working well if:
- ✅ Web UI loads in < 2 seconds
- ✅ Document upload completes in < 30 seconds per PDF
- ✅ Queries return results in < 5 seconds
- ✅ LangGraph Studio shows successful execution traces
- ✅ No error messages in logs
- ✅ System handles your expected document volume

## 🎉 **You're All Set!**

Your complete self-hosted RAG solution is now running with:
- 🎨 **Visual Control Plane** (LangGraph Studio)
- 📊 **User-Friendly Data Plane** (Web UI)
- 🔧 **Production-Ready Infrastructure** (Docker)
- 📈 **Monitoring & Debugging** (Built-in)

**Next Steps**: Upload your documents and start querying! 🚀
