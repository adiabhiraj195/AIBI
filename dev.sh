#!/bin/bash

# ============================================================
# AIBI Developer Helper Script
# Common tasks for local development
# Usage: ./dev.sh [command]
# ============================================================

case "$1" in
  # Start services
  start)
    echo "🚀 Starting all services..."
    docker compose up --build
    ;;
  
  # Stop services
  stop)
    echo "⏹️  Stopping all services..."
    docker compose down
    ;;
  
  # View logs
  logs)
    SERVICE="${2:-}"
    if [ -n "$SERVICE" ]; then
      docker compose logs -f "$SERVICE"
    else
      docker compose logs -f
    fi
    ;;
  
  # Access service shell
  shell)
    SERVICE="${2:-backend-brain}"
    echo "Accessing $SERVICE shell..."
    docker compose exec "$SERVICE" /bin/bash
    ;;
  
  # Access database
  db)
    echo "Connecting to PostgreSQL database..."
    docker compose exec database psql -U AIBI_user -d AIBI_Backend
    ;;
  
  # Access Redis
  redis)
    echo "Accessing Redis CLI..."
    docker compose exec redis redis-cli
    ;;
  
  # Database stats
  db-stats)
    echo "Database Statistics:"
    docker compose exec database psql -U AIBI_user -d AIBI_Backend \
      -c "SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size FROM pg_tables ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"
    ;;
  
  # Test APIs
  test-api)
    echo "Testing API endpoints..."
    echo ""
    echo "Main Brain API:"
    curl -s http://localhost:8000/docs > /dev/null && echo "✅ http://localhost:8000/docs" || echo "❌ http://localhost:8000/docs"
    echo ""
    echo "CSV API:"
    curl -s http://localhost:8001/docs > /dev/null && echo "✅ http://localhost:8001/docs" || echo "❌ http://localhost:8001/docs"
    echo ""
    echo "Frontend:"
    curl -s http://localhost:3000 > /dev/null && echo "✅ http://localhost:3000" || echo "❌ http://localhost:3000"
    ;;
  
  # Check service status
  status)
    echo "Service Status:"
    echo ""
    docker compose ps
    ;;
  
  # Reset everything
  reset)
    echo "🔄 Resetting all services and data..."
    docker compose down -v
    echo "✅ All services stopped and volumes removed"
    echo ""
    echo "Run './dev.sh start' to start fresh"
    ;;
  
  # View Docker resource usage
  stats)
    docker stats --no-stream
    ;;
  
  # Build images only (no start)
  build)
    echo "🔨 Building Docker images..."
    docker compose build
    ;;
  
  # Clean up unused Docker resources
  clean)
    echo "🧹 Cleaning up Docker resources..."
    docker system prune --volumes -f
    echo "✅ Cleanup complete"
    ;;
  
  # Help
  help|'')
    cat << 'EOF'
AIBI Developer Helper

Usage: ./dev.sh [command] [options]

Commands:
  start            Start all services (docker compose up --build)
  stop             Stop all services
  logs [SERVICE]   View logs (optional: specify service name)
  shell [SERVICE]  Access service shell (default: backend-brain)
  db               Connect to PostgreSQL database
  redis            Access Redis CLI
  db-stats         Show database table sizes
  test-api         Test all API endpoints
  status           Show service status
  reset            Remove all services and data (docker compose down -v)
  stats            Show Docker resource usage
  build            Build Docker images only
  clean            Clean up unused Docker resources
  help             Show this help message

Examples:
  ./dev.sh start              # Start everything
  ./dev.sh logs backend-brain # View Main Brain logs
  ./dev.sh shell backend-csv  # Access CSV API shell
  ./dev.sh db                 # Connect to database
  ./dev.sh reset              # Start from scratch

EOF
    ;;
  
  *)
    echo "❌ Unknown command: $1"
    echo ""
    echo "Use './dev.sh help' for available commands"
    exit 1
    ;;
esac
