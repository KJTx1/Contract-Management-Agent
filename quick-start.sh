#!/bin/bash

# Contract Management Agent - Quick Start Script
# This script provides easy access to common operations

set -e

echo "🤖 Contract Management Agent - Quick Start"
echo "=========================================="

# Function to show help
show_help() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  studio     Start LangGraph Studio"
    echo "  ingest     Ingest documents"
    echo "  query      Query documents"
    echo "  stats      Show system statistics"
    echo "  test       Run unit/integration tests"
    echo "  system     Run system integration test"
    echo "  clean      Clean up data"
    echo "  help       Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 studio                    # Start Studio"
    echo "  $0 ingest my-doc.pdf        # Ingest a document"
    echo "  $0 query 'Tell me about...' # Query documents"
}

# Function to start Studio
start_studio() {
    echo "🎨 Starting LangGraph Studio..."
    ./scripts/start-studio.sh
}

# Function to ingest documents
ingest_docs() {
    if [ -z "$1" ]; then
        echo "❌ Please provide a document path"
        echo "Usage: $0 ingest <document-path>"
        exit 1
    fi
    
    echo "📄 Ingesting document: $1"
    source .venv/bin/activate
    python -m src.agent.cli ingest --source "$1"
}

# Function to query documents
query_docs() {
    if [ -z "$1" ]; then
        echo "❌ Please provide a query"
        echo "Usage: $0 query '<your-query>'"
        exit 1
    fi
    
    echo "🔍 Querying: $1"
    source .venv/bin/activate
    python -m src.agent.cli query "$1"
}

# Function to show stats
show_stats() {
    echo "📊 System Statistics:"
    source .venv/bin/activate
    python -m src.agent.cli stats
}

# Function to run tests
run_tests() {
    echo "🧪 Running tests..."
    source .venv/bin/activate
    python -m pytest tests/ -v
}

# Function to run system integration test
run_system_test() {
    echo "🔍 Running system integration test..."
    source .venv/bin/activate
    python tests/test_system_integration.py
}

# Function to clean data
clean_data() {
    echo "🧹 Cleaning up data..."
    read -p "This will delete all ingested documents. Continue? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -f data/logistics.db data/faiss_index.index
        echo "✅ Data cleaned"
    else
        echo "❌ Cleanup cancelled"
    fi
}

# Main script logic
case "${1:-help}" in
    studio)
        start_studio
        ;;
    ingest)
        ingest_docs "$2"
        ;;
    query)
        query_docs "$2"
        ;;
    stats)
        show_stats
        ;;
    test)
        run_tests
        ;;
    system)
        run_system_test
        ;;
    clean)
        clean_data
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
