#!/bin/bash

echo "🧪 Running Quick Tests..."

# Check if we're in the backend directory
if [ ! -f "main.py" ]; then
    echo "❌ Please run this script from the backend directory"
    exit 1
fi

# Check if the container is running
if ! docker ps | grep -q "timeoff-manager-api"; then
    echo "❌ Backend container is not running. Please start the services first:"
    echo "   cd .. && ./start.sh"
    exit 1
fi

echo "🐳 Running quick tests inside the Docker container..."

# Install test dependencies if not already installed
docker exec timeoff-manager-api pip install -r requirements-test.txt 2>/dev/null || true

# Run tests without coverage for speed
echo "🔍 Running tests..."
docker exec timeoff-manager-api python -m pytest tests/ -v

echo "✅ Quick tests completed!"
