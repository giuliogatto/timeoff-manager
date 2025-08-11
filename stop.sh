#!/bin/bash

echo "🛑 Stopping Timeoff Manager..."

# Stop all services
docker compose down

echo "✅ All services stopped!"

echo ""
echo "🧹 To remove all data (volumes, networks):"
echo "   docker compose down -v"
echo ""
echo "🚀 To start again:"
echo "   ./start.sh"
echo "   or"
echo "   docker compose up -d"
