#!/bin/bash

# LangGraph Studio - Lightweight Self-Hosted Deployment
# Single-service deployment for operational efficiency

set -e

echo "🎨 Deploying LangGraph Studio (Lightweight)"
echo "============================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
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
LANGSMITH_API_KEY=
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

# Build and start LangGraph Studio
echo "🔨 Building LangGraph Studio..."
docker-compose -f docker-compose.studio.yml build

echo "🚀 Starting LangGraph Studio..."
docker-compose -f docker-compose.studio.yml up -d

# Wait for service to be ready
echo "⏳ Waiting for LangGraph Studio to start..."
sleep 15

# Check service health
echo "🔍 Checking service health..."
if curl -f http://localhost:8123/ok &> /dev/null; then
    echo "✅ LangGraph Studio is running successfully!"
else
    echo "⚠️  LangGraph Studio may still be starting up..."
    echo "   Check logs: docker-compose -f docker-compose.studio.yml logs -f"
fi

echo ""
echo "🎉 Deployment Complete!"
echo "======================"
echo ""
echo "🎨 LangGraph Studio: http://localhost:8123"
echo ""
echo "📊 Features Available:"
echo "  • Visual RAG pipeline editor"
echo "  • Real-time execution tracing"
echo "  • Interactive query testing"
echo "  • Performance monitoring"
echo "  • Debug capabilities"
echo ""
echo "🔧 Management Commands:"
echo "  • View logs: docker-compose -f docker-compose.studio.yml logs -f"
echo "  • Stop service: docker-compose -f docker-compose.studio.yml down"
echo "  • Restart service: docker-compose -f docker-compose.studio.yml restart"
echo ""
echo "📚 Next Steps:"
echo "  1. Open http://localhost:8123 in your browser"
echo "  2. Use the CLI to ingest documents: python -m agent.cli ingest ./docs"
echo "  3. Test queries in LangGraph Studio interface"
echo "  4. Monitor execution traces and performance"
echo ""
