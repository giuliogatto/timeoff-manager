#!/bin/bash

echo "🧪 Running Timeoff Manager Backend Tests..."

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

echo "🐳 Running tests inside the Docker container..."

# Install test dependencies in the container
echo "📦 Installing test dependencies..."
docker exec timeoff-manager-api pip install -r requirements-test.txt

# Run tests with coverage in the container
echo "🔍 Running tests with coverage..."
docker exec timeoff-manager-api python -m pytest tests/ -v --cov=. --cov-report=term-missing --cov-report=html

# Copy coverage report to host if needed
echo "📊 Copying coverage report to host..."
docker cp timeoff-manager-api:/app/htmlcov ./htmlcov

echo ""
echo "📊 Test coverage report generated in htmlcov/index.html"
echo "✅ Tests completed!"
