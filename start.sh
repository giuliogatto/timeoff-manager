#!/bin/bash

echo "🚀 Starting Timeoff Manager..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Create external network if it doesn't exist
if ! docker network ls | grep -q "timeoff_manager_network"; then
    echo "📡 Creating Docker network..."
    docker network create timeoff_manager_network
fi

# Create external volume if it doesn't exist
if ! docker volume ls | grep -q "timeoff_manager_data"; then
    echo "💾 Creating Docker volume..."
    docker volume create timeoff_manager_data
fi

# Start all services
echo "🔧 Starting all services..."
docker-compose up -d

# Wait a moment for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Check service status
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "✅ Timeoff Manager is starting up!"
echo ""
echo "🌐 Access Points:"
echo "   Frontend:     http://localhost:3000"
echo "   Backend API:  http://localhost:8000"
echo "   API Docs:     http://localhost:8000/docs"
echo "   phpMyAdmin:   http://localhost:8080"
echo ""
echo "🔐 Default Admin Login:"
echo "   Email:    admin@example.com"
echo "   Password: password"
echo ""
echo "📝 To view logs: docker-compose logs -f"
echo "🛑 To stop:      docker-compose down"
