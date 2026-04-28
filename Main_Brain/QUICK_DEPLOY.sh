#!/bin/bash

# Quick Deploy Script for AWS EC2
# Run this script on your EC2 instance after cloning the repository

set -e  # Exit on error

echo "🚀 Multi-Agent Chatbot Copilot - Quick Deploy Script"
echo "=================================================="
echo ""

# Check if running on Ubuntu
if [ ! -f /etc/lsb-release ]; then
    echo "❌ This script is designed for Ubuntu. Please install manually."
    exit 1
fi

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
echo "🐍 Installing Python 3.11..."
sudo apt install -y python3.11 python3.11-venv python3-pip build-essential python3.11-dev libpq-dev

# Install Redis
echo "💾 Installing Redis..."
sudo apt install -y redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Install Git
echo "📥 Installing Git..."
sudo apt install -y git

# Install Nginx
echo "🌐 Installing Nginx..."
sudo apt install -y nginx

# Create virtual environment
echo "🔧 Creating virtual environment..."
python3.11 -m venv venv

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install dependencies
echo "📚 Installing Python dependencies (this may take a few minutes)..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env file with your actual credentials:"
    echo "   - DB_USER"
    echo "   - DB_PASSWORD"
    echo "   - LLM_API_KEY"
    echo "   - SECRET_KEY (generate with: python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
    echo ""
    read -p "Press Enter to edit .env file now..."
    nano .env
else
    echo "✅ .env file already exists"
fi

# Test the application
echo ""
echo "🧪 Testing application..."
echo "Starting test server (press Ctrl+C to stop)..."
echo ""
python main.py &
APP_PID=$!

# Wait for server to start
sleep 5

# Test health endpoint
echo ""
echo "Testing health endpoint..."
curl -s http://localhost:8000/health | python3 -m json.tool || echo "❌ Health check failed"

# Stop test server
kill $APP_PID 2>/dev/null || true

echo ""
echo "=================================================="
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Setup systemd service (see AWS_EC2_DEPLOYMENT_GUIDE.md Step 7)"
echo "2. Configure Nginx reverse proxy (see AWS_EC2_DEPLOYMENT_GUIDE.md Step 8)"
echo "3. Setup SSL with Let's Encrypt (optional, see AWS_EC2_DEPLOYMENT_GUIDE.md Step 9)"
echo ""
echo "To start the application manually:"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
echo "For full deployment guide, see: AWS_EC2_DEPLOYMENT_GUIDE.md"
echo "=================================================="
