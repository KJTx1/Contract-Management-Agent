#!/bin/bash

# Test script for local LangGraph Studio deployment

echo "🧪 Testing Local LangGraph Studio Deployment"
echo "============================================"

# Wait a moment for the server to start
sleep 5

# Test if LangGraph Studio is running
echo "🔍 Testing LangGraph Studio connection..."
if curl -s http://localhost:8123/health &> /dev/null; then
    echo "✅ LangGraph Studio is running on http://localhost:8123"
else
    echo "⚠️  LangGraph Studio may still be starting up..."
fi

# Test CLI functionality
echo ""
echo "🔍 Testing CLI functionality..."

# Activate virtual environment
source .venv/bin/activate

# Test stats
echo "📊 System Statistics:"
python -m agent.cli stats

echo ""
echo "📄 Recent Documents:"
python -m agent.cli list | head -10

echo ""
echo "🔍 Testing a sample query..."
python -m agent.cli query "What are the payment terms?" | head -20

echo ""
echo "🎉 Local deployment test complete!"
echo ""
echo "🎨 Access LangGraph Studio: http://localhost:8123"
echo "📊 Use CLI commands: python -m agent.cli [command]"
echo ""
