#!/bin/bash

echo "📝 Timeoff Manager Logs"
echo "======================"
echo ""
echo "Press Ctrl+C to exit"
echo ""

# Show logs from all services
docker-compose logs -f
