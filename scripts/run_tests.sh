#!/bin/bash

# Test runner script for concurrent processing functionality

echo "🧪 Running Unit Tests for Concurrent Processing"
echo "=============================================="

# Set up environment
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Run all tests
echo "📋 Running all tests..."
python -m pytest tests/ -v --tb=short

echo ""
echo "🔍 Running concurrent processing tests specifically..."
python -m pytest tests/unit_tests/test_concurrent_processing.py -v --tb=short

echo ""
echo "🗄️ Running batch operations tests..."
python -m pytest tests/unit_tests/test_batch_operations.py -v --tb=short

echo ""
echo "🖥️ Running CLI concurrent tests..."
python -m pytest tests/unit_tests/test_cli_concurrent.py -v --tb=short

echo ""
echo "📊 Running performance tests..."
python -m pytest tests/ -k "performance" -v --tb=short

echo ""
echo "✅ Test run complete!"
