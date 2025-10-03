#!/bin/bash

# LangGraph Studio - Local Development Deployment (No Docker)
# Lightweight local testing without containers

set -e

echo "🎨 Starting LangGraph Studio (Local Development)"
echo "==============================================="

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Virtual environment not activated. Activating..."
    source .venv/bin/activate
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating template..."
    cat > .env << EOF
# OpenAI API Key (required)
# OPENAI_API_KEY should be set in .env file

# Optional: Cohere API Key
COHERE_API_KEY=

# RAG Configuration
SIMILARITY_THRESHOLD=0.3
TOP_K=5
CHUNK_SIZE=800
CHUNK_OVERLAP=100

# Optional: LangSmith (for enhanced tracing)
# LANGSMITH_API_KEY should be set in .env file
LANGSMITH_PROJECT=logistics-rag
EOF
    echo "📝 Please edit .env file with your API keys before continuing."
    echo "   nano .env"
    exit 1
fi

# Validate API key is set
if grep -q "your-openai-api-key-here" .env; then
    echo "❌ Please set your OPENAI_API_KEY in .env file"
    exit 1
fi

echo "✅ Environment configuration validated"

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check if required dependencies are installed
echo "🔍 Checking dependencies..."

if ! python -c "import langgraph" 2>/dev/null; then
    echo "❌ LangGraph not found. Installing dependencies..."
    pip install -e .
fi

if ! python -c "import langgraph_cli" 2>/dev/null; then
    echo "❌ LangGraph CLI not found. Installing in virtual environment..."
    pip install 'langgraph-cli[inmem]'
fi

echo "✅ Dependencies verified"

# Create data directory if it doesn't exist
mkdir -p data

# Check if documents are ingested
DOC_COUNT=$(python -c "
import sys
sys.path.insert(0, 'src')
try:
    from agent.database import Database
    db = Database()
    stats = db.get_stats()
    print(stats['total_documents'])
except:
    print('0')
" 2>/dev/null)

# Remove any non-numeric characters and default to 0 if empty
DOC_COUNT=$(echo "$DOC_COUNT" | grep -o '[0-9]*' | head -1)
DOC_COUNT=${DOC_COUNT:-0}

if [ "$DOC_COUNT" -eq "0" ]; then
    echo "📄 No documents found. Would you like to ingest sample documents? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "📤 Ingesting documents from ./docs..."
        python -m agent.cli ingest ./docs
        echo "✅ Documents ingested successfully"
    fi
fi

echo ""
echo "🚀 Starting LangGraph Studio..."
echo "================================"
echo ""
echo "🎨 LangGraph Studio will be available at: http://localhost:8123"
echo "📊 You can also use CLI commands in another terminal:"
echo "   python -m agent.cli query 'your question'"
echo "   python -m agent.cli stats"
echo "   python -m agent.cli list"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start LangGraph Studio in development mode (no Docker required)
echo "🎨 Starting LangGraph Studio..."
echo "If Studio doesn't start, you may need a LangSmith API key."
echo "Get one from: https://smith.langchain.com/"
echo ""

# Try different startup methods using local CLI
if python -m langgraph_cli dev --port 8123 --host 127.0.0.1 --no-browser; then
    echo "✅ Studio started successfully"
else
    echo "⚠️  Studio startup failed. Trying alternative method..."
    python -m langgraph_cli up --port 8123 --no-pull || {
        echo "❌ Studio startup failed. Please check:"
        echo "   1. LangSmith API key is set in .env"
        echo "   2. Docker is running (for 'up' command)"
        echo "   3. Port 8123 is available"
        echo ""
        echo "🔧 Manual startup:"
        echo "   ./start-studio.sh"
    }
fi
