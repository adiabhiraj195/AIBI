# AWS EC2 Deployment Guide - Multi-Agent Chatbot Copilot

Complete step-by-step guide to deploy this backend on AWS EC2.

## 📋 Prerequisites

- AWS Account with EC2 access
- SSH key pair for EC2 instance
- Domain name (optional, for production)

## 🚀 Quick Deployment Steps

### Step 1: Launch EC2 Instance

1. **Login to AWS Console** → Navigate to EC2 Dashboard

2. **Launch Instance**:
   - Click "Launch Instance"
   - **Name**: `multi-agent-chatbot-backend`
   - **AMI**: Ubuntu Server 22.04 LTS (Free tier eligible)
   - **Instance Type**: `t3.medium` (recommended) or `t2.medium` (minimum)
     - 2 vCPUs, 4 GB RAM minimum for ML models
   - **Key Pair**: Create new or select existing SSH key
   - **Network Settings**:
     - Allow SSH (port 22) from your IP
     - Allow HTTP (port 80) from anywhere (0.0.0.0/0)
     - Allow HTTPS (port 443) from anywhere (0.0.0.0/0)
     - Allow Custom TCP (port 8000) from anywhere (0.0.0.0/0)
   - **Storage**: 30 GB gp3 (minimum for dependencies)
   - Click "Launch Instance"

3. **Note your instance details**:
   - Public IPv4 address (e.g., `54.123.45.67`)
   - Public IPv4 DNS (e.g., `ec2-54-123-45-67.compute-1.amazonaws.com`)

### Step 2: Connect to EC2 Instance

```bash
# Make your key file secure
chmod 400 your-key.pem

# Connect via SSH
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

### Step 3: Install System Dependencies

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python 3.11 and pip
sudo apt install -y python3.11 python3.11-venv python3-pip

# Install Redis (for conversation memory)
sudo apt install -y redis-server

# Start and enable Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Install Git
sudo apt install -y git

# Install build essentials (required for some Python packages)
sudo apt install -y build-essential python3.11-dev libpq-dev

# Install nginx (optional, for reverse proxy)
sudo apt install -y nginx
```

### Step 4: Clone and Setup Application

```bash
# Clone your repository
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -r requirements.txt
```

### Step 5: Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit environment file
nano .env
```

**Update these critical values in `.env`**:

```bash
# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false
ENVIRONMENT=production

# Database Configuration (Your existing PostgreSQL)
DB_HOST=23.22.202.15
DB_PORT=5432
DB_NAME=postgres
DB_USER=your_actual_username
DB_PASSWORD=your_actual_password
DB_SSL_MODE=require

# Redis Configuration (Local on EC2)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# LLM Configuration
LLM_MODEL=meta-llama/llama-3.3-70b-instruct:free
LLM_API_KEY=your_actual_api_key
LLM_BASE_URL=https://openrouter.ai/api/v1

# Security
SECRET_KEY=generate_a_secure_random_key_here

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

**Generate a secure SECRET_KEY**:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Save and exit (Ctrl+X, then Y, then Enter)

### Step 6: Test the Application

```bash
# Activate virtual environment if not already active
source venv/bin/activate

# Test run the application
python main.py
```

You should see:
```
🚀 Starting Multi-Agent Chatbot Copilot...
✅ Application startup complete
🌟 Starting server on 0.0.0.0:8000
```

**Test from your local machine**:
```bash
curl http://YOUR_EC2_PUBLIC_IP:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "multi-agent-chatbot-copilot",
  "version": "1.0.0"
}
```

Press `Ctrl+C` to stop the test server.

### Step 7: Setup Production Server with Systemd

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/chatbot-backend.service
```

Add this configuration:

```ini
[Unit]
Description=Multi-Agent Chatbot Copilot Backend
After=network.target redis-server.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/YOUR_REPO
Environment="PATH=/home/ubuntu/YOUR_REPO/venv/bin"
ExecStart=/home/ubuntu/YOUR_REPO/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Replace `YOUR_REPO` with your actual repository folder name.**

Save and exit (Ctrl+X, then Y, then Enter)

Enable and start the service:

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable chatbot-backend

# Start the service
sudo systemctl start chatbot-backend

# Check status
sudo systemctl status chatbot-backend
```

### Step 8: Setup Nginx Reverse Proxy (Optional but Recommended)

```bash
# Create nginx configuration
sudo nano /etc/nginx/sites-available/chatbot-backend
```

Add this configuration:

```nginx
server {
    listen 80;
    server_name YOUR_EC2_PUBLIC_IP;  # Or your domain name

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeout settings for long-running queries
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
    }
}
```

Enable the site:

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/chatbot-backend /etc/nginx/sites-enabled/

# Test nginx configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

Now your API is accessible at:
- Direct: `http://YOUR_EC2_PUBLIC_IP:8000`
- Via Nginx: `http://YOUR_EC2_PUBLIC_IP`

### Step 9: Setup SSL with Let's Encrypt (Optional, for HTTPS)

**Only if you have a domain name:**

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is configured automatically
```

## 🔍 Monitoring and Maintenance

### View Application Logs

```bash
# View real-time logs
sudo journalctl -u chatbot-backend -f

# View last 100 lines
sudo journalctl -u chatbot-backend -n 100

