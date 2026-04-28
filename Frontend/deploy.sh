#!/bin/bash

# CFO Chatbot Frontend Deployment Script for AWS EC2
# This script automates the deployment process

set -e  # Exit on any error

echo "🚀 Starting CFO Chatbot Frontend Deployment..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
APP_DIR="/var/www/cfo-chatbot"
NGINX_CONF="/etc/nginx/sites-available/cfo-chatbot"
NGINX_ENABLED="/etc/nginx/sites-enabled/cfo-chatbot"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Please run as root (use sudo)${NC}"
    exit 1
fi

echo -e "${YELLOW}📦 Step 1: Installing system dependencies...${NC}"
apt-get update
apt-get install -y nginx curl

# Install Node.js 18.x if not installed
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}📦 Installing Node.js...${NC}"
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
    apt-get install -y nodejs
fi

echo -e "${GREEN}✅ Node.js version: $(node --version)${NC}"
echo -e "${GREEN}✅ npm version: $(npm --version)${NC}"

echo -e "${YELLOW}📁 Step 2: Setting up application directory...${NC}"
mkdir -p $APP_DIR
cp -r . $APP_DIR/
cd $APP_DIR

echo -e "${YELLOW}📦 Step 3: Installing npm dependencies...${NC}"
npm install

echo -e "${YELLOW}🔨 Step 4: Building production bundle...${NC}"
npm run build

echo -e "${YELLOW}⚙️  Step 5: Configuring Nginx...${NC}"
cp nginx.conf $NGINX_CONF

# Enable site if not already enabled
if [ ! -L "$NGINX_ENABLED" ]; then
    ln -s $NGINX_CONF $NGINX_ENABLED
fi

# Remove default nginx site if exists
if [ -L "/etc/nginx/sites-enabled/default" ]; then
    rm /etc/nginx/sites-enabled/default
fi

# Test nginx configuration
nginx -t

echo -e "${YELLOW}🔄 Step 6: Restarting Nginx...${NC}"
systemctl restart nginx
systemctl enable nginx

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo ""
echo -e "${GREEN}🌐 Your application is now running!${NC}"
echo -e "${GREEN}📍 Access it at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo 'YOUR_EC2_IP')${NC}"
echo ""
echo -e "${YELLOW}⚠️  Important: Update .env.production with your backend API URL${NC}"
echo -e "${YELLOW}   Then rebuild: npm run build${NC}"
