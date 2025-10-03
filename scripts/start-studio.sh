#!/bin/bash

# LangGraph Studio Startup Script
# Works for all deployment types: local, Docker, production

set -e

echo "🎨 Starting LangGraph Studio"
echo "============================"

# Check if virtual environment is activated (for local deployment)
if [[ "$VIRTUAL_ENV" == "" ]] && [[ -d ".venv" ]]; then
    echo "⚡ Activating virtual environment..."
    source .venv/bin/activate
fi

# Load environment variables
if [ -f .env ]; then
    echo "📝 Loading environment variables..."
    export $(cat .env | grep -v '^#' | grep -v '^$' | xargs)
else
    echo "⚠️  No .env file found. Creating template..."
    cat > .env << EOF
# OpenAI API Key (required)
OPENAI_API_KEY=your-openai-api-key-here

# LangSmith (required for LangGraph Studio)
LANGSMITH_API_KEY=your-langsmith-api-key-here
LANGSMITH_PROJECT=logistics-rag
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com

# RAG Configuration
SIMILARITY_THRESHOLD=0.3
TOP_K=5
CHUNK_SIZE=800
CHUNK_OVERLAP=100
EOF
    echo "📝 Please edit .env file with your API keys"
    exit 1
fi

# Validate required keys
if [[ "$OPENAI_API_KEY" == "your-openai-api-key-here" ]] || [[ -z "$OPENAI_API_KEY" ]]; then
    echo "❌ Please set OPENAI_API_KEY in .env file"
    exit 1
fi

if [[ "$LANGSMITH_API_KEY" == "your-langsmith-api-key-here" ]] || [[ -z "$LANGSMITH_API_KEY" ]]; then
    echo "❌ Please set LANGSMITH_API_KEY in .env file for LangGraph Studio"
    echo "   Get your key from: https://smith.langchain.com/"
    exit 1
fi

echo "✅ API keys validated"

# Check if langgraph CLI is available in virtual environment
if ! python -c "import langgraph_cli" 2>/dev/null; then
    echo "📦 Installing LangGraph CLI in virtual environment..."
    pip install 'langgraph-cli[inmem]'
fi

# Kill any existing LangGraph processes
pkill -f "langgraph" 2>/dev/null || true
sleep 2

# Create data directory
mkdir -p data

# Check port availability
if lsof -Pi :8123 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 8123 is in use. Trying to free it..."
    lsof -ti:8123 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

echo ""
echo "🚀 Starting LangGraph Studio..."
echo "==============================="
echo ""
echo "🎨 Studio will be available at: http://localhost:8123"
echo "📊 Features available:"
echo "   • Visual RAG pipeline graph"
echo "   • Real-time execution tracing"
echo "   • Interactive query testing"
echo "   • Performance monitoring"
echo "   • Debug capabilities"
echo ""
echo "📋 You can also use CLI in another terminal:"
echo "   python -m agent.cli query 'your question'"
echo "   python -m agent.cli stats"
echo "   python -m agent.cli ingest ./docs"
echo ""
echo "Press Ctrl+C to stop Studio"
echo ""

# Start LangGraph Studio with proper configuration using local CLI
exec python -m langgraph_cli dev \
    --port 8123 \
    --host 127.0.0.1 \
    --no-browser \
    --config config/langgraph.json
