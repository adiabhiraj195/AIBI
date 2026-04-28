#!/bin/bash

# ============================================================
# Suzlon Multi-Service Docker Startup Script
# Quick start for all services with helpful diagnostics
# ============================================================

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$PROJECT_DIR/.env"
ENV_EXAMPLE="$PROJECT_DIR/.env.example"

echo "🚀 Suzlon Multi-Service Setup"
echo "=============================="
echo ""

# Check if Docker is running
echo "📋 Checking Docker..."
if ! docker ps &>/dev/null; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi
echo "✅ Docker is running"
echo ""

# Check if .env exists
if [ ! -f "$ENV_FILE" ]; then
    echo "⚠️  .env file not found."
    echo "Creating .env from .env.example..."
    if [ -f "$ENV_EXAMPLE" ]; then
        cp "$ENV_EXAMPLE" "$ENV_FILE"
        echo "✅ .env created. Please review and update with your credentials."
        echo "📝 File: $ENV_FILE"
        echo ""
        echo "Required variables to set:"
        echo "  - DB_PASSWORD (PostgreSQL password)"
        echo "  - LLM_API_KEY (for Main Brain)"
        echo "  - GROQ_API_KEY (for CSV processing)"
        echo ""
        echo "After updating .env, run this script again."
        exit 0
    else
        echo "❌ .env.example not found"
        exit 1
    fi
fi

echo "✅ .env file found"
echo ""

# Parse .env for important variables
DB_PASSWORD=$(grep -E "^DB_PASSWORD=" "$ENV_FILE" | cut -d= -f2 | tr -d '\r')
LLM_API_KEY=$(grep -E "^LLM_API_KEY=" "$ENV_FILE" | cut -d= -f2 | tr -d '\r')
GROQ_API_KEY=$(grep -E "^GROQ_API_KEY=" "$ENV_FILE" | cut -d= -f2 | tr -d '\r')

# Validate critical configuration
MISSING_VARS=()

if [ -z "$DB_PASSWORD" ] || [ "$DB_PASSWORD" = "suzlon_password_change_me_in_production" ]; then
    MISSING_VARS+=("DB_PASSWORD")
fi

if [ -z "$LLM_API_KEY" ] || [ "$LLM_API_KEY" = "your_llm_api_key_here" ]; then
    MISSING_VARS+=("LLM_API_KEY")
fi

if [ -z "$GROQ_API_KEY" ] || [ "$GROQ_API_KEY" = "your_groq_api_key_here" ]; then
    MISSING_VARS+=("GROQ_API_KEY")
fi

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    echo "⚠️  Critical environment variables are not configured:"
    for var in "${MISSING_VARS[@]}"; do
        echo "  - $var"
    done
    echo ""
    echo "📝 Please update $ENV_FILE with real values"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi

echo ""
echo "🐳 Starting Docker Compose..."
echo "=============================="
echo ""
echo "Services starting:"
echo "  📦 PostgreSQL Database  → port 5432"
echo "  🔴 Redis              → port 6379"
echo "  🧠 Main Brain API     → port 8000"
echo "  📄 CSV API            → port 8001"
echo "  🎨 Frontend           → port 3000"
echo ""
echo "Building images and starting services..."
echo ""

# Start services
cd "$PROJECT_DIR"
docker compose up --build

# This won't execute unless compose fails
exit 1