# View logs from today
sudo journalctl -u chatbot-backend --since today
```

### Restart Application

```bash
sudo systemctl restart chatbot-backend
```

### Stop Application

```bash
sudo systemctl stop chatbot-backend
```

### Update Application

```bash
# SSH into EC2
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP

# Navigate to repo
cd YOUR_REPO

# Pull latest changes
git pull

# Activate virtual environment
source venv/bin/activate

# Update dependencies if needed
pip install -r requirements.txt

# Restart service
sudo systemctl restart chatbot-backend
```

## 🧪 Testing Your Deployment

### Test Health Endpoint

```bash
curl http://YOUR_EC2_PUBLIC_IP/health
```

### Test System Status

```bash
curl http://YOUR_EC2_PUBLIC_IP/api/system/status
```

### Test Query Endpoint

```bash
curl -X POST http://YOUR_EC2_PUBLIC_IP/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is our total portfolio capacity?",
    "session_id": "test-session-123",
    "user_id": "test-user"
  }'
```

## 🔒 Security Best Practices

### 1. Secure Your EC2 Instance

```bash
# Update security group to restrict SSH access to your IP only
# In AWS Console: EC2 → Security Groups → Edit inbound rules
# SSH (22): Your IP only
# HTTP (80): 0.0.0.0/0
# HTTPS (443): 0.0.0.0/0
# Custom TCP (8000): 0.0.0.0/0 (or restrict if using nginx)
```

### 2. Setup Firewall (UFW)

```bash
# Enable UFW
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp
sudo ufw enable
```

### 3. Secure Redis

```bash
# Edit Redis config
sudo nano /etc/redis/redis.conf

# Add password (uncomment and set):
# requirepass your_strong_password_here

# Bind to localhost only:
# bind 127.0.0.1

# Restart Redis
sudo systemctl restart redis-server
```

Update `.env` with Redis password:
```bash
REDIS_PASSWORD=your_strong_password_here
```

### 4. Regular Updates

```bash
# Setup automatic security updates
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

## 📊 Resource Requirements

### Minimum Configuration
- **Instance Type**: t2.medium
- **vCPUs**: 2
- **RAM**: 4 GB
- **Storage**: 30 GB
- **Cost**: ~$30-40/month

### Recommended Configuration
- **Instance Type**: t3.medium
- **vCPUs**: 2
- **RAM**: 4 GB
- **Storage**: 50 GB
- **Cost**: ~$35-45/month

### Production Configuration
- **Instance Type**: t3.large
- **vCPUs**: 2
- **RAM**: 8 GB
- **Storage**: 100 GB
- **Cost**: ~$60-75/month

## 🐛 Troubleshooting

### Application Won't Start

```bash
# Check logs
sudo journalctl -u chatbot-backend -n 50

# Check if port is in use
sudo lsof -i :8000

# Check environment variables
cat .env

# Test manually
source venv/bin/activate
python main.py
```

### Database Connection Issues

```bash
# Test database connectivity
telnet 23.22.202.15 5432

# Check environment variables
grep DB_ .env

# Test from Python
python3 -c "import psycopg2; conn = psycopg2.connect(host='23.22.202.15', port=5432, dbname='postgres', user='YOUR_USER', password='YOUR_PASS'); print('Connected!')"
```

### Redis Connection Issues

```bash
# Check Redis status
sudo systemctl status redis-server

# Test Redis connection
redis-cli ping

# Check Redis logs
sudo journalctl -u redis-server -n 50
```

### Out of Memory

```bash
# Check memory usage
free -h

# Check swap
sudo swapon --show

# Add swap if needed (4GB)
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

## 🌐 Frontend Integration

Your frontend should connect to:
- **Development**: `http://YOUR_EC2_PUBLIC_IP:8000`
- **Production with Nginx**: `http://YOUR_EC2_PUBLIC_IP`
- **Production with SSL**: `https://your-domain.com`

Update your frontend `.env`:
```bash
VITE_API_BASE_URL=http://YOUR_EC2_PUBLIC_IP:8000
# or
VITE_API_BASE_URL=https://your-domain.com
```

## 📝 Quick Reference Commands

```bash
# Start service
sudo systemctl start chatbot-backend

# Stop service
sudo systemctl stop chatbot-backend

# Restart service
sudo systemctl restart chatbot-backend

# View logs
sudo journalctl -u chatbot-backend -f

# Check status
sudo systemctl status chatbot-backend

# Update code
cd YOUR_REPO && git pull && sudo systemctl restart chatbot-backend
```

## ✅ Deployment Checklist

- [ ] EC2 instance launched with correct security groups
- [ ] SSH access configured
- [ ] System dependencies installed (Python, Redis, Git)
- [ ] Repository cloned
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] `.env` file configured with production values
- [ ] Application tested manually
- [ ] Systemd service created and enabled
- [ ] Nginx reverse proxy configured (optional)
- [ ] SSL certificate installed (optional)
- [ ] Firewall configured
- [ ] Redis secured
- [ ] Health endpoint accessible
- [ ] Query endpoint tested
- [ ] Frontend connected and tested

---

**Your backend is now deployed and ready for production use!** 🚀

For support or issues, check the logs first:
```bash
sudo journalctl -u chatbot-backend -f
```
