#!/bin/bash

# Logistics RAG Assistant - Self-Hosted Deployment Script
# This script sets up both control plane (LangGraph Studio) and data plane (RAG API)

set -e

echo "🚀 Deploying Logistics RAG Assistant (Self-Hosted)"
echo "=================================================="

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
COHERE_API_KEY=your-cohere-api-key-here

# RAG Configuration
SIMILARITY_THRESHOLD=0.3
TOP_K=5
CHUNK_SIZE=800
CHUNK_OVERLAP=100

# LangSmith (optional - for tracing)
LANGSMITH_API_KEY=your-langsmith-key-here
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

# Build and start services
echo "🔨 Building Docker images..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo "🔍 Checking service health..."

# Check LangGraph Studio
if curl -f http://localhost:8123/health &> /dev/null; then
    echo "✅ LangGraph Studio (Control Plane) is running on http://localhost:8123"
else
    echo "⚠️  LangGraph Studio may still be starting up..."
fi

# Check Web UI
if curl -f http://localhost:8000/health &> /dev/null; then
    echo "✅ Web UI (Data Plane) is running on http://localhost:8000"
else
    echo "⚠️  Web UI may still be starting up..."
fi

echo ""
echo "🎉 Deployment Complete!"
echo "======================"
echo ""
echo "📊 Access Points:"
echo "  • Web UI (Document Management): http://localhost:8000"
echo "  • LangGraph Studio (Control Plane): http://localhost:8123"
echo ""
echo "🔧 Management Commands:"
echo "  • View logs: docker-compose logs -f"
echo "  • Stop services: docker-compose down"
echo "  • Restart services: docker-compose restart"
echo ""
echo "📚 Next Steps:"
echo "  1. Open http://localhost:8000 in your browser"
echo "  2. Upload some PDF documents"
echo "  3. Start querying your documents"
echo "  4. Use http://localhost:8123 for advanced debugging"
echo ""
