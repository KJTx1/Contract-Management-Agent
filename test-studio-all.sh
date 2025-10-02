#!/bin/bash

# Test LangGraph Studio across all deployment types

echo "🧪 Testing LangGraph Studio - All Deployment Types"
echo "=================================================="

# Function to test Studio accessibility
test_studio() {
    local deployment_type=$1
    local url=${2:-"http://localhost:8123"}
    
    echo "🔍 Testing $deployment_type deployment..."
    
    # Wait for startup
    sleep 10
    
    # Test different endpoints
    if curl -s -f "$url/health" &> /dev/null; then
        echo "✅ $deployment_type: Health endpoint working"
    elif curl -s -f "$url/ok" &> /dev/null; then
        echo "✅ $deployment_type: OK endpoint working"
    elif curl -s -f "$url/" | grep -q "LangGraph" &> /dev/null; then
        echo "✅ $deployment_type: Studio UI loading"
    else
        echo "❌ $deployment_type: Studio not accessible"
        return 1
    fi
    
    return 0
}

# Function to cleanup processes
cleanup() {
    echo "🧹 Cleaning up processes..."
    pkill -f "langgraph" 2>/dev/null || true
    docker-compose down 2>/dev/null || true
    docker-compose -f docker-compose.studio.yml down 2>/dev/null || true
    sleep 3
}

# Test 1: Local Development
echo ""
echo "🏠 Test 1: Local Development"
echo "============================"

cleanup

if [ -f .venv/bin/activate ]; then
    source .venv/bin/activate
    export $(cat .env | grep -v '^#' | xargs)
    
    echo "Starting local Studio..."
    ./start-studio.sh &
    STUDIO_PID=$!
    
    if test_studio "Local Development"; then
        echo "✅ Local development test passed"
        LOCAL_SUCCESS=true
    else
        echo "❌ Local development test failed"
        LOCAL_SUCCESS=false
    fi
    
    kill $STUDIO_PID 2>/dev/null || true
else
    echo "⚠️  Virtual environment not found, skipping local test"
    LOCAL_SUCCESS=false
fi

# Test 2: Docker Studio-Only
echo ""
echo "🐳 Test 2: Docker Studio-Only"
echo "=============================="

cleanup

if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    echo "Building Docker image..."
    docker-compose -f docker-compose.studio.yml build --quiet
    
    echo "Starting Docker Studio..."
    docker-compose -f docker-compose.studio.yml up -d
    
    if test_studio "Docker Studio-Only"; then
        echo "✅ Docker studio-only test passed"
        DOCKER_STUDIO_SUCCESS=true
    else
        echo "❌ Docker studio-only test failed"
        DOCKER_STUDIO_SUCCESS=false
    fi
    
    docker-compose -f docker-compose.studio.yml down
else
    echo "⚠️  Docker not available, skipping Docker tests"
    DOCKER_STUDIO_SUCCESS=false
fi

# Test 3: Full Docker Stack
echo ""
echo "🐳 Test 3: Full Docker Stack"
echo "============================"

cleanup

if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    echo "Building full stack..."
    docker-compose build --quiet
    
    echo "Starting full stack..."
    docker-compose up -d
    
    if test_studio "Full Docker Stack"; then
        echo "✅ Full Docker stack test passed"
        DOCKER_FULL_SUCCESS=true
    else
        echo "❌ Full Docker stack test failed"
        DOCKER_FULL_SUCCESS=false
    fi
    
    # Also test web UI if available
    if curl -s -f "http://localhost:8000/health" &> /dev/null; then
        echo "✅ Web UI also working on port 8000"
    fi
    
    docker-compose down
else
    echo "⚠️  Docker not available, skipping full stack test"
    DOCKER_FULL_SUCCESS=false
fi

# Test 4: CLI Integration
echo ""
echo "📊 Test 4: CLI Integration"
echo "=========================="

if [ -f .venv/bin/activate ]; then
    source .venv/bin/activate
    
    echo "Testing CLI functionality..."
    
    # Test stats
    if python -m agent.cli stats &> /dev/null; then
        echo "✅ CLI stats working"
        CLI_SUCCESS=true
    else
        echo "❌ CLI stats failed"
        CLI_SUCCESS=false
    fi
    
    # Test query
    if python -m agent.cli query "test query" &> /dev/null; then
        echo "✅ CLI query working"
    else
        echo "❌ CLI query failed"
        CLI_SUCCESS=false
    fi
else
    echo "⚠️  Virtual environment not found, skipping CLI test"
    CLI_SUCCESS=false
fi

# Final cleanup
cleanup

# Summary
echo ""
echo "📊 Test Summary"
echo "==============="
echo ""

if [ "$LOCAL_SUCCESS" = true ]; then
    echo "✅ Local Development: PASSED"
else
    echo "❌ Local Development: FAILED"
fi

if [ "$DOCKER_STUDIO_SUCCESS" = true ]; then
    echo "✅ Docker Studio-Only: PASSED"
else
    echo "❌ Docker Studio-Only: FAILED"
fi

if [ "$DOCKER_FULL_SUCCESS" = true ]; then
    echo "✅ Full Docker Stack: PASSED"
else
    echo "❌ Full Docker Stack: FAILED"
fi

if [ "$CLI_SUCCESS" = true ]; then
    echo "✅ CLI Integration: PASSED"
else
    echo "❌ CLI Integration: FAILED"
fi

echo ""

# Overall result
TOTAL_TESTS=4
PASSED_TESTS=0

[ "$LOCAL_SUCCESS" = true ] && ((PASSED_TESTS++))
[ "$DOCKER_STUDIO_SUCCESS" = true ] && ((PASSED_TESTS++))
[ "$DOCKER_FULL_SUCCESS" = true ] && ((PASSED_TESTS++))
[ "$CLI_SUCCESS" = true ] && ((PASSED_TESTS++))

echo "🎯 Overall Result: $PASSED_TESTS/$TOTAL_TESTS tests passed"

if [ $PASSED_TESTS -eq $TOTAL_TESTS ]; then
    echo "🎉 All tests passed! LangGraph Studio is working across all deployment types."
elif [ $PASSED_TESTS -gt 0 ]; then
    echo "⚠️  Some tests passed. Check the setup guide for failed deployments."
else
    echo "❌ All tests failed. Please check your configuration:"
    echo "   1. Ensure LANGSMITH_API_KEY is set in .env"
    echo "   2. Ensure OPENAI_API_KEY is set in .env"
    echo "   3. Check Docker is running (for Docker tests)"
    echo "   4. Verify port 8123 is available"
fi

echo ""
echo "📚 Next Steps:"
echo "   • Use ./start-studio.sh for local development"
echo "   • Use ./deploy-studio.sh for Docker deployment"
echo "   • Access Studio at http://localhost:8123"
echo "   • Check STUDIO_SETUP_GUIDE.md for detailed instructions"
echo ""
